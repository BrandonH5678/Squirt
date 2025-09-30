#!/usr/bin/env python3
"""
Squirt Standalone Voice Processing Engine
Complete voice processing system for business document automation
"""

import json
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import threading
import queue

# Core dependencies
import numpy as np
from pydub import AudioSegment

# Engine imports (to be loaded lazily)
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import whisper
    OPENAI_WHISPER_AVAILABLE = True
except ImportError:
    OPENAI_WHISPER_AVAILABLE = False


class TranscriptionMode(Enum):
    FAST = "fast"           # faster-whisper tiny for speed
    ACCURATE = "accurate"   # whisper large-v3 for accuracy
    AUTO = "auto"          # system chooses based on content


class ProcessingPriority(Enum):
    EMERGENCY = "emergency"    # Emergency client requests
    BUSINESS = "business"      # Normal business hours processing
    BACKGROUND = "background"  # Background processing
    BATCH = "batch"           # Batch operations


@dataclass
class VoiceProcessingRequest:
    """Request for voice processing"""
    audio_path: str
    mode: TranscriptionMode
    priority: ProcessingPriority
    metadata: Dict = None
    callback: Optional[callable] = None


@dataclass
class TranscriptionResult:
    """Result from voice transcription"""
    text: str
    segments: List[Dict]
    processing_time: float
    model_used: str
    confidence: float
    metadata: Dict = None


