#!/usr/bin/env python3
"""
Enhanced Document Session Manager for Squirt 1.2
Manages LibreOffice document sessions with priority, context, and grouping

Enhanced Rules:
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


class EnhancedDocumentSessionManager:
    """
    Enhanced centralized manager for all LibreOffice document operations in Squirt
    Implements all 5 enhanced document handling rules
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
            # Remove from group
            session = self.active_sessions[session_id]
            if session.group_id and session.group_id in self.document_groups:
                self.document_groups[session.group_id].discard(session_id)
                if not self.document_groups[session.group_id]:
                    print(f"📋 Auto-removing empty group: {session.group_id}")
                    del self.document_groups[session.group_id]
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
            
            # Remove from group if it was part of one
            if session.group_id and session.group_id in self.document_groups:
                self.document_groups[session.group_id].discard(session_id)
                if not self.document_groups[session.group_id]:
                    print(f"📋 Auto-removing empty group: {session.group_id}")
                    del self.document_groups[session.group_id]
                    
            del self.active_sessions[session_id]
            return True
            
        except Exception as e:
            print(f"⚠️ Error closing document {file_path}: {e}")
            # Still remove from tracking even if close failed
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
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
        if group_id in self.document_groups:
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
    
    def update_session_activity(self, file_path: str):
        """Update last activity time for a session (prevents auto-close)"""
        session_id = self._get_session_id(file_path)
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.now()
    
    def set_session_exempt(self, file_path: str, exempt: bool = True, reason: str = "manual"):
        """Mark a session as exempt from automatic closure"""
        session_id = self._get_session_id(file_path)
        if session_id in self.active_sessions:
            self.active_sessions[session_id].auto_close_exempt = exempt
            if exempt:
                self.active_sessions[session_id].keep_alive_reason = reason
                print(f"🛡️ Protected session from auto-close: {Path(file_path).name} ({reason})")
            else:
                self.active_sessions[session_id].keep_alive_reason = None
                print(f"⚙️ Removed auto-close protection: {Path(file_path).name}")
    
    def open_document_gui(self, file_path: str, document_type: str = "document", 
                         priority: SessionPriority = SessionPriority.COMPARATIVE_ANALYSIS,
                         context: SessionContext = SessionContext.HUMAN_VALIDATION,
                         group_id: Optional[str] = None,
                         keep_alive_reason: Optional[str] = None) -> bool:
        """
        Open document in LibreOffice GUI with enhanced priority and context management
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
        print(f"   Priority: {priority.name}, Context: {context.value}")
        
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
                    
                    # Check if GUI process is running
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
    
    # Convenience methods for common Squirt workflows
    
    def open_for_template_comparison(self, template_paths: List[str], comparison_purpose: str = "validation") -> Optional[str]:
        """Open multiple templates for side-by-side comparison"""
        if len(template_paths) > 4:
            print(f"⚠️ Too many templates for comparison ({len(template_paths)}), limiting to 4")
            template_paths = template_paths[:4]
        
        group_id = f"comparison_{int(time.time())}"
        session_ids = []
        
        print(f"🔍 Opening {len(template_paths)} templates for comparison...")
        
        for template_path in template_paths:
            success = self.open_document_gui(
                template_path,
                document_type="template",
                priority=SessionPriority.CRITICAL_VALIDATION,
                context=SessionContext.HUMAN_VALIDATION,
                group_id=group_id,
                keep_alive_reason=f"template_comparison_{comparison_purpose}"
            )
            
            if success:
                session_ids.append(self._get_session_id(template_path))
            else:
                print(f"⚠️ Failed to open: {Path(template_path).name}")
        
        if len(session_ids) >= 2:  # Need at least 2 for comparison
            self.create_document_group(group_id, session_ids, f"template_comparison_{comparison_purpose}")
            return group_id
        else:
            print("❌ Failed to open sufficient templates for comparison")
            return None
    
    def open_for_client_portfolio(self, client_documents: List[str], client_name: str) -> Optional[str]:
        """Open multiple documents for a single client portfolio review"""
        group_id = f"client_{client_name.lower().replace(' ', '_')}_{int(time.time())}"
        session_ids = []
        
        print(f"📁 Opening {len(client_documents)} documents for client {client_name}...")
        
        for doc_path in client_documents:
            success = self.open_document_gui(
                doc_path,
                document_type="client document",
                priority=SessionPriority.ACTIVE_CLIENT_WORK,
                context=SessionContext.COLLABORATIVE,
                group_id=group_id,
                keep_alive_reason=f"client_portfolio_{client_name}"
            )
            
            if success:
                session_ids.append(self._get_session_id(doc_path))
        
        if session_ids:
            self.create_document_group(group_id, session_ids, f"client_portfolio_{client_name}")
            return group_id
        
        return None
    
    def _get_session_id(self, file_path: str) -> str:
        """Generate unique session ID for a file path"""
        return f"doc_{hash(file_path) % 10000}"
    
    def _log_session_start(self, session: DocumentSession):
        """Log when a session starts with enhanced context info"""
        self.session_history.append({
            'action': 'start',
            'file_path': session.file_path,
            'session_type': session.session_type,
            'priority': session.priority.name,
            'context': session.context.value,
            'group_id': session.group_id,
            'process_id': session.process_id,
            'timestamp': session.opened_at.isoformat(),
            'keep_alive_reason': session.keep_alive_reason
        })
    
    def _log_session_end(self, session_id: str, reason: str):
        """Log when a session ends with enhanced context info"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            self.session_history.append({
                'action': 'end',
                'file_path': session.file_path,
                'session_type': session.session_type,
                'priority': session.priority.name,
                'context': session.context.value,
                'group_id': session.group_id,
                'process_id': session.process_id,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - session.opened_at).total_seconds(),
                'keep_alive_reason': session.keep_alive_reason
            })
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current status of document sessions"""
        self._cleanup_dead_sessions()
        
        sessions_by_priority = {}
        for session in self.active_sessions.values():
            priority_name = session.priority.name
            if priority_name not in sessions_by_priority:
                sessions_by_priority[priority_name] = []
            
            sessions_by_priority[priority_name].append({
                'file': Path(session.file_path).name,
                'type': session.session_type,
                'context': session.context.value,
                'opened_at': session.opened_at.strftime('%H:%M:%S'),
                'duration': str(datetime.now() - session.opened_at).split('.')[0],
                'group_id': session.group_id,
                'exempt': session.auto_close_exempt,
                'keep_alive_reason': session.keep_alive_reason
            })
        
        return {
            'active_sessions': len(self.active_sessions),
            'max_concurrent': self.max_concurrent_docs,
            'sessions_by_priority': sessions_by_priority,
            'document_groups': {gid: len(sessions) for gid, sessions in self.document_groups.items()},
            'libreoffice_processes': len(self._get_libreoffice_processes())
        }
    
    def print_session_status(self):
        """Print enhanced session status with priorities and groups"""
        status = self.get_session_status()
        
        print(f"\n📊 ENHANCED DOCUMENT SESSION STATUS")
        print(f"Active sessions: {status['active_sessions']}/{status['max_concurrent']}")
        print(f"LibreOffice processes: {status['libreoffice_processes']}")
        
        if status['document_groups']:
            print(f"\n📋 Document Groups:")
            for group_id, count in status['document_groups'].items():
                print(f"  • {group_id}: {count} documents")
        
        if status['sessions_by_priority']:
            print("\n📄 Active Documents by Priority:")
            for priority, sessions in status['sessions_by_priority'].items():
                print(f"\n  {priority} ({len(sessions)} docs):")
                for session in sessions:
                    exempt_flag = "🛡️" if session['exempt'] else ""
                    group_flag = f"[{session['group_id']}] " if session['group_id'] else ""
                    context_flag = f"({session['context']}) "
                    print(f"    • {group_flag}{session['file']} {context_flag}{session['duration']} {exempt_flag}")
                    if session['keep_alive_reason']:
                        print(f"      ↳ Keep-alive: {session['keep_alive_reason']}")
        else:
            print("No active document sessions")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all sessions"""
        self.close_all_documents("context_exit")


