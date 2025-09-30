#!/usr/bin/env python3
"""
Multi-Input Processing System
Handles voice memos, paper worksheets, SMS, and manual corrections in unified workflow
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import logging

# Import Squirt modules
try:
    from voice_document_processor import VoiceDocumentProcessor, VOICE_ENGINE_AVAILABLE
    from enhanced_voice_extractor import EnhancedVoiceExtractor
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    VOICE_ENGINE_AVAILABLE = False


@dataclass
class InputSource:
    """Represents a single input source"""
    source_type: str  # "voice", "paper", "sms", "manual"
    content: str
    file_path: Optional[str] = None
    timestamp: Optional[str] = None
    employee: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessingResult:
    """Result of multi-input processing"""
    success: bool
    merged_data: Dict[str, Any]
    input_sources: List[InputSource]
    conflicts: List[Dict[str, Any]]
    warnings: List[str]
    confidence_score: float
    processing_time: float


class ConflictResolver:
    """Resolves conflicts between different input sources"""

    def __init__(self):
        # Priority order for different source types
        self.source_priority = {
            "manual": 1.0,      # Highest priority - human input
            "voice": 0.8,       # High priority - recent voice memo
            "sms": 0.6,         # Medium priority - text message
            "paper": 0.4        # Lower priority - OCR may have errors
        }

        # Field-specific resolution strategies
        self.field_strategies = {
            "client_name": "highest_confidence",
            "property_address": "highest_confidence",
            "contact_phone": "most_recent",
            "contact_email": "most_recent",
            "estimated_amount": "manual_override",
            "project_description": "merge_descriptions",
            "urgency": "highest_priority"
        }

    def resolve_conflicts(self, input_sources: List[InputSource]) -> Dict[str, Any]:
        """Resolve conflicts between multiple input sources"""

        if not input_sources:
            return {}

        # Extract data from each source
        source_data = []
        for source in input_sources:
            if source.source_type == "voice":
                # Use enhanced extractor for voice
                extractor = EnhancedVoiceExtractor()
                data = extractor.extract_data(source.content)
                data["_source"] = source
            else:
                # For other sources, parse content based on type
                data = self._parse_source_content(source)
                data["_source"] = source

            source_data.append(data)

        # Merge data with conflict resolution
        merged = {}
        conflicts = []

        # Get all unique fields across sources
        all_fields = set()
        for data in source_data:
            all_fields.update(data.keys())

        all_fields.discard("_source")  # Don't merge internal field

        # Resolve each field
        for field in all_fields:
            values = []
            sources = []

            for data in source_data:
                if field in data and data[field] is not None:
                    values.append(data[field])
                    sources.append(data["_source"])

            if not values:
                continue
            elif len(values) == 1:
                merged[field] = values[0]
            else:
                # Multiple values - resolve conflict
                resolved_value, conflict_info = self._resolve_field_conflict(
                    field, values, sources
                )
                merged[field] = resolved_value

                if conflict_info:
                    conflicts.append(conflict_info)

        return merged, conflicts

    def _resolve_field_conflict(self, field: str, values: List[Any], sources: List[InputSource]) -> tuple:
        """Resolve conflict for a specific field"""

        strategy = self.field_strategies.get(field, "highest_confidence")

        if strategy == "highest_confidence":
            # Use value from source with highest confidence
            best_idx = max(range(len(sources)), key=lambda i: sources[i].confidence)
            return values[best_idx], None

        elif strategy == "highest_priority":
            # Use value from highest priority source type
            best_idx = max(range(len(sources)),
                         key=lambda i: self.source_priority.get(sources[i].source_type, 0))
            return values[best_idx], None

        elif strategy == "most_recent":
            # Use value from most recent source
            best_idx = max(range(len(sources)),
                         key=lambda i: sources[i].timestamp)
            return values[best_idx], None

        elif strategy == "manual_override":
            # Prefer manual input, otherwise highest confidence
            manual_sources = [i for i, s in enumerate(sources) if s.source_type == "manual"]
            if manual_sources:
                return values[manual_sources[0]], None
            else:
                return self._resolve_field_conflict(field, values, sources)[0], {
                    "field": field,
                    "values": values,
                    "resolution": "no_manual_override",
                    "note": "Multiple values found, manual verification recommended"
                }

        elif strategy == "merge_descriptions":
            # Merge project descriptions intelligently
            merged_desc = self._merge_descriptions(values)
            return merged_desc, None

        else:
            # Default: use first value and flag conflict
            return values[0], {
                "field": field,
                "values": values,
                "resolution": "first_value_used",
                "note": f"Multiple {field} values found - used first, please verify"
            }

    def _merge_descriptions(self, descriptions: List[str]) -> str:
        """Merge multiple project descriptions intelligently"""
        if not descriptions:
            return ""

        if len(descriptions) == 1:
            return descriptions[0]

        # Remove duplicates while preserving order
        unique_parts = []
        seen = set()

        for desc in descriptions:
            if desc and desc.strip():
                cleaned = desc.strip().lower()
                if cleaned not in seen:
                    unique_parts.append(desc.strip())
                    seen.add(cleaned)

        return "; ".join(unique_parts)

    def _parse_source_content(self, source: InputSource) -> Dict[str, Any]:
        """Parse content based on source type"""

        if source.source_type == "manual":
            # Manual input is already structured JSON
            try:
                return json.loads(source.content)
            except json.JSONDecodeError:
                # Treat as plain text description
                return {"project_description": source.content}

        elif source.source_type == "sms":
            # Parse SMS-like text input
            return self._parse_sms_content(source.content)

        elif source.source_type == "paper":
            # Parse OCR'd paper content
            return self._parse_paper_content(source.content)

        else:
            # Unknown source type - treat as description
            return {"project_description": source.content}

    def _parse_sms_content(self, content: str) -> Dict[str, Any]:
        """Parse SMS content for key information"""
        data = {}

        # Simple patterns for SMS parsing
        lines = content.split('\n')
        for line in lines:
            line = line.strip()

            # Name patterns
            if line.lower().startswith(('client:', 'name:', 'customer:')):
                data["client_name"] = line.split(':', 1)[1].strip()

            # Address patterns
            elif line.lower().startswith(('address:', 'location:', 'at:')):
                data["property_address"] = line.split(':', 1)[1].strip()

            # Service patterns
            elif line.lower().startswith(('service:', 'work:', 'job:')):
                data["project_description"] = line.split(':', 1)[1].strip()

            # Phone patterns
            elif line.lower().startswith('phone:'):
                data["contact_phone"] = line.split(':', 1)[1].strip()

            # Amount patterns
            elif '$' in line or 'amount' in line.lower():
                import re
                amount_match = re.search(r'\$?([0-9,]+(?:\.[0-9]{2})?)', line)
                if amount_match:
                    try:
                        data["estimated_amount"] = float(amount_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

        # If no structured data found, treat entire content as description
        if not data:
            data["project_description"] = content

        return data

    def _parse_paper_content(self, content: str) -> Dict[str, Any]:
        """Parse OCR'd paper worksheet content"""
        # Similar to SMS parsing but with OCR error tolerance
        data = self._parse_sms_content(content)

        # OCR often has lower confidence
        data["_ocr_source"] = True

        return data


