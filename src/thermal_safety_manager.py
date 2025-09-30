#!/usr/bin/env python3
"""
Thermal Safety Manager
Enhanced thermal monitoring and safety protocols for voice processing operations
"""

import subprocess
import time
import threading
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class ThermalState(Enum):
    """System thermal states"""
    SAFE = "safe"                    # <75°C - Normal operations
    WARM = "warm"                    # 75-80°C - Monitor closely
    HOT = "hot"                      # 80-85°C - Reduce operations
    CRITICAL = "critical"            # 85-90°C - Emergency protocols
    EMERGENCY = "emergency"          # >90°C - Immediate shutdown


class CoolingAction(Enum):
    """Available cooling actions"""
    NONE = "none"
    MONITOR = "monitor"
    REDUCE_LOAD = "reduce_load"
    DEFER_PROCESSING = "defer_processing"
    EMERGENCY_STOP = "emergency_stop"
    EXTERNAL_COOLING = "external_cooling"


@dataclass
class ThermalReading:
    """Single thermal reading"""
    timestamp: str
    cpu_temp: Optional[float]
    thermal_state: ThermalState
    cooling_action: CoolingAction
    fan_speed: Optional[int] = None  # RPM if available
    thermal_throttling: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ThermalPolicy:
    """Thermal management policy"""
    safe_threshold: float = 75.0
    warm_threshold: float = 80.0
    hot_threshold: float = 85.0
    critical_threshold: float = 90.0
    emergency_threshold: float = 95.0
    monitoring_interval: int = 30  # seconds
    alert_email: Optional[str] = None
    external_cooling_command: Optional[str] = None


