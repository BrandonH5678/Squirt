#!/usr/bin/env python3
"""
LibreOffice Coordinator
Manages voice processing coordination with LibreOffice document generation
"""

import os
import subprocess
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import psutil


class LibreOfficeState(Enum):
    """LibreOffice application states"""
    NOT_RUNNING = "not_running"
    IDLE = "idle"
    DOCUMENT_OPEN = "document_open"
    BUSY_PROCESSING = "busy_processing"
    ERROR_STATE = "error_state"


class ProcessPriority(Enum):
    """Process priority levels"""
    CRITICAL = 1      # LibreOffice document generation during business hours
    HIGH = 2         # Voice processing for urgent client requests
    NORMAL = 3       # Regular voice processing
    BACKGROUND = 4   # Batch operations


@dataclass
class LibreOfficeProcess:
    """Information about LibreOffice process"""
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    open_files: List[str]
    state: LibreOfficeState
    last_activity: datetime


class ResourceMonitor:
    """Monitor system resources for coordination"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)

            # Load average
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)

            return {
                "cpu_percent": cpu_percent,
                "memory_used_mb": memory_mb,
                "memory_available_mb": memory_available_mb,
                "memory_percent": memory.percent,
                "load_average": load_avg[0],  # 1-minute load average
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to get system resources: {e}")
            return {
                "cpu_percent": 0,
                "memory_used_mb": 0,
                "memory_available_mb": 1000,  # Assume some available memory
                "memory_percent": 0,
                "load_average": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def is_system_under_load(self) -> bool:
        """Check if system is under heavy load"""
        resources = self.get_system_resources()

        # System is under load if:
        # - CPU usage > 80%
        # - Memory usage > 90%
        # - Load average > 3.0 (for single core systems)
        return (
            resources["cpu_percent"] > 80 or
            resources["memory_percent"] > 90 or
            resources["load_average"] > 3.0
        )


class LibreOfficeMonitor:
    """Monitor LibreOffice processes and state"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.process_cache = {}
        self.last_scan = None

    def get_libreoffice_processes(self) -> List[LibreOfficeProcess]:
        """Get all LibreOffice-related processes"""
        processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    pinfo = proc.info
                    if any(name in pinfo['name'].lower() for name in ['soffice', 'libreoffice']):

                        # Get open files for this process
                        open_files = []
                        try:
                            for file in proc.open_files():
                                open_files.append(file.path)
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass

                        # Determine process state
                        state = self._determine_process_state(proc, open_files)

                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024) if pinfo['memory_info'] else 0

                        lo_process = LibreOfficeProcess(
                            pid=pinfo['pid'],
                            name=pinfo['name'],
                            cpu_percent=pinfo['cpu_percent'] or 0,
                            memory_mb=memory_mb,
                            open_files=open_files,
                            state=state,
                            last_activity=datetime.now()
                        )

                        processes.append(lo_process)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            self.logger.error(f"Error scanning LibreOffice processes: {e}")

        self.last_scan = datetime.now()
        return processes

    def _determine_process_state(self, proc, open_files: List[str]) -> LibreOfficeState:
        """Determine LibreOffice process state"""
        try:
            # Check if process is responsive
            if proc.status() == psutil.STATUS_ZOMBIE:
                return LibreOfficeState.ERROR_STATE

            # Check CPU usage to determine if busy
            cpu_percent = proc.cpu_percent()
            if cpu_percent > 50:  # High CPU usage
                return LibreOfficeState.BUSY_PROCESSING

            # Check if document files are open
            document_extensions = {'.odt', '.ods', '.odp', '.doc', '.docx', '.xls', '.xlsx', '.pdf'}
            has_documents = any(
                any(Path(f).suffix.lower() == ext for ext in document_extensions)
                for f in open_files
            )

            if has_documents:
                return LibreOfficeState.DOCUMENT_OPEN
            else:
                return LibreOfficeState.IDLE

        except Exception:
            return LibreOfficeState.ERROR_STATE

    def is_libreoffice_busy(self) -> bool:
        """Check if LibreOffice is currently busy"""
        processes = self.get_libreoffice_processes()

        for proc in processes:
            if proc.state in [LibreOfficeState.BUSY_PROCESSING, LibreOfficeState.DOCUMENT_OPEN]:
                return True

        return False

    def wait_for_libreoffice_idle(self, timeout: int = 300) -> bool:
        """Wait for LibreOffice to become idle"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if not self.is_libreoffice_busy():
                return True

            time.sleep(5)  # Check every 5 seconds

        return False

    def get_libreoffice_status(self) -> Dict[str, Any]:
        """Get comprehensive LibreOffice status"""
        processes = self.get_libreoffice_processes()

        if not processes:
            return {
                "status": "not_running",
                "process_count": 0,
                "total_memory_mb": 0,
                "total_cpu_percent": 0,
                "documents_open": 0,
                "last_scan": self.last_scan.isoformat() if self.last_scan else None
            }

        total_memory = sum(proc.memory_mb for proc in processes)
        total_cpu = sum(proc.cpu_percent for proc in processes)
        documents_open = sum(1 for proc in processes if proc.state == LibreOfficeState.DOCUMENT_OPEN)

        # Determine overall status
        if any(proc.state == LibreOfficeState.BUSY_PROCESSING for proc in processes):
            overall_status = "busy"
        elif any(proc.state == LibreOfficeState.DOCUMENT_OPEN for proc in processes):
            overall_status = "document_open"
        elif any(proc.state == LibreOfficeState.ERROR_STATE for proc in processes):
            overall_status = "error"
        else:
            overall_status = "idle"

        return {
            "status": overall_status,
            "process_count": len(processes),
            "total_memory_mb": total_memory,
            "total_cpu_percent": total_cpu,
            "documents_open": documents_open,
            "processes": [
                {
                    "pid": proc.pid,
                    "name": proc.name,
                    "state": proc.state.value,
                    "memory_mb": proc.memory_mb,
                    "cpu_percent": proc.cpu_percent
                }
                for proc in processes
            ],
            "last_scan": self.last_scan.isoformat() if self.last_scan else None
        }


class ProcessCoordinator:
    """Coordinate voice processing with LibreOffice operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.libreoffice_monitor = LibreOfficeMonitor()
        self.resource_monitor = ResourceMonitor()
        self.coordination_lock = threading.Lock()

        # Business hours manager
        from voice_queue_manager import BusinessHoursManager
        self.business_hours = BusinessHoursManager()

    def can_start_voice_processing(self, priority: ProcessPriority = ProcessPriority.NORMAL) -> Dict[str, Any]:
        """
        Check if voice processing can start given current system state

        Args:
            priority: Priority level of the voice processing request

        Returns:
            Dictionary with decision and reasoning
        """

        result = {
            "can_start": False,
            "reason": "",
            "suggested_delay": 0,  # seconds to wait before retrying
            "system_status": {}
        }

        # Get current system status
        lo_status = self.libreoffice_monitor.get_libreoffice_status()
        system_resources = self.resource_monitor.get_system_resources()
        is_business_hours = self.business_hours.is_business_hours()

        result["system_status"] = {
            "libreoffice": lo_status,
            "resources": system_resources,
            "business_hours": is_business_hours
        }

        # Critical priority can always start (emergency situations)
        if priority == ProcessPriority.CRITICAL:
            result["can_start"] = True
            result["reason"] = "Critical priority overrides all restrictions"
            return result

        # During business hours, LibreOffice has priority
        if is_business_hours:
            if lo_status["status"] in ["busy", "document_open"]:
                if priority == ProcessPriority.HIGH:
                    # High priority can interrupt idle LibreOffice
                    if lo_status["status"] == "document_open" and lo_status["total_cpu_percent"] < 20:
                        result["can_start"] = True
                        result["reason"] = "High priority with idle LibreOffice"
                        return result
                else:
                    result["reason"] = "LibreOffice active during business hours"
                    result["suggested_delay"] = 60  # Check again in 1 minute
                    return result

        # Check system resources
        if self.resource_monitor.is_system_under_load():
            result["reason"] = "System under heavy load"
            result["suggested_delay"] = 120  # Wait 2 minutes for load to decrease
            return result

        # Check available memory
        if system_resources["memory_available_mb"] < 500:  # Need at least 500MB for voice processing
            result["reason"] = "Insufficient available memory"
            result["suggested_delay"] = 180  # Wait 3 minutes
            return result

        # All checks passed
        result["can_start"] = True
        result["reason"] = "System ready for voice processing"
        return result

    def request_processing_slot(self,
                              priority: ProcessPriority = ProcessPriority.NORMAL,
                              estimated_duration: int = 60) -> Dict[str, Any]:
        """
        Request a processing slot for voice processing

        Args:
            priority: Priority level
            estimated_duration: Estimated processing time in seconds

        Returns:
            Slot allocation result
        """

        with self.coordination_lock:
            # Check if we can start immediately
            can_start_result = self.can_start_voice_processing(priority)

            if can_start_result["can_start"]:
                # Grant immediate slot
                return {
                    "granted": True,
                    "start_immediately": True,
                    "estimated_start": datetime.now().isoformat(),
                    "estimated_end": (datetime.now() + timedelta(seconds=estimated_duration)).isoformat(),
                    "reason": can_start_result["reason"]
                }

            else:
                # Calculate next available slot
                next_slot = self._calculate_next_available_slot(priority, estimated_duration)

                return {
                    "granted": True,
                    "start_immediately": False,
                    "estimated_start": next_slot["start_time"],
                    "estimated_end": next_slot["end_time"],
                    "delay_reason": can_start_result["reason"],
                    "suggested_delay": can_start_result["suggested_delay"]
                }

    def _calculate_next_available_slot(self,
                                     priority: ProcessPriority,
                                     duration: int) -> Dict[str, str]:
        """Calculate next available processing slot"""

        now = datetime.now()

        if priority == ProcessPriority.BACKGROUND:
            # Background processing waits for off-hours
            next_slot = self.business_hours.get_off_hours_window()
        else:
            # Other priorities can use next business hour gap
            next_slot = now + timedelta(minutes=5)  # Default 5-minute delay

        return {
            "start_time": next_slot.isoformat(),
            "end_time": (next_slot + timedelta(seconds=duration)).isoformat()
        }

    def notify_processing_start(self, job_id: str, priority: ProcessPriority):
        """Notify coordinator that voice processing has started"""
        self.logger.info(f"Voice processing started: job {job_id} with priority {priority.name}")

    def notify_processing_end(self, job_id: str, success: bool):
        """Notify coordinator that voice processing has ended"""
        self.logger.info(f"Voice processing ended: job {job_id}, success: {success}")

    def emergency_stop_voice_processing(self):
        """Emergency stop of voice processing for critical LibreOffice operations"""
        self.logger.warning("Emergency stop requested for voice processing")
        # This would integrate with the queue manager to pause processing
        # Implementation depends on the specific voice processing system

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status"""

        lo_status = self.libreoffice_monitor.get_libreoffice_status()
        system_resources = self.resource_monitor.get_system_resources()
        is_business_hours = self.business_hours.is_business_hours()

        # Determine current coordination state
        if is_business_hours and lo_status["status"] in ["busy", "document_open"]:
            coordination_state = "libreoffice_priority"
        elif self.resource_monitor.is_system_under_load():
            coordination_state = "resource_constrained"
        else:
            coordination_state = "voice_processing_available"

        return {
            "coordination_state": coordination_state,
            "business_hours": is_business_hours,
            "libreoffice_status": lo_status,
            "system_resources": system_resources,
            "voice_processing_available": coordination_state == "voice_processing_available",
            "timestamp": datetime.now().isoformat()
        }


class LibreOfficeIntegration:
    """Main integration class for LibreOffice coordination"""

    def __init__(self):
        self.coordinator = ProcessCoordinator()
        self.logger = logging.getLogger(__name__)

    def start_coordinated_voice_processing(self,
                                         job_data: Dict[str, Any],
                                         priority: ProcessPriority = ProcessPriority.NORMAL) -> Dict[str, Any]:
        """
        Start voice processing with LibreOffice coordination

        Args:
            job_data: Voice processing job data
            priority: Processing priority

        Returns:
            Processing result
        """

        job_id = job_data.get("job_id", "unknown")
        estimated_duration = job_data.get("estimated_duration", 60)

        # Request processing slot
        slot_request = self.coordinator.request_processing_slot(priority, estimated_duration)

        if not slot_request["granted"]:
            return {
                "success": False,
                "reason": "Processing slot not granted",
                "details": slot_request
            }

        if not slot_request["start_immediately"]:
            return {
                "success": False,
                "reason": "Processing deferred",
                "start_time": slot_request["estimated_start"],
                "details": slot_request
            }

        # Start processing
        try:
            self.coordinator.notify_processing_start(job_id, priority)

            # Import and use voice processing
            from voice_enabled_generator import VoiceEnabledEstimateGenerator

            generator = VoiceEnabledEstimateGenerator()
            result = generator.generate_from_voice(
                audio_file=job_data["audio_file"],
                template_path=job_data["template_path"],
                mode=job_data.get("processing_mode", "fast"),
                employee_name=job_data.get("employee"),
                skip_visual_validation=False
            )

            self.coordinator.notify_processing_end(job_id, result["success"])
            return result

        except Exception as e:
            self.coordinator.notify_processing_end(job_id, False)
            self.logger.error(f"Coordinated voice processing failed: {e}")
            return {
                "success": False,
                "reason": f"Processing failed: {e}"
            }

    def monitor_libreoffice_state(self) -> Dict[str, Any]:
        """Get current LibreOffice state for monitoring"""
        return self.coordinator.get_coordination_status()


def main():
    """Command line interface for LibreOffice coordination"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="LibreOffice Coordination Monitor")
    parser.add_argument("command", choices=["status", "monitor", "check"])
    parser.add_argument("--priority", choices=["critical", "high", "normal", "background"],
                       default="normal", help="Processing priority for check command")

    args = parser.parse_args()

    coordinator = ProcessCoordinator()

    if args.command == "status":
        status = coordinator.get_coordination_status()
        print(json.dumps(status, indent=2))

    elif args.command == "monitor":
        print("LibreOffice Coordination Monitor - Press Ctrl+C to stop")
        try:
            while True:
                status = coordinator.get_coordination_status()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"State: {status['coordination_state']}, "
                      f"LO: {status['libreoffice_status']['status']}, "
                      f"CPU: {status['system_resources']['cpu_percent']:.1f}%")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

    elif args.command == "check":
        priority_map = {
            "critical": ProcessPriority.CRITICAL,
            "high": ProcessPriority.HIGH,
            "normal": ProcessPriority.NORMAL,
            "background": ProcessPriority.BACKGROUND
        }

        result = coordinator.can_start_voice_processing(priority_map[args.priority])
        print(f"Can start voice processing: {result['can_start']}")
        print(f"Reason: {result['reason']}")
        if result['suggested_delay'] > 0:
            print(f"Suggested delay: {result['suggested_delay']} seconds")


if __name__ == "__main__":
    main()