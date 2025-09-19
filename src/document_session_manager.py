#!/usr/bin/env python3
"""
Document Session Manager for Squirt 1.2
Manages LibreOffice document sessions to prevent system slowdown

Rules:
1. Close documents before opening new ones (unless specific reason to keep open)
2. Maximum 4 documents open simultaneously during validation/processing
3. Priority-based document retention with smart preemption
4. Smart document grouping for comparative and multi-phase workflows
5. Context-aware auto-closure (time limits for machine-only, no limits for human processes)
"""

import subprocess
import time
import os
import signal
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import psutil


class SessionPriority(Enum):
    """Priority levels for document sessions"""
    CRITICAL_VALIDATION = 1    # Template cross-validation (highest)
    ACTIVE_CLIENT_WORK = 2     # Current client deliverables
    COMPARATIVE_ANALYSIS = 3   # Template comparison and pricing
    BATCH_PROCESSING = 4       # Automated generation workflows
    BACKGROUND_TASKS = 5       # Screenshots, conversions, cleanup (lowest)


class SessionContext(Enum):
    """Context types for determining closure behavior"""
    HUMAN_VALIDATION = "human_validation"           # Human-in-the-loop, no time limits
    COLLABORATIVE = "collaborative"                 # Claude-human collaboration, no time limits
    AUTOMATED = "automated"                         # Machine-only, time limits apply
    BACKGROUND = "background"                       # Background tasks, aggressive time limits


@dataclass
class DocumentSession:
    """Represents an active document session with priority and context"""
    file_path: str
    process_id: int
    session_type: str  # 'gui', 'headless', 'validation'
    opened_at: datetime
    last_activity: datetime
    priority: SessionPriority = SessionPriority.BATCH_PROCESSING
    context: SessionContext = SessionContext.AUTOMATED
    group_id: Optional[str] = None  # For related documents
    keep_alive_reason: Optional[str] = None
    related_sessions: Set[str] = field(default_factory=set)
    auto_close_exempt: bool = False


