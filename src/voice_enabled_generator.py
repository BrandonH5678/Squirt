#!/usr/bin/env python3
"""
Voice-Enabled Document Generator
Extends existing UNO generators with voice input capabilities
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

# Import existing Squirt modules
try:
    from uno_estimate_generator import UnoEstimateGenerator
    from uno_invoice_generator import UnoInvoiceGenerator
    from voice_document_processor import VoiceDocumentProcessor, VOICE_ENGINE_AVAILABLE
    from vision_validator import VisionValidator
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Make sure you're running from the Squirt src/ directory")
    sys.exit(1)


class VoiceEnabledEstimateGenerator:
    """Voice-enabled estimate generator combining voice processing with document generation"""

    def __init__(self):
        self.voice_processor = None
        self.document_generator = UnoEstimateGenerator()
        self.vision_validator = VisionValidator()

        # Initialize voice processor if available
        if VOICE_ENGINE_AVAILABLE:
            try:
                self.voice_processor = VoiceDocumentProcessor()
                print("✅ Voice processing enabled")
            except Exception as e:
                print(f"⚠️ Voice processor initialization failed: {e}")
                self.voice_processor = None
        else:
            print("⚠️ Voice processing not available")

    def generate_from_voice(self,
                           audio_file: str,
                           template_path: str,
                           mode: str = "fast",
                           employee_name: Optional[str] = None,
                           manual_corrections: Optional[Dict[str, Any]] = None,
                           skip_visual_validation: bool = False) -> Dict[str, Any]:
        """
        Generate document from voice memo

        Args:
            audio_file: Path to voice memo audio file
            template_path: Path to JSON template file
            mode: "fast" or "accurate" voice processing
            employee_name: Name of employee who recorded memo
            manual_corrections: Manual corrections to apply to extracted data
            skip_visual_validation: Skip visual validation (for batch processing)

        Returns:
            Generation result with paths and validation info
        """

        if not self.voice_processor:
            raise RuntimeError("Voice processing not available")

        result = {
            "success": False,
            "voice_result": None,
            "input_json_path": None,
            "generated_files": [],
            "validation_result": None,
            "warnings": [],
            "errors": []
        }

        try:
            print(f"🎙️ Processing voice memo: {Path(audio_file).name}")

            # Step 1: Process voice memo
            voice_result = self.voice_processor.process_voice_memo(
                audio_file=audio_file,
                mode=mode,
                employee_name=employee_name,
                project_context="Estimate generation"
            )

            result["voice_result"] = voice_result
            result["warnings"].extend(voice_result.warnings)

            print(f"✅ Voice processing completed in {voice_result.processing_time:.1f}s")
            print(f"📊 Confidence: {voice_result.confidence:.2f}")

            # Step 2: Generate input JSON from voice data
            input_data = self.voice_processor.generate_input_json(voice_result, "estimate")

            # Step 3: Apply manual corrections if provided
            if manual_corrections:
                print("✏️ Applying manual corrections...")
                input_data = self._apply_corrections(input_data, manual_corrections)

            # Step 4: Save input JSON to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(input_data, f, indent=2)
                input_json_path = f.name

            result["input_json_path"] = input_json_path

            print(f"📄 Generated input JSON: {input_json_path}")

            # Step 5: Generate document using existing UNO generator
            if not self.document_generator.load_files(template_path, input_json_path):
                result["errors"].append("Failed to load template or input files")
                return result

            print("🔧 Generating document...")
            generation_success = self.document_generator.generate()

            if generation_success:
                generated_files = self.document_generator.get_output_files()
                result["generated_files"] = generated_files
                print(f"✅ Document generated: {len(generated_files)} files")

                # Step 6: Visual validation (if not skipped)
                if not skip_visual_validation and generated_files:
                    print("📸 Performing visual validation...")
                    try:
                        validation_result = self._perform_visual_validation(generated_files)
                        result["validation_result"] = validation_result

                        if validation_result.get("errors"):
                            result["warnings"].append("Visual validation found issues")

                    except Exception as e:
                        result["warnings"].append(f"Visual validation failed: {e}")

                result["success"] = True

            else:
                result["errors"].append("Document generation failed")

        except Exception as e:
            result["errors"].append(str(e))
            print(f"❌ Error: {e}")

        return result

    def generate_with_review(self,
                            audio_file: str,
                            template_path: str,
                            mode: str = "fast",
                            employee_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate document with interactive review process for extracted data

        Args:
            audio_file: Path to voice memo
            template_path: Path to template
            mode: Voice processing mode
            employee_name: Employee name

        Returns:
            Generation result after review
        """

        if not self.voice_processor:
            raise RuntimeError("Voice processing not available")

        print(f"🎙️ Processing voice memo with review: {Path(audio_file).name}")

        # Process voice memo
        voice_result = self.voice_processor.process_voice_memo(
            audio_file=audio_file,
            mode=mode,
            employee_name=employee_name,
            project_context="Estimate with review"
        )

        print(f"\n📝 Transcription:")
        print(f"   {voice_result.transcription}")
        print(f"\n📊 Confidence: {voice_result.confidence:.2f}")

        # Display extracted data
        extracted = voice_result.extracted_data
        print(f"\n🔍 Extracted Data:")
        print(f"   Client: {extracted.get('client_name', 'Not found')}")
        print(f"   Address: {extracted.get('property_address', 'Not found')}")
        print(f"   Service: {extracted.get('project_description', 'Not found')}")
        print(f"   Phone: {extracted.get('contact_phone', 'Not found')}")
        print(f"   Amount: ${extracted.get('estimated_amount', 0):,.2f}" if extracted.get('estimated_amount') else "   Amount: Not specified")

        # Interactive review
        corrections = {}
        print(f"\n🔧 Review and Corrections:")
        print("Press Enter to keep current value, or type new value")

        # Review key fields
        corrections["client_name"] = self._get_user_input(
            "Client name",
            extracted.get('client_name', '')
        )

        corrections["property_address"] = self._get_user_input(
            "Property address",
            extracted.get('property_address', '')
        )

        corrections["project_description"] = self._get_user_input(
            "Project description",
            extracted.get('project_description', '')
        )

        corrections["contact_phone"] = self._get_user_input(
            "Contact phone",
            extracted.get('contact_phone', '')
        )

        # Remove empty corrections
        corrections = {k: v for k, v in corrections.items() if v.strip()}

        # Generate with corrections
        return self.generate_from_voice(
            audio_file=audio_file,
            template_path=template_path,
            mode=mode,
            employee_name=employee_name,
            manual_corrections=corrections,
            skip_visual_validation=False
        )

    def _apply_corrections(self, input_data: Dict[str, Any], corrections: Dict[str, Any]) -> Dict[str, Any]:
        """Apply manual corrections to input data"""

        corrected_data = input_data.copy()

        # Apply direct field corrections
        for field, value in corrections.items():
            if field in ["client_name", "property_address", "project_description"]:
                corrected_data[field] = value
            elif field == "contact_phone" and "contact_info" in corrected_data:
                corrected_data["contact_info"]["phone"] = value
            elif field == "contact_email" and "contact_info" in corrected_data:
                corrected_data["contact_info"]["email"] = value

        # Update voice processing metadata to note corrections
        if "voice_processing" in corrected_data:
            corrected_data["voice_processing"]["manual_corrections"] = corrections
            corrected_data["voice_processing"]["corrected_at"] = datetime.now().isoformat()

        return corrected_data

    def _perform_visual_validation(self, generated_files: list) -> Dict[str, Any]:
        """Perform visual validation on generated documents"""

        validation_result = {
            "validated_files": [],
            "issues_found": [],
            "overall_score": 0.0,
            "errors": []
        }

        # Find PDF files for validation
        pdf_files = [f for f in generated_files if f.endswith('.pdf')]

        if not pdf_files:
            validation_result["errors"].append("No PDF files found for validation")
            return validation_result

        try:
            for pdf_file in pdf_files:
                print(f"🔍 Validating: {Path(pdf_file).name}")

                # Use existing vision validator
                file_validation = self.vision_validator.validate_document(pdf_file)

                validation_result["validated_files"].append({
                    "file": pdf_file,
                    "result": file_validation
                })

                if file_validation.get("issues"):
                    validation_result["issues_found"].extend(file_validation["issues"])

                # Track overall score (average of all files)
                if "score" in file_validation:
                    validation_result["overall_score"] += file_validation["score"]

            # Calculate average score
            if validation_result["validated_files"]:
                validation_result["overall_score"] /= len(validation_result["validated_files"])

        except Exception as e:
            validation_result["errors"].append(f"Validation error: {e}")

        return validation_result

    def _get_user_input(self, field_name: str, current_value: str) -> str:
        """Get user input for field correction"""
        prompt = f"{field_name} [{current_value}]: "
        user_input = input(prompt).strip()
        return user_input if user_input else current_value


