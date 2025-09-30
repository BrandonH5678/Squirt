#!/usr/bin/env python3
"""
Voice Memo Queue Manager
Manages voice processing queue with business hours priority and thermal awareness
"""

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import queue
import subprocess

# Import standalone voice processing
try:
    from voice_document_processor import VoiceDocumentProcessor
    VOICE_PROCESSOR_AVAILABLE = True
except ImportError:
    VOICE_PROCESSOR_AVAILABLE = False


class QueuePriority(Enum):
    """Priority levels for voice processing queue"""
    EMERGENCY = 1       # Emergency requests (thermal issues, urgent client needs)
    BUSINESS_HOURS = 2  # Normal business hours processing
    BACKGROUND = 3      # Background processing during off-hours
    BATCH = 4          # Batch processing during maintenance windows


class ProcessingStatus(Enum):
    """Status of voice processing jobs"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"


@dataclass
class VoiceJob:
    """Represents a voice processing job in the queue"""
    job_id: str
    audio_file: str
    template_path: str
    priority: QueuePriority
    employee: Optional[str] = None
    client_name: Optional[str] = None
    processing_mode: str = "fast"
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 2

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class ThermalMonitor:
    """Monitor system thermal status for voice processing safety"""

    def __init__(self):
        self.last_check = None
        self.last_temperature = None
        self.check_interval = 30  # seconds

    def get_cpu_temperature(self) -> Optional[float]:
        """Get current CPU temperature in Celsius"""
        try:
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and "Package id 0" in result.stdout:
                # Parse temperature from sensors output
                for line in result.stdout.split('\n'):
                    if "Package id 0" in line:
                        # Look for temperature like "+85.0°C"
                        import re
                        temp_match = re.search(r'\+(\d+\.\d+)°C', line)
                        if temp_match:
                            return float(temp_match.group(1))

            return None

        except Exception as e:
            logging.warning(f"Failed to get CPU temperature: {e}")
            return None

    def is_safe_for_processing(self, processing_mode: str = "fast") -> bool:
        """Check if thermal conditions are safe for voice processing"""
        temp = self.get_cpu_temperature()

        if temp is None:
            # If we can't check temperature, assume it's safe
            return True

        self.last_temperature = temp
        self.last_check = datetime.now()

        # Temperature thresholds
        if processing_mode == "fast":
            # Fast mode can run at higher temperatures
            return temp < 85.0
        else:
            # Accurate mode requires cooler temperatures
            return temp < 80.0

    def get_status(self) -> Dict[str, Any]:
        """Get current thermal status"""
        return {
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "temperature": self.last_temperature,
            "safe_for_fast": self.last_temperature < 85.0 if self.last_temperature else None,
            "safe_for_accurate": self.last_temperature < 80.0 if self.last_temperature else None
        }


class BusinessHoursManager:
    """Manage business hours logic for voice processing priority"""

    def __init__(self):
        # Business hours: 6am-7pm Monday-Friday
        self.business_start = 6
        self.business_end = 19
        self.business_days = [0, 1, 2, 3, 4]  # Monday = 0, Friday = 4

    def is_business_hours(self, dt: Optional[datetime] = None) -> bool:
        """Check if given time (or now) is business hours"""
        if dt is None:
            dt = datetime.now()

        is_business_day = dt.weekday() in self.business_days
        is_business_time = self.business_start <= dt.hour < self.business_end

        return is_business_day and is_business_time

    def get_next_business_window(self) -> datetime:
        """Get next available business processing window"""
        now = datetime.now()

        if self.is_business_hours(now):
            return now

        # Find next business day/time
        next_time = now.replace(hour=self.business_start, minute=0, second=0, microsecond=0)

        # If it's after business hours today, move to tomorrow
        if now.hour >= self.business_end:
            next_time += timedelta(days=1)

        # Skip weekends
        while next_time.weekday() not in self.business_days:
            next_time += timedelta(days=1)

        return next_time

    def get_off_hours_window(self) -> Optional[datetime]:
        """Get next off-hours processing window (for background processing)"""
        now = datetime.now()

        if not self.is_business_hours(now):
            return now

        # Next off-hours is after business today or start of weekend
        next_time = now.replace(hour=self.business_end, minute=0, second=0, microsecond=0)

        # If it's weekend, we're already in off-hours
        if now.weekday() >= 5:  # Saturday/Sunday
            return now

        return next_time


class VoiceQueueManager:
    """Main queue manager for voice processing with business hours and thermal awareness"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "/home/johnny5/Squirt/voice_queue.db"
        self.thermal_monitor = ThermalMonitor()
        self.business_hours = BusinessHoursManager()
        self.processing_thread = None
        self.stop_processing = threading.Event()
        self.processing_lock = threading.Lock()
        self.job_callbacks = {}  # job_id -> callback function

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._init_database()

        # Import voice processor
        try:
            from voice_enabled_generator import VoiceEnabledEstimateGenerator
            self.voice_generator = VoiceEnabledEstimateGenerator()
        except ImportError:
            self.logger.warning("Voice processor not available")
            self.voice_generator = None

    def _init_database(self):
        """Initialize SQLite database for queue management"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS voice_jobs (
                    job_id TEXT PRIMARY KEY,
                    audio_file TEXT NOT NULL,
                    template_path TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    employee TEXT,
                    client_name TEXT,
                    processing_mode TEXT DEFAULT 'fast',
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT,
                    result_data TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 2
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON voice_jobs(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON voice_jobs(priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON voice_jobs(created_at)")

    def add_job(self, audio_file: str,
                template_path: str,
                priority: QueuePriority = QueuePriority.BUSINESS_HOURS,
                employee: Optional[str] = None,
                client_name: Optional[str] = None,
                processing_mode: str = "fast",
                callback: Optional[Callable] = None) -> str:
        """
        Add voice processing job to queue

        Args:
            audio_file: Path to audio file
            template_path: Path to template file
            priority: Processing priority
            employee: Employee name
            client_name: Client name for tracking
            processing_mode: "fast" or "accurate"
            callback: Optional callback function when job completes

        Returns:
            Job ID string
        """

        # Generate unique job ID
        job_id = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(audio_file) % 10000:04d}"

        job = VoiceJob(
            job_id=job_id,
            audio_file=audio_file,
            template_path=template_path,
            priority=priority,
            employee=employee,
            client_name=client_name,
            processing_mode=processing_mode
        )

        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO voice_jobs (
                    job_id, audio_file, template_path, priority, employee, client_name,
                    processing_mode, status, created_at, retry_count, max_retries
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.job_id, job.audio_file, job.template_path, job.priority.value,
                job.employee, job.client_name, job.processing_mode, job.status.value,
                job.created_at, job.retry_count, job.max_retries
            ))

        # Register callback if provided
        if callback:
            self.job_callbacks[job_id] = callback

        self.logger.info(f"Added voice job {job_id} with priority {priority.name}")
        return job_id

    def get_next_job(self) -> Optional[VoiceJob]:
        """Get next job to process based on priority and business hours"""

        now = datetime.now()
        is_business_time = self.business_hours.is_business_hours(now)

        # During business hours, prioritize business jobs
        # During off-hours, process background and batch jobs
        if is_business_time:
            priority_filter = [QueuePriority.EMERGENCY.value, QueuePriority.BUSINESS_HOURS.value]
        else:
            priority_filter = [
                QueuePriority.EMERGENCY.value,
                QueuePriority.BACKGROUND.value,
                QueuePriority.BATCH.value
            ]

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM voice_jobs
                WHERE status = 'pending' AND priority IN ({})
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            """.format(','.join('?' * len(priority_filter))), priority_filter)

            row = cursor.fetchone()
            if row:
                return VoiceJob(
                    job_id=row['job_id'],
                    audio_file=row['audio_file'],
                    template_path=row['template_path'],
                    priority=QueuePriority(row['priority']),
                    employee=row['employee'],
                    client_name=row['client_name'],
                    processing_mode=row['processing_mode'],
                    status=ProcessingStatus(row['status']),
                    created_at=row['created_at'],
                    started_at=row['started_at'],
                    completed_at=row['completed_at'],
                    error_message=row['error_message'],
                    result_data=json.loads(row['result_data']) if row['result_data'] else None,
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries']
                )

        return None

    def process_job(self, job: VoiceJob) -> bool:
        """Process a single voice job"""

        # Check thermal safety
        if not self.thermal_monitor.is_safe_for_processing(job.processing_mode):
            self.logger.warning(f"Deferring job {job.job_id} due to high temperature")
            self._update_job_status(job.job_id, ProcessingStatus.DEFERRED,
                                  error_message="Deferred due to high system temperature")
            return False

        # Update status to processing
        self._update_job_status(job.job_id, ProcessingStatus.PROCESSING,
                              started_at=datetime.now().isoformat())

        try:
            self.logger.info(f"Processing voice job {job.job_id}")

            if not self.voice_generator:
                raise RuntimeError("Voice generator not available")

            # Process voice memo
            result = self.voice_generator.generate_from_voice(
                audio_file=job.audio_file,
                template_path=job.template_path,
                mode=job.processing_mode,
                employee_name=job.employee,
                skip_visual_validation=False  # Always validate for quality
            )

            if result["success"]:
                # Job completed successfully
                self._update_job_status(
                    job.job_id,
                    ProcessingStatus.COMPLETED,
                    completed_at=datetime.now().isoformat(),
                    result_data=result
                )

                self.logger.info(f"Completed voice job {job.job_id}")

                # Execute callback if registered
                if job.job_id in self.job_callbacks:
                    try:
                        self.job_callbacks[job.job_id](job.job_id, result)
                    except Exception as e:
                        self.logger.error(f"Callback failed for job {job.job_id}: {e}")

                return True

            else:
                # Job failed
                error_msg = "; ".join(result.get("errors", ["Unknown error"]))
                self._handle_job_failure(job, error_msg)
                return False

        except Exception as e:
            self.logger.error(f"Error processing job {job.job_id}: {e}")
            self._handle_job_failure(job, str(e))
            return False

    def _handle_job_failure(self, job: VoiceJob, error_message: str):
        """Handle job failure with retry logic"""

        if job.retry_count < job.max_retries:
            # Retry the job
            self.logger.info(f"Retrying job {job.job_id} (attempt {job.retry_count + 1})")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE voice_jobs
                    SET status = ?, retry_count = ?, error_message = ?
                    WHERE job_id = ?
                """, (ProcessingStatus.PENDING.value, job.retry_count + 1, error_message, job.job_id))
        else:
            # Mark as failed permanently
            self._update_job_status(job.job_id, ProcessingStatus.FAILED,
                                  error_message=error_message,
                                  completed_at=datetime.now().isoformat())

    def _update_job_status(self, job_id: str, status: ProcessingStatus, **kwargs):
        """Update job status in database"""

        set_clause = ["status = ?"]
        params = [status.value]

        for key, value in kwargs.items():
            set_clause.append(f"{key} = ?")
            if key == "result_data" and isinstance(value, dict):
                params.append(json.dumps(value, default=str))
            else:
                params.append(value)

        params.append(job_id)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"""
                UPDATE voice_jobs SET {', '.join(set_clause)} WHERE job_id = ?
            """, params)

    def start_processing(self):
        """Start background processing thread"""

        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.warning("Processing thread already running")
            return

        self.stop_processing.clear()
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        self.logger.info("Started voice processing queue")

    def stop_processing_queue(self):
        """Stop background processing thread"""

        if self.processing_thread:
            self.stop_processing.set()
            self.processing_thread.join(timeout=30)
            self.logger.info("Stopped voice processing queue")

    def _processing_loop(self):
        """Main processing loop"""

        while not self.stop_processing.is_set():
            try:
                with self.processing_lock:
                    job = self.get_next_job()

                    if job:
                        self.process_job(job)
                    else:
                        # No jobs available, wait before checking again
                        time.sleep(10)

            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(30)  # Wait longer on errors

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM voice_jobs
                GROUP BY status
            """)

            status_counts = dict(cursor.fetchall())

            cursor = conn.execute("""
                SELECT priority, COUNT(*) as count
                FROM voice_jobs
                WHERE status = 'pending'
                GROUP BY priority
            """)

            priority_counts = dict(cursor.fetchall())

        return {
            "queue_size": status_counts.get("pending", 0),
            "processing": status_counts.get("processing", 0),
            "completed": status_counts.get("completed", 0),
            "failed": status_counts.get("failed", 0),
            "priority_breakdown": priority_counts,
            "thermal_status": self.thermal_monitor.get_status(),
            "business_hours": self.business_hours.is_business_hours(),
            "processing_active": self.processing_thread and self.processing_thread.is_alive()
        }

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific job"""

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM voice_jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)

        return None


def main():
    """Command line interface for queue management"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Queue Manager")
    parser.add_argument("command", choices=["add", "start", "stop", "status", "list"])
    parser.add_argument("--audio", help="Audio file path (for add command)")
    parser.add_argument("--template", help="Template file path (for add command)")
    parser.add_argument("--priority", choices=["emergency", "business", "background", "batch"],
                       default="business", help="Processing priority")
    parser.add_argument("--employee", help="Employee name")
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast")

    args = parser.parse_args()

    queue_manager = VoiceQueueManager()

    if args.command == "add":
        if not args.audio or not args.template:
            print("❌ Audio file and template required for add command")
            return

        priority_map = {
            "emergency": QueuePriority.EMERGENCY,
            "business": QueuePriority.BUSINESS_HOURS,
            "background": QueuePriority.BACKGROUND,
            "batch": QueuePriority.BATCH
        }

        job_id = queue_manager.add_job(
            audio_file=args.audio,
            template_path=args.template,
            priority=priority_map[args.priority],
            employee=args.employee,
            processing_mode=args.mode
        )

        print(f"✅ Added job {job_id}")

    elif args.command == "start":
        queue_manager.start_processing()
        print("✅ Started queue processing")

        try:
            while True:
                time.sleep(10)
                status = queue_manager.get_queue_status()
                print(f"Queue: {status['queue_size']} pending, {status['processing']} processing")

        except KeyboardInterrupt:
            queue_manager.stop_processing_queue()
            print("\n🛑 Stopped queue processing")

    elif args.command == "stop":
        queue_manager.stop_processing_queue()
        print("🛑 Stopped queue processing")

    elif args.command == "status":
        status = queue_manager.get_queue_status()
        print(json.dumps(status, indent=2))

    elif args.command == "list":
        with sqlite3.connect(queue_manager.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT job_id, status, priority, employee, created_at
                FROM voice_jobs
                ORDER BY created_at DESC
                LIMIT 20
            """)

            print("Recent Jobs:")
            for row in cursor:
                print(f"  {row['job_id']}: {row['status']} (priority {row['priority']}) - {row['employee']} - {row['created_at']}")


if __name__ == "__main__":
    main()