class DocumentSessionManager:
    """
    Centralized manager for all LibreOffice document operations in Squirt
    Enforces enhanced document handling rules with priority and context awareness
    """
    
    def __init__(self, max_concurrent_docs: int = 4):
        self.max_concurrent_docs = max_concurrent_docs
        self.active_sessions: Dict[str, DocumentSession] = {}
        self.session_history: List[Dict] = []
        self.document_groups: Dict[str, Set[str]] = {}  # group_id -> session_ids
        
        # Time limits for automated contexts (in minutes)
        self.auto_close_timeouts = {
            SessionContext.AUTOMATED: 10,
            SessionContext.BACKGROUND: 5,
            SessionContext.HUMAN_VALIDATION: None,  # No time limit
            SessionContext.COLLABORATIVE: None      # No time limit
        }
        
    def get_active_session_count(self) -> int:
        """Get number of currently active document sessions"""
        self._cleanup_dead_sessions()
        return len(self.active_sessions)
    
    def _cleanup_dead_sessions(self):
        """Remove sessions for processes that no longer exist"""
        dead_sessions = []
        
        # Also cleanup expired automated sessions based on context
        self._cleanup_expired_sessions()
        for session_id, session in self.active_sessions.items():
            if not self._is_process_alive(session.process_id):
                dead_sessions.append(session_id)
        
        for session_id in dead_sessions:
            self._log_session_end(session_id, "process_died")
            del self.active_sessions[session_id]
    
    def _cleanup_expired_sessions(self):
        """Clean up sessions that have exceeded their context-based timeout"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            timeout_minutes = self.auto_close_timeouts.get(session.context)
            
            # Skip sessions with no time limits (human/collaborative)
            if timeout_minutes is None or session.auto_close_exempt:
                continue
                
            # Check if session has expired
            time_since_activity = current_time - session.last_activity
            if time_since_activity > timedelta(minutes=timeout_minutes):
                expired_sessions.append(session_id)
                print(f"⏰ Session expired: {Path(session.file_path).name} ({session.context.value}, {timeout_minutes}min limit)")
        
        # Close expired sessions
        for session_id in expired_sessions:
            session = self.active_sessions[session_id]
            self.close_document(session.file_path, f"expired_{session.context.value}")
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            return psutil.pid_exists(pid)
        except:
            return False
    
    def _get_libreoffice_processes(self) -> List[int]:
        """Find all running LibreOffice processes"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'soffice' in proc.info['name'].lower():
                    processes.append(proc.info['pid'])
                elif proc.info['cmdline'] and any('libreoffice' in str(arg).lower() for arg in proc.info['cmdline']):
                    processes.append(proc.info['pid'])
        except:
            pass
        return processes
    
    def close_document(self, file_path: str, reason: str = "manual_close") -> bool:
        """Close a specific document session"""
        session_id = self._get_session_id(file_path)
        
        if session_id not in self.active_sessions:
            return True  # Already closed
        
        session = self.active_sessions[session_id]
        
        try:
            # Try graceful shutdown first
            if self._is_process_alive(session.process_id):
                os.kill(session.process_id, signal.SIGTERM)
                time.sleep(2)
                
                # Force kill if still alive
                if self._is_process_alive(session.process_id):
                    os.kill(session.process_id, signal.SIGKILL)
                    time.sleep(1)
            
            self._log_session_end(session_id, reason)
            del self.active_sessions[session_id]
            return True
            
        except Exception as e:
            print(f"⚠️ Error closing document {file_path}: {e}")
            return False
    
    def close_lowest_priority_document(self, requesting_priority: SessionPriority) -> bool:
        """Close the lowest priority document to make room for higher priority request"""
        if not self.active_sessions:
            return True
        
        # Find sessions that can be closed (not human-involved or exempt)
        closeable_sessions = [
            (sid, session) for sid, session in self.active_sessions.items()
            if (session.context in [SessionContext.AUTOMATED, SessionContext.BACKGROUND] 
                and not session.auto_close_exempt
                and session.priority.value > requesting_priority.value)
        ]
        
        if not closeable_sessions:
            # Fallback to oldest non-exempt session
            closeable_sessions = [
                (sid, session) for sid, session in self.active_sessions.items()
                if not session.auto_close_exempt
            ]
        
        if not closeable_sessions:
            print("⚠️ No closeable sessions found (all are human-involved or exempt)")
            return False
        
        # Close lowest priority (highest priority value) session
        session_id, session = max(closeable_sessions, key=lambda x: x[1].priority.value)
        
        print(f"🔄 Closing lower priority document: {Path(session.file_path).name} (P{session.priority.value})")
        return self.close_document(session.file_path, "priority_preemption")
    
    def close_oldest_document(self) -> bool:
        """Close the oldest active document to make room for new one (fallback method)"""
        if not self.active_sessions:
            return True
        
        # Find oldest non-exempt session
        eligible_sessions = {
            sid: session for sid, session in self.active_sessions.items()
            if not session.auto_close_exempt
        }
        
        if not eligible_sessions:
            print("⚠️ No eligible sessions for closure (all are exempt)")
            return False
        
        oldest_session_id = min(
            eligible_sessions.keys(),
            key=lambda x: eligible_sessions[x].opened_at
        )
        
        oldest_session = eligible_sessions[oldest_session_id]
        print(f"🔄 Closing oldest document: {Path(oldest_session.file_path).name}")
        
        return self.close_document(oldest_session.file_path, "auto_close_oldest")
    
    def close_all_documents(self, reason: str = "shutdown") -> bool:
        """Close all active document sessions"""
        print(f"🛑 Closing all {len(self.active_sessions)} active document sessions...")
        
        success = True
        for session_id in list(self.active_sessions.keys()):
            session = self.active_sessions[session_id]
            if not self.close_document(session.file_path, reason):
                success = False
        
        return success
    
    def _enforce_document_limit(self, priority: SessionPriority, context: SessionContext) -> bool:
        """Ensure we don't exceed maximum concurrent documents using priority-based eviction"""
        current_count = self.get_active_session_count()
        
        if current_count >= self.max_concurrent_docs:
            print(f"⚠️ Document limit reached ({current_count}/{self.max_concurrent_docs})")
            
            # Try to close lower priority documents first
            if not self.close_lowest_priority_document(priority):
                # Fallback to oldest document if no lower priority sessions
                if not self.close_oldest_document():
                    print("❌ Could not make room for new document")
                    return False
        
        return True
    
    def create_document_group(self, group_id: str, session_ids: List[str], 
                             group_purpose: str = "comparison") -> bool:
        """Create a group of related documents that should be managed together"""
        if group_id in self.document_groups:
            print(f"⚠️ Document group '{group_id}' already exists")
            return False
        
        # Verify all sessions exist
        valid_session_ids = set()
        for session_id in session_ids:
            if session_id in self.active_sessions:
                valid_session_ids.add(session_id)
                # Update session to reference the group
                self.active_sessions[session_id].group_id = group_id
                self.active_sessions[session_id].related_sessions.update(valid_session_ids - {session_id})
            else:
                print(f"⚠️ Session {session_id} not found for group '{group_id}'")
        
        if valid_session_ids:
            self.document_groups[group_id] = valid_session_ids
            print(f"✅ Created document group '{group_id}' with {len(valid_session_ids)} documents ({group_purpose})")
            return True
        
        return False
    
    def close_document_group(self, group_id: str, reason: str = "group_close") -> bool:
        """Close all documents in a group"""
        if group_id not in self.document_groups:
            print(f"⚠️ Document group '{group_id}' not found")
            return False
        
        session_ids = list(self.document_groups[group_id])
        success_count = 0
        
        print(f"📋 Closing document group '{group_id}' ({len(session_ids)} documents)")
        
        for session_id in session_ids:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if self.close_document(session.file_path, f"{reason}_group"):
                    success_count += 1
        
        # Clean up the group
        del self.document_groups[group_id]
        
        print(f"✅ Closed {success_count}/{len(session_ids)} documents from group '{group_id}'")
        return success_count == len(session_ids)
    
    def get_related_sessions(self, session_id: str) -> Set[str]:
        """Get all sessions related to a given session (including group members)"""
        if session_id not in self.active_sessions:
            return set()
        
        session = self.active_sessions[session_id]
        related = set(session.related_sessions)
        
        # Add group members if session is part of a group
        if session.group_id and session.group_id in self.document_groups:
            related.update(self.document_groups[session.group_id])
            related.discard(session_id)  # Don't include self
        
        return related
    
    def open_document_gui(self, file_path: str, document_type: str = "document", 
                         priority: SessionPriority = SessionPriority.COMPARATIVE_ANALYSIS,
                         context: SessionContext = SessionContext.HUMAN_VALIDATION,
                         group_id: Optional[str] = None,
                         keep_alive_reason: Optional[str] = None) -> bool:
        """
        Open document in LibreOffice GUI for human validation
        Respects both rules: closes previous if needed, enforces 4-doc limit
        """
        if not os.path.exists(file_path):
            print(f"❌ Document not found: {file_path}")
            return False
        
        # Rule 2 & 3: Enforce document limit with priority consideration
        if not self._enforce_document_limit(priority, context):
            return False
        
        # Rule 1 & 4: Close previous GUI sessions unless they're related/grouped
        self._close_previous_gui_sessions(file_path, group_id)
        
        print(f"📄 Opening {document_type} for validation: {Path(file_path).name}")
        
        try:
            # Try different LibreOffice opening methods
            commands = [
                ['libreoffice', file_path],
                ['libreoffice', '--writer', file_path],
                ['soffice', file_path]
            ]
            
            for cmd in commands:
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        env=dict(os.environ, DISPLAY=':0')
                    )
                    
                    # Give it time to start
                    time.sleep(3)
                    
                    # Verify it's running
                    if process.poll() is None:  # Still running
                        session_id = self._get_session_id(file_path)
                        session = DocumentSession(
                            file_path=file_path,
                            process_id=process.pid,
                            session_type="gui",
                            opened_at=datetime.now(),
                            last_activity=datetime.now(),
                            priority=priority,
                            context=context,
                            group_id=group_id,
                            keep_alive_reason=keep_alive_reason,
                            auto_close_exempt=(context in [SessionContext.HUMAN_VALIDATION, SessionContext.COLLABORATIVE])
                        )
                        
                        self.active_sessions[session_id] = session
                        self._log_session_start(session)
                        
                        print(f"✅ Document opened in GUI: {' '.join(cmd)}")
                        print(f"👁️ Please validate the {document_type}")
                        return True
                        
                except Exception:
                    continue
            
            print("❌ All LibreOffice GUI opening methods failed")
            return False
            
        except Exception as e:
            print(f"❌ Error opening document in GUI: {e}")
            return False
    
    def convert_document_headless(self, input_path: str, output_format: str, output_dir: str,
                                 priority: SessionPriority = SessionPriority.BATCH_PROCESSING,
                                 context: SessionContext = SessionContext.AUTOMATED) -> bool:
        """
        Convert document using headless LibreOffice
        Uses sequential processing to avoid overwhelming system
        """
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return False
        
        # For headless conversion, we typically don't need to enforce the limit as strictly
        # But we should still be reasonable
        if self.get_active_session_count() >= self.max_concurrent_docs * 2:  # More lenient for headless
            print(f"⚠️ Too many active processes, waiting...")
            time.sleep(5)
        
        try:
            cmd = [
                'libreoffice', '--headless', '--convert-to', output_format,
                '--outdir', output_dir,
                input_path
            ]
            
            print(f"🔄 Converting: {Path(input_path).name} → {output_format}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0:
                print(f"✅ Conversion successful")
                return True
            else:
                print(f"❌ Conversion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Conversion timeout")
            return False
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return False
    
    def _close_previous_gui_sessions(self, new_file_path: str, new_group_id: Optional[str] = None):
        """Close previous GUI sessions unless they're related or in same group"""
        sessions_to_close = []
        
        for sid, session in self.active_sessions.items():
            if (session.session_type == "gui" and 
                session.file_path != new_file_path and
                not session.auto_close_exempt):
                
                # Don't close if it's in the same group as the new document
                if new_group_id and session.group_id == new_group_id:
                    continue
                
                # Don't close if it's marked as collaborative or critical validation
                if session.context in [SessionContext.HUMAN_VALIDATION, SessionContext.COLLABORATIVE]:
                    continue
                    
                sessions_to_close.append((sid, session))
        
        if sessions_to_close:
            print(f"🔄 Closing {len(sessions_to_close)} unrelated GUI session(s)...")
            for session_id, session in sessions_to_close:
                self.close_document(session.file_path, "sequential_gui")
    
    def _get_session_id(self, file_path: str) -> str:
        """Generate unique session ID for a file path"""
        return f"doc_{hash(file_path) % 10000}"
    
    def _log_session_start(self, session: DocumentSession):
        """Log when a session starts"""
        self.session_history.append({
            'action': 'start',
            'file_path': session.file_path,
            'session_type': session.session_type,
            'process_id': session.process_id,
            'timestamp': session.opened_at.isoformat()
        })
    
    def _log_session_end(self, session_id: str, reason: str):
        """Log when a session ends"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            self.session_history.append({
                'action': 'end',
                'file_path': session.file_path,
                'session_type': session.session_type,
                'process_id': session.process_id,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - session.opened_at).total_seconds()
            })
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current status of document sessions"""
        self._cleanup_dead_sessions()
        
        return {
            'active_sessions': len(self.active_sessions),
            'max_concurrent': self.max_concurrent_docs,
            'sessions': [
                {
                    'file': Path(session.file_path).name,
                    'type': session.session_type,
                    'opened_at': session.opened_at.strftime('%H:%M:%S'),
                    'duration': str(datetime.now() - session.opened_at).split('.')[0]
                }
                for session in self.active_sessions.values()
            ],
            'libreoffice_processes': len(self._get_libreoffice_processes())
        }
    
    def print_session_status(self):
        """Print current session status"""
        status = self.get_session_status()
        
        print(f"\n📊 DOCUMENT SESSION STATUS")
        print(f"Active sessions: {status['active_sessions']}/{status['max_concurrent']}")
        print(f"LibreOffice processes: {status['libreoffice_processes']}")
        
        if status['sessions']:
            print("\nActive documents:")
            for session in status['sessions']:
                print(f"  • {session['file']} ({session['type']}) - {session['duration']}")
        else:
            print("No active document sessions")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all sessions"""
        self.close_all_documents("context_exit")


# Global session manager instance
_session_manager = None

def get_session_manager() -> DocumentSessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = DocumentSessionManager()
    return _session_manager


def main():
    """Test the document session manager"""
    print("🧪 TESTING DOCUMENT SESSION MANAGER")
    print("=" * 50)
    
    with DocumentSessionManager(max_concurrent_docs=2) as manager:
        # Test status
        manager.print_session_status()
        
        # Test document opening (if test files exist)
        test_files = [
            "/home/johnny5/Squirt/test_validation_samples/fall_cleanup_comprehensive.odt",
            "/home/johnny5/Squirt/test_validation_samples/irrigation_maintenance_basic.odt"
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\n🧪 Testing with: {Path(test_file).name}")
                success = manager.open_document_gui(test_file, "test document")
                if success:
                    manager.print_session_status()
                    time.sleep(2)  # Brief pause
                break
        else:
            print("\n⚠️ No test files found for GUI testing")
        
        # Final status
        print("\n🧪 Final status:")
        manager.print_session_status()


if __name__ == "__main__":
    main()