class VoiceEnabledInvoiceGenerator:
    """Voice-enabled invoice generator"""

    def __init__(self):
        self.voice_processor = None
        self.document_generator = UnoInvoiceGenerator()
        self.vision_validator = VisionValidator()

        # Initialize voice processor if available
        if VOICE_ENGINE_AVAILABLE:
            try:
                self.voice_processor = VoiceDocumentProcessor()
                print("✅ Voice processing enabled for invoices")
            except Exception as e:
                print(f"⚠️ Voice processor initialization failed: {e}")
                self.voice_processor = None

    def generate_from_voice(self,
                           audio_file: str,
                           template_path: str,
                           mode: str = "fast",
                           employee_name: Optional[str] = None,
                           manual_corrections: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate invoice from voice memo - similar to estimate generator"""

        if not self.voice_processor:
            raise RuntimeError("Voice processing not available")

        # Process voice for invoice context
        voice_result = self.voice_processor.process_voice_memo(
            audio_file=audio_file,
            mode=mode,
            employee_name=employee_name,
            project_context="Invoice generation"
        )

        # Generate input JSON for invoice
        input_data = self.voice_processor.generate_input_json(voice_result, "invoice")

        # Apply corrections if provided
        if manual_corrections:
            input_data = self._apply_corrections(input_data, manual_corrections)

        # Use existing invoice generator
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(input_data, f, indent=2)
            input_json_path = f.name

        if self.document_generator.load_files(template_path, input_json_path):
            success = self.document_generator.generate()
            if success:
                return {
                    "success": True,
                    "voice_result": voice_result,
                    "generated_files": self.document_generator.get_output_files(),
                    "input_json_path": input_json_path
                }

        return {"success": False, "voice_result": voice_result}

    def _apply_corrections(self, input_data: Dict[str, Any], corrections: Dict[str, Any]) -> Dict[str, Any]:
        """Apply manual corrections - same as estimate generator"""
        corrected_data = input_data.copy()

        for field, value in corrections.items():
            if field in ["client_name", "property_address", "project_description"]:
                corrected_data[field] = value
            elif field == "contact_phone" and "contact_info" in corrected_data:
                corrected_data["contact_info"]["phone"] = value

        if "voice_processing" in corrected_data:
            corrected_data["voice_processing"]["manual_corrections"] = corrections

        return corrected_data


def main():
    """Command line interface for voice-enabled document generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate documents from voice memos")
    parser.add_argument("audio_file", help="Path to voice memo audio file")
    parser.add_argument("template", help="Path to JSON template file")
    parser.add_argument("--type", choices=["estimate", "invoice"], default="estimate",
                       help="Document type to generate")
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast",
                       help="Voice processing mode")
    parser.add_argument("--employee", help="Employee name")
    parser.add_argument("--review", action="store_true",
                       help="Enable interactive review of extracted data")
    parser.add_argument("--output-dir", help="Output directory for generated files")

    args = parser.parse_args()

    if not VOICE_ENGINE_AVAILABLE:
        print("❌ Voice engine not available")
        sys.exit(1)

    try:
        if args.type == "estimate":
            generator = VoiceEnabledEstimateGenerator()

            if args.review:
                result = generator.generate_with_review(
                    audio_file=args.audio_file,
                    template_path=args.template,
                    mode=args.mode,
                    employee_name=args.employee
                )
            else:
                result = generator.generate_from_voice(
                    audio_file=args.audio_file,
                    template_path=args.template,
                    mode=args.mode,
                    employee_name=args.employee
                )

        else:  # invoice
            generator = VoiceEnabledInvoiceGenerator()
            result = generator.generate_from_voice(
                audio_file=args.audio_file,
                template_path=args.template,
                mode=args.mode,
                employee_name=args.employee
            )

        # Display results
        if result["success"]:
            print(f"\n✅ Document generation successful!")
            print(f"📁 Generated files:")
            for file in result.get("generated_files", []):
                print(f"   - {file}")

            if result.get("validation_result"):
                validation = result["validation_result"]
                print(f"🔍 Validation score: {validation.get('overall_score', 0):.1f}/10")

        else:
            print(f"\n❌ Document generation failed")
            for error in result.get("errors", []):
                print(f"   Error: {error}")

        # Display warnings
        for warning in result.get("warnings", []):
            print(f"⚠️ {warning}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()