#!/usr/bin/env python3
"""
Claude Code command for voice-enabled estimate generation
"""

import sys
import os
import argparse
from pathlib import Path

# Add Squirt src to path
squirt_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(squirt_src))

try:
    from voice_enabled_generator import VoiceEnabledEstimateGenerator, VOICE_ENGINE_AVAILABLE
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Voice processing not available")
    sys.exit(1)


def main():
    """Main command entry point"""

    if not VOICE_ENGINE_AVAILABLE:
        print("❌ Voice engine not available")
        print("Please install required packages: faster-whisper, openai-whisper")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate estimate from voice memo")
    parser.add_argument("audio_file", help="Path to voice memo audio file")
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast",
                       help="Voice processing mode (default: fast)")
    parser.add_argument("--employee", help="Employee name who recorded memo")
    parser.add_argument("--review", action="store_true",
                       help="Enable interactive review of extracted data")
    parser.add_argument("--template", help="Custom template path")

    args = parser.parse_args()

    # Validate audio file
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {args.audio_file}")
        sys.exit(1)

    # Determine template path
    if args.template:
        template_path = Path(args.template)
    else:
        # Use default fall cleanup template
        template_path = squirt_src.parent / "templates" / "fall_cleanup_template.json"

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        print("Available templates:")
        templates_dir = squirt_src.parent / "templates"
        if templates_dir.exists():
            for template in templates_dir.glob("*.json"):
                print(f"  - {template.name}")
        sys.exit(1)

    try:
        print(f"🎙️ WaterWizard Voice Estimate Generator")
        print(f"📁 Audio: {audio_path.name}")
        print(f"📋 Template: {template_path.name}")
        print(f"⚡ Mode: {args.mode}")
        print()

        # Initialize generator
        generator = VoiceEnabledEstimateGenerator()

        # Generate estimate
        if args.review:
            result = generator.generate_with_review(
                audio_file=str(audio_path),
                template_path=str(template_path),
                mode=args.mode,
                employee_name=args.employee
            )
        else:
            result = generator.generate_from_voice(
                audio_file=str(audio_path),
                template_path=str(template_path),
                mode=args.mode,
                employee_name=args.employee
            )

        # Display results
        if result["success"]:
            print(f"\n✅ Estimate generated successfully!")

            voice_result = result.get("voice_result")
            if voice_result:
                print(f"📊 Voice confidence: {voice_result.confidence:.2f}")
                print(f"⏱️ Processing time: {voice_result.processing_time:.1f}s")

                # Show extracted client info
                extracted = voice_result.extracted_data
                print(f"\n👤 Client Information:")
                print(f"   Name: {extracted.get('client_name', 'Not extracted')}")
                print(f"   Address: {extracted.get('property_address', 'Not extracted')}")
                print(f"   Service: {extracted.get('project_description', 'Not extracted')}")

            # Show generated files
            generated_files = result.get("generated_files", [])
            if generated_files:
                print(f"\n📁 Generated Files:")
                for file_path in generated_files:
                    print(f"   - {file_path}")

            # Show validation results
            validation = result.get("validation_result")
            if validation:
                score = validation.get("overall_score", 0)
                print(f"\n🔍 Quality Score: {score:.1f}/10")

                issues = validation.get("issues_found", [])
                if issues:
                    print(f"⚠️ Issues found: {len(issues)}")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"   - {issue}")

        else:
            print(f"\n❌ Estimate generation failed")
            for error in result.get("errors", []):
                print(f"   {error}")

        # Show warnings
        warnings = result.get("warnings", [])
        if warnings:
            print(f"\n⚠️ Warnings:")
            for warning in warnings:
                print(f"   - {warning}")

        # Show recommendations
        voice_result = result.get("voice_result")
        if voice_result and voice_result.needs_review:
            print(f"\n🔍 RECOMMENDATION: Human review suggested")
            print("   - Low confidence on key data extraction")
            print("   - Please verify client information before sending")

    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()