class MultiInputProcessor:
    """Main processor for handling multiple input types"""

    def __init__(self):
        self.voice_processor = None
        self.conflict_resolver = ConflictResolver()
        self.logger = logging.getLogger(__name__)

        # Initialize voice processor if available
        if VOICE_ENGINE_AVAILABLE:
            try:
                self.voice_processor = VoiceDocumentProcessor()
                self.logger.info("Voice processor initialized")
            except Exception as e:
                self.logger.warning(f"Voice processor failed to initialize: {e}")
                self.voice_processor = None

    def process_multiple_inputs(self,
                               input_sources: List[InputSource],
                               template_type: str = "estimate") -> ProcessingResult:
        """
        Process multiple input sources into unified document data

        Args:
            input_sources: List of input sources to process
            template_type: Type of template to generate

        Returns:
            ProcessingResult with merged data and conflicts
        """
        start_time = datetime.now()
        warnings = []
        all_sources = []

        try:
            # Process each input source
            for source in input_sources:
                processed_source = self._process_single_source(source)
                all_sources.append(processed_source)

            # Resolve conflicts and merge data
            merged_data, conflicts = self.conflict_resolver.resolve_conflicts(all_sources)

            # Add processing metadata
            merged_data["multi_input_processing"] = {
                "timestamp": datetime.now().isoformat(),
                "source_count": len(all_sources),
                "conflict_count": len(conflicts),
                "template_type": template_type
            }

            # Calculate overall confidence
            if all_sources:
                total_confidence = sum(source.confidence for source in all_sources)
                avg_confidence = total_confidence / len(all_sources)
            else:
                avg_confidence = 0.0

            # Add warnings for conflicts
            if conflicts:
                warnings.append(f"{len(conflicts)} data conflicts found - review recommended")

            # Validate required fields
            required_fields = ["client_name", "project_description"]
            missing_fields = [field for field in required_fields if not merged_data.get(field)]

            if missing_fields:
                warnings.append(f"Missing required fields: {', '.join(missing_fields)}")

            processing_time = (datetime.now() - start_time).total_seconds()

            return ProcessingResult(
                success=True,
                merged_data=merged_data,
                input_sources=all_sources,
                conflicts=conflicts,
                warnings=warnings,
                confidence_score=avg_confidence,
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Multi-input processing failed: {e}")

            return ProcessingResult(
                success=False,
                merged_data={},
                input_sources=input_sources,
                conflicts=[],
                warnings=[f"Processing failed: {e}"],
                confidence_score=0.0,
                processing_time=processing_time
            )

    def _process_single_source(self, source: InputSource) -> InputSource:
        """Process a single input source and update its confidence"""

        if source.source_type == "voice" and self.voice_processor:
            try:
                # Process voice file
                voice_result = self.voice_processor.process_voice_memo(
                    source.file_path,
                    mode="fast",  # Use fast mode for multi-input to save time
                    employee_name=source.employee
                )

                source.confidence = voice_result.confidence
                source.content = voice_result.transcription
                source.metadata.update({
                    "processing_time": voice_result.processing_time,
                    "mode": voice_result.mode_used,
                    "extracted_data": voice_result.extracted_data
                })

            except Exception as e:
                self.logger.warning(f"Voice processing failed for {source.file_path}: {e}")
                source.confidence = 0.1  # Low confidence for failed voice processing
                source.metadata["error"] = str(e)

        elif source.source_type == "paper":
            # OCR typically has lower confidence
            source.confidence = 0.6

        elif source.source_type == "sms":
            # SMS is usually accurate but brief
            source.confidence = 0.8

        elif source.source_type == "manual":
            # Manual input has highest confidence
            source.confidence = 1.0

        return source

    def create_interactive_correction_session(self,
                                            processing_result: ProcessingResult) -> Dict[str, Any]:
        """
        Create interactive session for manual corrections

        Args:
            processing_result: Result from multi-input processing

        Returns:
            Corrected data dictionary
        """

        if not processing_result.success:
            print("❌ Cannot create correction session - processing failed")
            return {}

        print(f"\n🔧 Multi-Input Review Session")
        print(f"📊 Processed {len(processing_result.input_sources)} input sources")
        print(f"⚠️ Found {len(processing_result.conflicts)} conflicts")
        print(f"🎯 Overall confidence: {processing_result.confidence_score:.2f}")

        merged = processing_result.merged_data.copy()

        # Show conflicts first
        if processing_result.conflicts:
            print(f"\n⚠️ Data Conflicts Found:")
            for i, conflict in enumerate(processing_result.conflicts, 1):
                print(f"   {i}. {conflict['field']}: {conflict['note']}")
                if "values" in conflict:
                    for j, value in enumerate(conflict["values"]):
                        print(f"      Option {j+1}: {value}")

        # Interactive review of key fields
        print(f"\n📝 Field Review (press Enter to keep current value):")

        key_fields = [
            ("client_name", "Client Name"),
            ("property_address", "Property Address"),
            ("project_description", "Project Description"),
            ("contact_phone", "Contact Phone"),
            ("estimated_amount", "Estimated Amount"),
            ("urgency", "Urgency Level")
        ]

        for field, display_name in key_fields:
            current_value = merged.get(field, "")

            if field == "estimated_amount" and current_value:
                display_value = f"${current_value:,.2f}"
            else:
                display_value = str(current_value)

            user_input = input(f"   {display_name} [{display_value}]: ").strip()

            if user_input:
                if field == "estimated_amount":
                    try:
                        merged[field] = float(user_input.replace('$', '').replace(',', ''))
                    except ValueError:
                        print("     ⚠️ Invalid amount format - keeping original")
                else:
                    merged[field] = user_input

        # Add correction metadata
        merged["multi_input_processing"]["manual_corrections"] = {
            "corrected_at": datetime.now().isoformat(),
            "corrected_fields": [field for field, _ in key_fields if input()]
        }

        print(f"\n✅ Corrections applied")
        return merged

    def save_processing_session(self,
                               result: ProcessingResult,
                               output_path: Optional[str] = None) -> str:
        """Save complete processing session for audit trail"""

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/multi_input_session_{timestamp}.json"

        session_data = {
            "session_metadata": {
                "timestamp": datetime.now().isoformat(),
                "success": result.success,
                "processing_time": result.processing_time,
                "confidence_score": result.confidence_score
            },
            "input_sources": [asdict(source) for source in result.input_sources],
            "merged_data": result.merged_data,
            "conflicts": result.conflicts,
            "warnings": result.warnings
        }

        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        return output_path


def main():
    """Command line interface for multi-input processing"""
    import argparse

    parser = argparse.ArgumentParser(description="Process multiple input sources")
    parser.add_argument("--voice", help="Voice memo file path")
    parser.add_argument("--sms", help="SMS text content")
    parser.add_argument("--paper", help="Paper worksheet content file")
    parser.add_argument("--manual", help="Manual input JSON file")
    parser.add_argument("--employee", help="Employee name")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive review")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Build input sources
    sources = []

    if args.voice:
        sources.append(InputSource(
            source_type="voice",
            content="",
            file_path=args.voice,
            employee=args.employee
        ))

    if args.sms:
        sources.append(InputSource(
            source_type="sms",
            content=args.sms,
            employee=args.employee
        ))

    if args.paper:
        with open(args.paper, 'r') as f:
            content = f.read()
        sources.append(InputSource(
            source_type="paper",
            content=content,
            file_path=args.paper,
            employee=args.employee
        ))

    if args.manual:
        with open(args.manual, 'r') as f:
            content = f.read()
        sources.append(InputSource(
            source_type="manual",
            content=content,
            file_path=args.manual,
            employee=args.employee
        ))

    if not sources:
        print("❌ No input sources provided")
        sys.exit(1)

    # Process inputs
    processor = MultiInputProcessor()
    result = processor.process_multiple_inputs(sources)

    if result.success:
        print(f"✅ Multi-input processing successful")
        print(f"📊 Confidence: {result.confidence_score:.2f}")
        print(f"⏱️ Processing time: {result.processing_time:.2f}s")

        if args.interactive:
            corrected_data = processor.create_interactive_correction_session(result)
            final_data = corrected_data
        else:
            final_data = result.merged_data

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(final_data, f, indent=2, default=str)
            print(f"💾 Saved to: {args.output}")
        else:
            print(f"\n📄 Merged Data:")
            print(json.dumps(final_data, indent=2, default=str))

        # Save session audit trail
        session_file = processor.save_processing_session(result)
        print(f"📋 Session saved: {session_file}")

    else:
        print(f"❌ Multi-input processing failed")
        for warning in result.warnings:
            print(f"   {warning}")


if __name__ == "__main__":
    main()