# Global session manager instance
_enhanced_session_manager = None

def get_enhanced_session_manager() -> EnhancedDocumentSessionManager:
    """Get the global enhanced session manager instance"""
    global _enhanced_session_manager
    if _enhanced_session_manager is None:
        _enhanced_session_manager = EnhancedDocumentSessionManager()
    return _enhanced_session_manager


def main():
    """Test the enhanced document session manager"""
    print("🧪 TESTING ENHANCED DOCUMENT SESSION MANAGER")
    print("=" * 60)
    
    with EnhancedDocumentSessionManager(max_concurrent_docs=4) as manager:
        # Test initial status
        manager.print_session_status()
        
        # Test template comparison workflow
        test_templates = [
            "/home/johnny5/Squirt/test_validation_samples/fall_cleanup_comprehensive.odt",
            "/home/johnny5/Squirt/test_validation_samples/path_lighting_economy.odt"
        ]
        
        existing_templates = [f for f in test_templates if os.path.exists(f)]
        
        if len(existing_templates) >= 2:
            print(f"\n🔍 Testing template comparison workflow...")
            group_id = manager.open_for_template_comparison(existing_templates, "sprint4_validation")
            
            if group_id:
                print(f"\n✅ Template comparison group created: {group_id}")
                manager.print_session_status()
                
                # Test session activity update
                time.sleep(2)
                manager.update_session_activity(existing_templates[0])
                print(f"\n🔄 Updated activity for: {Path(existing_templates[0]).name}")
                
                # Test closing the group
                time.sleep(2)
                print(f"\n📋 Closing comparison group...")
                manager.close_document_group(group_id, "test_complete")
        
        else:
            print("\n⚠️ Not enough test files for comparison workflow")
            # Test individual document opening
            if existing_templates:
                print(f"\n🧪 Testing individual document: {Path(existing_templates[0]).name}")
                success = manager.open_document_gui(
                    existing_templates[0], 
                    "test document",
                    priority=SessionPriority.CRITICAL_VALIDATION,
                    context=SessionContext.HUMAN_VALIDATION,
                    keep_alive_reason="manual_test"
                )
                if success:
                    manager.print_session_status()
        
        # Final status
        print("\n🧪 Final enhanced session status:")
        manager.print_session_status()


if __name__ == "__main__":
    main()