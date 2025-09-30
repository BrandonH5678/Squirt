#!/usr/bin/env python3
"""
Voice-to-Document Bridge Module
Integrates standalone voice processing with Squirt document generation
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
import logging

# Import standalone voice engine
try:
    from voice.squirt_voice_engine import SquirtVoiceEngine, TranscriptionMode, ProcessingPriority
    VOICE_ENGINE_AVAILABLE = True
except ImportError:
    VOICE_ENGINE_AVAILABLE = False
    print("⚠️ Voice engine not available - voice processing disabled")


@dataclass
class VoiceProcessingResult:
    """Result of voice processing with extracted data"""
    transcription: str
    confidence: float
    extracted_data: Dict[str, Any]
    processing_time: float
    mode_used: str
    warnings: List[str]
    needs_review: bool


class VoiceContentExtractor:
    """Extract structured data from voice transcriptions"""

    def __init__(self):
        self.client_patterns = [
            r"(?:client|customer)\s+(?:is\s+)?(.+?)(?:\s+at|\s+lives|\s+in|\.|$)",
            r"for\s+(.+?)(?:\s+at|\s+on|\s+in|\.|$)",
            r"(?:name|client)\s*[:]\s*(.+?)(?:\s+at|\.|$)"
        ]

        self.address_patterns = [
            r"(?:at|address|located at|property at)\s+(.+?)(?:\s+in|\s+for|\.|$)",
            r"(\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard))",
            r"address\s*[:]\s*(.+?)(?:\s+for|\.|$)"
        ]

        self.service_patterns = [
            r"(?:need|needs|want|wants|for|service|work)\s+(.+?)(?:\s+at|\s+for|\s+estimate|\.|$)",
            r"(?:fall cleanup|irrigation|sprinkler|landscape|lawn|garden|maintenance|repair)",
            r"(?:estimate|quote)\s+for\s+(.+?)(?:\s+at|\.|$)"
        ]

        self.amount_patterns = [
            r"\$([0-9,]+(?:\.[0-9]{2})?)",
            r"([0-9,]+)\s*dollars?",
            r"about\s+([0-9,]+)",
            r"roughly\s+([0-9,]+)"
        ]

        self.phone_patterns = [
            r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            r"phone\s*[:]\s*([0-9-().\s]+)"
        ]

    def extract_data(self, transcription: str) -> Dict[str, Any]:
        """Extract structured data from voice transcription"""
        extracted = {
            "client_name": None,
            "property_address": None,
            "project_description": None,
            "estimated_amount": None,
            "contact_phone": None,
            "service_type": None,
            "urgency": "normal",
            "confidence_scores": {}
        }

        text = transcription.lower().strip()

        # Extract client name
        client = self._extract_with_patterns(text, self.client_patterns)
        if client:
            extracted["client_name"] = self._clean_name(client)
            extracted["confidence_scores"]["client_name"] = 0.8

        # Extract address
        address = self._extract_with_patterns(text, self.address_patterns)
        if address:
            extracted["property_address"] = self._clean_address(address)
            extracted["confidence_scores"]["property_address"] = 0.7

        # Extract service type
        service = self._extract_with_patterns(text, self.service_patterns)
        if service:
            extracted["service_type"] = self._categorize_service(service)
            extracted["project_description"] = service.strip()
            extracted["confidence_scores"]["service_type"] = 0.9

        # Extract amount
        amount = self._extract_with_patterns(text, self.amount_patterns)
        if amount:
            extracted["estimated_amount"] = self._parse_amount(amount)
            extracted["confidence_scores"]["estimated_amount"] = 0.6

        # Extract phone
        phone = self._extract_with_patterns(text, self.phone_patterns)
        if phone:
            extracted["contact_phone"] = self._clean_phone(phone)
            extracted["confidence_scores"]["contact_phone"] = 0.8

        # Detect urgency
        if any(word in text for word in ["urgent", "asap", "emergency", "immediately", "today"]):
            extracted["urgency"] = "high"
        elif any(word in text for word in ["soon", "quick", "this week"]):
            extracted["urgency"] = "medium"

        return extracted

    def _extract_with_patterns(self, text: str, patterns: List[str]) -> Optional[str]:
        """Try multiple regex patterns to extract information"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _clean_name(self, name: str) -> str:
        """Clean and format client name"""
        name = re.sub(r'\s+', ' ', name.strip())
        return ' '.join(word.capitalize() for word in name.split())

    def _clean_address(self, address: str) -> str:
        """Clean and format address"""
        address = re.sub(r'\s+', ' ', address.strip())
        return address.title()

    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number"""
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            return float(amount_str.replace(',', ''))
        except ValueError:
            return 0.0

    def _categorize_service(self, service: str) -> str:
        """Categorize service type based on keywords"""
        service_lower = service.lower()

        if any(word in service_lower for word in ["fall", "cleanup", "leaf", "debris"]):
            return "cleanup"
        elif any(word in service_lower for word in ["irrigation", "sprinkler", "water"]):
            return "irrigation_repair"
        elif any(word in service_lower for word in ["landscape", "plant", "garden"]):
            return "planting"
        elif any(word in service_lower for word in ["maintenance", "trim", "prune"]):
            return "maintenance"
        elif any(word in service_lower for word in ["drainage", "drain"]):
            return "drainage"
        else:
            return "maintenance"  # default


class VoiceDocumentProcessor:
    """Main class for processing voice memos into documents"""

    def __init__(self):
        self.voice_engine = None
        self.extractor = VoiceContentExtractor()
        self.thermal_monitor = None

        # Initialize voice engine if available
        if VOICE_ENGINE_AVAILABLE:
            try:
                self.voice_engine = SquirtVoiceEngine()
                print("✅ Voice engine initialized successfully")
            except Exception as e:
                print(f"⚠️ Voice engine initialization failed: {e}")
                self.voice_engine = None

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def process_voice_memo(self,
                          audio_file: str,
                          mode: str = "fast",
                          employee_name: Optional[str] = None,
                          project_context: Optional[str] = None) -> VoiceProcessingResult:
        """
        Process voice memo into structured document data

        Args:
            audio_file: Path to audio file
            mode: "fast" or "accurate" processing
            employee_name: Employee who recorded the memo
            project_context: Additional context about the project

        Returns:
            VoiceProcessingResult with extracted data
        """

        if not self.voice_engine:
            raise RuntimeError("Voice engine not available")

        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        start_time = time.time()
        warnings = []

        # Check thermal constraints
        if not self._check_thermal_safety():
            warnings.append("High system temperature - using fast mode only")
            mode = "fast"

        # Process voice memo
        try:
            transcription_mode = TranscriptionMode.FAST if mode.lower() == "fast" else TranscriptionMode.ACCURATE
            priority = ProcessingPriority.BUSINESS if self._is_business_hours() else ProcessingPriority.BACKGROUND

            result = self.voice_engine.transcribe_audio(
                audio_file,
                mode=transcription_mode,
                priority=priority,
                context=project_context
            )

            transcription = result.get("transcription", "")
            confidence = result.get("confidence", 0.0)

        except Exception as e:
            self.logger.error(f"Voice transcription failed: {e}")
            raise RuntimeError(f"Voice processing failed: {e}")

        # Extract structured data
        extracted_data = self.extractor.extract_data(transcription)

        # Add metadata
        extracted_data["employee_name"] = employee_name
        extracted_data["processing_date"] = datetime.now().isoformat()
        extracted_data["audio_file"] = str(Path(audio_file).name)
        extracted_data["project_context"] = project_context

        # Determine if human review is needed
        needs_review = self._needs_human_review(extracted_data, confidence)
        if needs_review:
            warnings.append("Human review recommended - low confidence or missing critical data")

        processing_time = time.time() - start_time

        return VoiceProcessingResult(
            transcription=transcription,
            confidence=confidence,
            extracted_data=extracted_data,
            processing_time=processing_time,
            mode_used=mode,
            warnings=warnings,
            needs_review=needs_review
        )

    def generate_input_json(self, voice_result: VoiceProcessingResult, template_type: str = "estimate") -> Dict[str, Any]:
        """
        Generate Squirt input JSON from voice processing result

        Args:
            voice_result: Result from voice processing
            template_type: Type of document template to use

        Returns:
            JSON structure for Squirt document generation
        """

        extracted = voice_result.extracted_data

        # Base client and project info
        input_data = {
            "client_name": extracted.get("client_name", "Unknown Client"),
            "property_address": extracted.get("property_address", "Address needed"),
            "estimate_date": datetime.now().strftime("%Y-%m-%d"),
            "project_description": extracted.get("project_description", "Voice memo estimate"),
            "contact_info": {
                "phone": extracted.get("contact_phone", "Phone needed"),
                "email": "Email needed"
            },
            "company_info": {
                "name": "WaterWizard Irrigation & Landscape",
                "license": "CCB #12345",
                "phone": "(503) 555-0199",
                "email": "info@waterwizard.com"
            },
            "voice_processing": {
                "transcription": voice_result.transcription,
                "confidence": voice_result.confidence,
                "processing_mode": voice_result.mode_used,
                "processing_time": voice_result.processing_time,
                "employee": extracted.get("employee_name"),
                "needs_review": voice_result.needs_review,
                "warnings": voice_result.warnings
            }
        }

        # Add template-specific parameters based on service type
        service_type = extracted.get("service_type", "maintenance")
        if service_type == "cleanup":
            input_data["parameters"] = {
                "property_size": 0.25,  # Default 1/4 acre
                "debris_level": "medium",
                "access_difficulty": "normal"
            }
        elif service_type == "irrigation_repair":
            input_data["parameters"] = {
                "num_zones": 6,  # Default
                "repair_complexity": "standard"
            }
        else:
            input_data["parameters"] = {
                "project_scope": "standard",
                "estimated_hours": 4
            }

        # Add estimated amount if provided
        if extracted.get("estimated_amount"):
            input_data["target_amount"] = extracted["estimated_amount"]

        return input_data

    def _check_thermal_safety(self) -> bool:
        """Check if system temperature is safe for voice processing"""
        try:
            import subprocess
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "Package id 0" in result.stdout:
                temp_line = [line for line in result.stdout.split('\n') if "Package id 0" in line][0]
                temp_match = re.search(r'\+(\d+)\.\d+°C', temp_line)
                if temp_match:
                    temp = int(temp_match.group(1))
                    return temp < 80  # Safe under 80°C

            return True  # Assume safe if can't check

        except Exception:
            return True  # Assume safe if check fails

    def _is_business_hours(self) -> bool:
        """Check if current time is business hours (6am-7pm Mon-Fri)"""
        now = datetime.now()
        is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
        is_business_time = 6 <= now.hour < 19
        return is_weekday and is_business_time

    def _needs_human_review(self, extracted_data: Dict[str, Any], confidence: float) -> bool:
        """Determine if human review is needed"""

        # Low overall confidence
        if confidence < 0.7:
            return True

        # Missing critical data
        critical_fields = ["client_name", "project_description"]
        for field in critical_fields:
            if not extracted_data.get(field) or extracted_data[field] in ["Unknown Client", "Address needed"]:
                return True

        # Low confidence on key fields
        confidence_scores = extracted_data.get("confidence_scores", {})
        for field, score in confidence_scores.items():
            if field in critical_fields and score < 0.6:
                return True

        return False


def main():
    """Command line interface for voice document processing"""
    import argparse

    parser = argparse.ArgumentParser(description="Process voice memo into document data")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast",
                       help="Processing mode")
    parser.add_argument("--employee", help="Employee name")
    parser.add_argument("--context", help="Project context")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--template", default="estimate", help="Template type")

    args = parser.parse_args()

    if not VOICE_ENGINE_AVAILABLE:
        print("❌ Voice engine not available")
        sys.exit(1)

    processor = VoiceDocumentProcessor()

    try:
        print(f"🎙️ Processing voice memo: {args.audio_file}")
        print(f"📊 Mode: {args.mode}")

        # Process voice memo
        result = processor.process_voice_memo(
            args.audio_file,
            mode=args.mode,
            employee_name=args.employee,
            project_context=args.context
        )

        print(f"✅ Transcription completed in {result.processing_time:.1f}s")
        print(f"📝 Confidence: {result.confidence:.2f}")

        if result.warnings:
            for warning in result.warnings:
                print(f"⚠️ {warning}")

        # Generate input JSON
        input_json = processor.generate_input_json(result, args.template)

        # Save or display result
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(input_json, f, indent=2)
            print(f"💾 Saved to: {args.output}")
        else:
            print("\n📄 Generated Input JSON:")
            print(json.dumps(input_json, indent=2))

        if result.needs_review:
            print("\n🔍 HUMAN REVIEW RECOMMENDED")
            print("Please verify extracted data before document generation")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()