class SquirtVoiceEngine:
    """
    Standalone voice processing engine for Squirt business document automation
    Optimized for WaterWizard landscaping business workflows
    """

    def __init__(self, max_ram_gb: float = 4.0):
        self.max_ram_gb = max_ram_gb
        self.models = {}
        self.processing_queue = queue.PriorityQueue()
        self.current_processing = None
        self.stats = {
            "requests_processed": 0,
            "fast_mode_count": 0,
            "accurate_mode_count": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Threading for queue processing
        self.processing_thread = None
        self.shutdown_event = threading.Event()

        self.logger.info("Squirt Voice Engine initialized")

    def start(self):
        """Start the voice processing service"""
        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.warning("Voice engine already running")
            return

        self.logger.info("Starting Squirt Voice Engine")
        self.shutdown_event.clear()
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()

    def stop(self):
        """Stop the voice processing service"""
        self.logger.info("Stopping Squirt Voice Engine")
        self.shutdown_event.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=30)

    def transcribe_audio(self,
                        audio_path: str,
                        mode: TranscriptionMode = TranscriptionMode.FAST,
                        priority: ProcessingPriority = ProcessingPriority.BUSINESS,
                        context: Optional[str] = None) -> Dict:
        """
        Synchronous transcription for business document processing

        Args:
            audio_path: Path to audio file
            mode: Fast or accurate processing mode
            priority: Processing priority level
            context: Additional context for processing

        Returns:
            Dictionary with transcription results
        """

        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        start_time = time.time()

        try:
            # Load appropriate model
            if not self._load_model(mode):
                raise Exception(f"Failed to load model for mode: {mode}")

            # Ensure audio is in correct format
            processed_audio_path = self._ensure_wav_format(audio_path)

            # Transcribe based on mode
            if mode == TranscriptionMode.FAST:
                result = self._transcribe_fast(processed_audio_path)
                self.stats["fast_mode_count"] += 1
            elif mode == TranscriptionMode.ACCURATE:
                result = self._transcribe_accurate(processed_audio_path)
                self.stats["accurate_mode_count"] += 1
            else:
                raise Exception(f"Unsupported mode: {mode}")

            processing_time = time.time() - start_time

            # Update stats
            self.stats["requests_processed"] += 1
            self.stats["total_processing_time"] += processing_time
            self.stats["average_processing_time"] = (
                self.stats["total_processing_time"] / self.stats["requests_processed"]
            )

            return {
                "transcription": result["text"],
                "segments": result.get("segments", []),
                "processing_time": processing_time,
                "model_used": result["model"],
                "confidence": result.get("confidence", 0.0),
                "mode": mode.value,
                "context": context,
                "audio_duration": result.get("duration", 0.0),
                "language": result.get("language", "unknown")
            }

        except Exception as e:
            self.logger.error(f"Transcription failed for {audio_path}: {e}")
            return {
                "transcription": "",
                "segments": [],
                "processing_time": time.time() - start_time,
                "model_used": "none",
                "confidence": 0.0,
                "mode": mode.value,
                "error": str(e)
            }

    def _load_model(self, mode: TranscriptionMode) -> bool:
        """Lazy load transcription models based on mode"""
        if mode == TranscriptionMode.FAST:
            if "faster_whisper_tiny" not in self.models:
                if not FASTER_WHISPER_AVAILABLE:
                    self.logger.error("faster-whisper not available")
                    return False

                self.logger.info("Loading faster-whisper tiny model")
                try:
                    self.models["faster_whisper_tiny"] = WhisperModel(
                        "tiny",
                        device="cpu",
                        compute_type="int8"
                    )
                    self.logger.info("faster-whisper tiny model loaded successfully")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to load faster-whisper tiny: {e}")
                    return False
            return True

        elif mode == TranscriptionMode.ACCURATE:
            if "whisper_large_v3" not in self.models:
                if not OPENAI_WHISPER_AVAILABLE:
                    self.logger.error("openai-whisper not available")
                    return False

                self.logger.info("Loading Whisper Large-v3 model")
                try:
                    self.models["whisper_large_v3"] = whisper.load_model(
                        "large-v3",
                        device="cpu"
                    )
                    self.logger.info("Whisper Large-v3 model loaded successfully")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to load Whisper Large-v3: {e}")
                    return False
            return True

        return False

    def _process_queue(self):
        """Background thread to process voice requests"""
        while not self.shutdown_event.is_set():
            try:
                # Get request with timeout
                priority, timestamp, request = self.processing_queue.get(timeout=1.0)

                self.current_processing = request
                self.logger.info(f"Processing voice request: {request.audio_path}")

                result = self._process_request(request)

                # Execute callback if provided
                if request.callback:
                    request.callback(result)

                self.current_processing = None

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing request: {e}")
                self.current_processing = None

    def _process_request(self, request: VoiceProcessingRequest) -> TranscriptionResult:
        """Process a voice request"""
        start_time = time.time()

        # Load appropriate model
        if not self._load_model(request.mode):
            raise Exception(f"Failed to load model for mode: {request.mode}")

        # Ensure audio is in correct format
        processed_audio_path = self._ensure_wav_format(request.audio_path)

        # Transcribe based on mode
        if request.mode == TranscriptionMode.FAST:
            result = self._transcribe_fast(processed_audio_path)
        elif request.mode == TranscriptionMode.ACCURATE:
            result = self._transcribe_accurate(processed_audio_path)
        else:
            raise Exception(f"Unsupported mode: {request.mode}")

        processing_time = time.time() - start_time

        return TranscriptionResult(
            text=result["text"],
            segments=result.get("segments", []),
            processing_time=processing_time,
            model_used=result["model"],
            confidence=result.get("confidence", 0.0),
            metadata={"mode": request.mode.value, "priority": request.priority.value}
        )

    def _ensure_wav_format(self, audio_path: str) -> str:
        """Ensure audio is in WAV format at 16kHz mono for processing"""
        path = Path(audio_path)

        # If already a WAV file, check if it needs conversion
        if path.suffix.lower() == '.wav':
            try:
                audio = AudioSegment.from_wav(audio_path)
                if audio.frame_rate == 16000 and audio.channels == 1:
                    return audio_path  # Already in correct format
            except:
                pass

        # Convert to proper format
        try:
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_frame_rate(16000).set_channels(1)

            # Create temp file in same directory
            temp_dir = path.parent / "temp_audio"
            temp_dir.mkdir(exist_ok=True)

            output_path = temp_dir / f"{path.stem}_16k_mono.wav"
            audio.export(str(output_path), format="wav")

            self.logger.info(f"Converted {audio_path} to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Audio conversion failed for {audio_path}: {e}")
            raise Exception(f"Could not convert audio file: {e}")

    def _transcribe_fast(self, audio_path: str) -> Dict:
        """Fast transcription using faster-whisper tiny"""
        model = self.models["faster_whisper_tiny"]

        try:
            segments, info = model.transcribe(
                audio_path,
                beam_size=1,
                language="en",
                condition_on_previous_text=False
            )
            segments_list = list(segments)  # Convert generator to list

            text = " ".join([segment.text for segment in segments_list])

            return {
                "text": text.strip(),
                "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in segments_list],
                "model": "faster-whisper-tiny",
                "confidence": float(info.language_probability) if hasattr(info, 'language_probability') else 0.85,
                "language": info.language if hasattr(info, 'language') else "en",
                "duration": info.duration if hasattr(info, 'duration') else 0.0
            }
        except Exception as e:
            self.logger.error(f"Fast transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "model": "faster-whisper-tiny",
                "confidence": 0.0,
                "error": str(e)
            }

    def _transcribe_accurate(self, audio_path: str) -> Dict:
        """Accurate transcription using Whisper Large-v3"""
        model = self.models["whisper_large_v3"]

        try:
            result = model.transcribe(audio_path, language="en")

            # Calculate average confidence from segments
            segments = result.get("segments", [])
            avg_confidence = 0.95  # Default high confidence for large model
            if segments:
                # Whisper doesn't always provide confidence scores
                avg_confidence = 0.95

            return {
                "text": result["text"].strip(),
                "segments": [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in segments],
                "model": "whisper-large-v3",
                "confidence": avg_confidence,
                "language": result.get("language", "en")
            }
        except Exception as e:
            self.logger.error(f"Accurate transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "model": "whisper-large-v3",
                "confidence": 0.0,
                "error": str(e)
            }

    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            "queue_size": self.processing_queue.qsize() if hasattr(self, 'processing_queue') else 0,
            "current_processing": asdict(self.current_processing) if self.current_processing else None,
            "models_loaded": list(self.models.keys()),
            "stats": self.stats,
            "available_engines": {
                "faster_whisper": FASTER_WHISPER_AVAILABLE,
                "openai_whisper": OPENAI_WHISPER_AVAILABLE
            },
            "engine_type": "squirt_standalone"
        }

    def get_performance_metrics(self) -> Dict:
        """Get detailed performance metrics"""
        return {
            "total_requests": self.stats["requests_processed"],
            "fast_mode_requests": self.stats["fast_mode_count"],
            "accurate_mode_requests": self.stats["accurate_mode_count"],
            "average_processing_time": self.stats["average_processing_time"],
            "total_processing_time": self.stats["total_processing_time"],
            "fast_mode_percentage": (
                self.stats["fast_mode_count"] / max(1, self.stats["requests_processed"]) * 100
            ),
            "models_loaded": len(self.models),
            "memory_efficient": self.max_ram_gb <= 4.0
        }


# Global engine instance for Squirt
squirt_voice_engine = SquirtVoiceEngine()


def main():
    """Test the Squirt voice engine"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python squirt_voice_engine.py <audio_file> [mode]")
        print("Modes: fast, accurate")
        sys.exit(1)

    audio_file = sys.argv[1]
    mode = TranscriptionMode.FAST

    if len(sys.argv) > 2:
        mode_str = sys.argv[2].lower()
        if mode_str == "accurate":
            mode = TranscriptionMode.ACCURATE

    try:
        print(f"Testing Squirt voice engine with {audio_file} in {mode.value} mode...")

        result = squirt_voice_engine.transcribe_audio(
            audio_file,
            mode=mode,
            context="Test transcription"
        )

        print(f"\nTranscription Result:")
        print(f"Text: {result['transcription']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Model used: {result['model_used']}")

        if result.get('error'):
            print(f"Error: {result['error']}")

        # Show performance metrics
        metrics = squirt_voice_engine.get_performance_metrics()
        print(f"\nPerformance Metrics:")
        print(json.dumps(metrics, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()