class ThermalLogger:
    """Log thermal data for analysis"""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "/home/johnny5/Squirt/thermal_log.json"
        self.logger = logging.getLogger(__name__)

    def log_reading(self, reading: ThermalReading):
        """Log thermal reading to file"""
        try:
            log_entry = {
                "timestamp": reading.timestamp,
                "cpu_temp": reading.cpu_temp,
                "thermal_state": reading.thermal_state.value,
                "cooling_action": reading.cooling_action.value,
                "fan_speed": reading.fan_speed,
                "thermal_throttling": reading.thermal_throttling
            }

            # Append to log file
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

        except Exception as e:
            self.logger.error(f"Failed to log thermal reading: {e}")

    def get_recent_readings(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get thermal readings from last N hours"""
        readings = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        try:
            if Path(self.log_file).exists():
                with open(self.log_file, 'r') as f:
                    for line in f:
                        try:
                            reading = json.loads(line.strip())
                            reading_time = datetime.fromisoformat(reading['timestamp'])
                            if reading_time >= cutoff_time:
                                readings.append(reading)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue

        except Exception as e:
            self.logger.error(f"Failed to read thermal log: {e}")

        return readings

    def get_thermal_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get thermal summary for last N hours"""
        readings = self.get_recent_readings(hours)

        if not readings:
            return {"error": "No thermal data available"}

        temperatures = [r['cpu_temp'] for r in readings if r['cpu_temp'] is not None]
        states = [r['thermal_state'] for r in readings]

        if not temperatures:
            return {"error": "No temperature data available"}

        return {
            "period_hours": hours,
            "reading_count": len(readings),
            "temperature": {
                "min": min(temperatures),
                "max": max(temperatures),
                "avg": sum(temperatures) / len(temperatures),
                "current": temperatures[-1] if temperatures else None
            },
            "states": {
                "safe": states.count("safe"),
                "warm": states.count("warm"),
                "hot": states.count("hot"),
                "critical": states.count("critical"),
                "emergency": states.count("emergency")
            },
            "warnings": sum(1 for s in states if s in ["hot", "critical", "emergency"]),
            "last_reading": readings[-1]["timestamp"] if readings else None
        }


class ThermalSensor:
    """Interface to system thermal sensors"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_reading = None

    def read_cpu_temperature(self) -> Optional[float]:
        """Read CPU temperature from sensors"""
        try:
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return self._parse_sensors_output(result.stdout)

            self.logger.warning(f"Sensors command failed: {result.stderr}")
            return None

        except subprocess.TimeoutExpired:
            self.logger.warning("Sensors command timed out")
            return None
        except FileNotFoundError:
            self.logger.warning("Sensors command not found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read temperature: {e}")
            return None

    def _parse_sensors_output(self, output: str) -> Optional[float]:
        """Parse temperature from sensors output"""
        import re

        # Look for Package id 0 temperature (Intel CPUs)
        package_match = re.search(r'Package id 0:\s*\+(\d+\.\d+)°C', output)
        if package_match:
            return float(package_match.group(1))

        # Look for Core 0 temperature (fallback)
        core_match = re.search(r'Core 0:\s*\+(\d+\.\d+)°C', output)
        if core_match:
            return float(core_match.group(1))

        # Look for any CPU temperature
        cpu_match = re.search(r'CPU.*?:\s*\+(\d+\.\d+)°C', output)
        if cpu_match:
            return float(cpu_match.group(1))

        return None

    def read_fan_speed(self) -> Optional[int]:
        """Read fan speed if available"""
        try:
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return self._parse_fan_speed(result.stdout)

            return None

        except Exception:
            return None

    def _parse_fan_speed(self, output: str) -> Optional[int]:
        """Parse fan speed from sensors output"""
        import re

        # Look for fan speed in RPM
        fan_match = re.search(r'fan\d+:\s*(\d+)\s*RPM', output, re.IGNORECASE)
        if fan_match:
            return int(fan_match.group(1))

        return None

    def check_thermal_throttling(self) -> bool:
        """Check if system is thermal throttling"""
        try:
            # Check CPU frequency scaling
            result = subprocess.run(
                ["cat", "/proc/cpuinfo"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "cpu MHz" in result.stdout:
                # Parse CPU frequencies to detect throttling
                import re
                frequencies = re.findall(r'cpu MHz\s*:\s*(\d+\.\d+)', result.stdout)
                if frequencies:
                    freq_values = [float(f) for f in frequencies]
                    avg_freq = sum(freq_values) / len(freq_values)
                    # If frequency is significantly below expected, likely throttling
                    return avg_freq < 1000  # Below 1GHz suggests throttling

            return False

        except Exception:
            return False


class ThermalSafetyManager:
    """Main thermal safety management system"""

    def __init__(self, policy: Optional[ThermalPolicy] = None):
        self.policy = policy or ThermalPolicy()
        self.sensor = ThermalSensor()
        self.logger_system = ThermalLogger()
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        self.current_reading = None
        self.alert_callbacks = []

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self):
        """Start continuous thermal monitoring"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.warning("Thermal monitoring already running")
            return

        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Started thermal monitoring")

    def stop_monitoring_system(self):
        """Stop thermal monitoring"""
        if self.monitoring_thread:
            self.stop_monitoring.set()
            self.monitoring_thread.join(timeout=30)
            self.logger.info("Stopped thermal monitoring")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                reading = self.take_reading()
                self.current_reading = reading

                # Log the reading
                self.logger_system.log_reading(reading)

                # Take action based on thermal state
                self._handle_thermal_state(reading)

                # Trigger alerts if needed
                if reading.thermal_state in [ThermalState.CRITICAL, ThermalState.EMERGENCY]:
                    self._trigger_alerts(reading)

                # Wait for next reading
                time.sleep(self.policy.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Error in thermal monitoring loop: {e}")
                time.sleep(self.policy.monitoring_interval)

    def take_reading(self) -> ThermalReading:
        """Take a single thermal reading"""
        cpu_temp = self.sensor.read_cpu_temperature()
        fan_speed = self.sensor.read_fan_speed()
        thermal_throttling = self.sensor.check_thermal_throttling()

        # Determine thermal state
        if cpu_temp is None:
            thermal_state = ThermalState.SAFE  # Assume safe if can't read
            cooling_action = CoolingAction.MONITOR
        else:
            thermal_state, cooling_action = self._determine_thermal_state(cpu_temp)

        return ThermalReading(
            timestamp=datetime.now().isoformat(),
            cpu_temp=cpu_temp,
            thermal_state=thermal_state,
            cooling_action=cooling_action,
            fan_speed=fan_speed,
            thermal_throttling=thermal_throttling
        )

    def _determine_thermal_state(self, temperature: float) -> tuple:
        """Determine thermal state and required action"""
        if temperature >= self.policy.emergency_threshold:
            return ThermalState.EMERGENCY, CoolingAction.EMERGENCY_STOP
        elif temperature >= self.policy.critical_threshold:
            return ThermalState.CRITICAL, CoolingAction.DEFER_PROCESSING
        elif temperature >= self.policy.hot_threshold:
            return ThermalState.HOT, CoolingAction.REDUCE_LOAD
        elif temperature >= self.policy.warm_threshold:
            return ThermalState.WARM, CoolingAction.MONITOR
        else:
            return ThermalState.SAFE, CoolingAction.NONE

    def _handle_thermal_state(self, reading: ThermalReading):
        """Handle thermal state changes"""
        if reading.cooling_action == CoolingAction.EMERGENCY_STOP:
            self.logger.critical(f"THERMAL EMERGENCY: {reading.cpu_temp}°C - Stopping all operations")
            self._emergency_stop()

        elif reading.cooling_action == CoolingAction.DEFER_PROCESSING:
            self.logger.warning(f"THERMAL CRITICAL: {reading.cpu_temp}°C - Deferring voice processing")
            self._defer_voice_processing()

        elif reading.cooling_action == CoolingAction.REDUCE_LOAD:
            self.logger.warning(f"THERMAL HOT: {reading.cpu_temp}°C - Reducing system load")
            self._reduce_system_load()

        elif reading.cooling_action == CoolingAction.EXTERNAL_COOLING:
            self.logger.info(f"THERMAL WARM: {reading.cpu_temp}°C - Activating external cooling")
            self._activate_external_cooling()

    def _emergency_stop(self):
        """Emergency stop all operations"""
        # Notify all registered callbacks about emergency stop
        for callback in self.alert_callbacks:
            try:
                callback("emergency_stop", self.current_reading)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

    def _defer_voice_processing(self):
        """Defer voice processing operations"""
        # This would integrate with the queue manager
        self.logger.info("Deferring voice processing due to thermal conditions")

    def _reduce_system_load(self):
        """Reduce system load"""
        # Lower process priorities, reduce concurrent operations
        self.logger.info("Reducing system load due to thermal conditions")

    def _activate_external_cooling(self):
        """Activate external cooling if configured"""
        if self.policy.external_cooling_command:
            try:
                subprocess.run(self.policy.external_cooling_command, shell=True, timeout=30)
                self.logger.info("External cooling activated")
            except Exception as e:
                self.logger.error(f"Failed to activate external cooling: {e}")

    def _trigger_alerts(self, reading: ThermalReading):
        """Trigger thermal alerts"""
        alert_data = {
            "timestamp": reading.timestamp,
            "temperature": reading.cpu_temp,
            "state": reading.thermal_state.value,
            "action": reading.cooling_action.value,
            "message": f"Thermal alert: {reading.cpu_temp}°C ({reading.thermal_state.value})"
        }

        # Log alert
        self.logger.warning(f"THERMAL ALERT: {alert_data['message']}")

        # Email alert if configured
        if self.policy.alert_email:
            self._send_email_alert(alert_data)

    def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Send email alert (placeholder implementation)"""
        # This would integrate with actual email system
        self.logger.info(f"Email alert would be sent to {self.policy.alert_email}")

    def register_alert_callback(self, callback: Callable):
        """Register callback for thermal alerts"""
        self.alert_callbacks.append(callback)

    def is_safe_for_voice_processing(self, processing_mode: str = "fast") -> bool:
        """Check if thermal conditions are safe for voice processing"""
        if not self.current_reading:
            reading = self.take_reading()
        else:
            reading = self.current_reading

        if processing_mode == "fast":
            # Fast mode can run in warm conditions
            return reading.thermal_state in [ThermalState.SAFE, ThermalState.WARM]
        else:
            # Accurate mode needs cooler conditions
            return reading.thermal_state == ThermalState.SAFE

    def get_thermal_status(self) -> Dict[str, Any]:
        """Get current thermal status"""
        if not self.current_reading:
            reading = self.take_reading()
        else:
            reading = self.current_reading

        return {
            "current_reading": asdict(reading),
            "safe_for_voice_fast": self.is_safe_for_voice_processing("fast"),
            "safe_for_voice_accurate": self.is_safe_for_voice_processing("accurate"),
            "monitoring_active": self.monitoring_thread and self.monitoring_thread.is_alive(),
            "policy": asdict(self.policy),
            "recent_summary": self.logger_system.get_thermal_summary(hours=1)
        }


def main():
    """Command line interface for thermal safety management"""
    import argparse

    parser = argparse.ArgumentParser(description="Thermal Safety Manager")
    parser.add_argument("command", choices=["status", "monitor", "check", "summary"])
    parser.add_argument("--hours", type=int, default=24, help="Hours for summary command")

    args = parser.parse_args()

    thermal_manager = ThermalSafetyManager()

    if args.command == "status":
        status = thermal_manager.get_thermal_status()
        print(json.dumps(status, indent=2))

    elif args.command == "monitor":
        print("Thermal Safety Monitor - Press Ctrl+C to stop")
        thermal_manager.start_monitoring()

        try:
            while True:
                if thermal_manager.current_reading:
                    reading = thermal_manager.current_reading
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Temp: {reading.cpu_temp}°C, "
                          f"State: {reading.thermal_state.value}, "
                          f"Action: {reading.cooling_action.value}")
                time.sleep(10)
        except KeyboardInterrupt:
            thermal_manager.stop_monitoring_system()
            print("\nThermal monitoring stopped")

    elif args.command == "check":
        reading = thermal_manager.take_reading()
        print(f"Temperature: {reading.cpu_temp}°C")
        print(f"State: {reading.thermal_state.value}")
        print(f"Safe for voice (fast): {thermal_manager.is_safe_for_voice_processing('fast')}")
        print(f"Safe for voice (accurate): {thermal_manager.is_safe_for_voice_processing('accurate')}")

    elif args.command == "summary":
        summary = thermal_manager.logger_system.get_thermal_summary(args.hours)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()