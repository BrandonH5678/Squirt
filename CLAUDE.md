# Squirt - Claude Code Integration Guide

## 🚨 MANDATORY FIRST STEP - READ THIS BEFORE ALL TASKS

**ZERO TOLERANCE POLICY: Mathematical errors are UNACCEPTABLE in production documents.**

### ALWAYS START WITH THESE VALIDATION STEPS:

**PHASE 0: Source Document Verification (MANDATORY BEFORE ALL DOCUMENT GENERATION):**
1. **Locate source spreadsheet/document** - Find ODS, CSV, PDF, or JSON source
2. **Read source values line-by-line** - Extract EXACT quantities, rates, prices
3. **Verify ALL calculations manually** - Never trust formulas without verification
4. **Compare totals independently** - Recalculate subtotals and tax independently
5. **Flag ANY discrepancies immediately** - Stop and ask user before proceeding

**CRITICAL MATH VALIDATION RULES:**
- ✅ **ALWAYS** convert ODS/Excel to CSV and read exact values
- ✅ **ALWAYS** verify quantities match source (not template defaults)
- ✅ **ALWAYS** recalculate all arithmetic independently
- ✅ **ALWAYS** validate subtotals sum correctly
- ✅ **ALWAYS** verify tax calculations (rate × subtotal)
- ✅ **ALWAYS** check final total = subtotal + tax
- ❌ **NEVER** assume template quantities are correct
- ❌ **NEVER** skip Equipment section if present in source
- ❌ **NEVER** modify source values without explicit approval
- ❌ **NEVER** round differently than source document

## System Overview
Squirt is WaterWizard's production AI document automation system that transforms voice memos into professional contracts and invoices in under 5 minutes with **ZERO mathematical errors**.

## Core Mission
**Primary Purpose:** Automate WaterWizard business document creation through voice input, maintaining **100% mathematical accuracy** and professional quality while operating safely on aging hardware with thermal constraints.

## Current System Status
- **Status:** Production Operational ✅
- **Voice Processing:** Dual-engine (faster-whisper + OpenAI Whisper) with **intelligent model selection** ✅
- **Document Generation:** LibreOffice UNO bridge with visual validation
- **Integration:** Sherlock intelligence sharing, Johny5Alive health monitoring
- **Safety:** Thermal monitoring, business hours coordination
- **Last Updated:** 2025-09-29 - INTELLIGENT MODEL SELECTION DEPLOYED

## 🤖 INTELLIGENT MODEL SELECTION (NEW - CRITICAL)

### MANDATORY AUTO-INJECTION: Voice Processing Tasks

**BEFORE Any Voice Processing Implementation:**
**CRITICAL CONSTRAINTS (Auto-Inject):**
- **🤖 INTELLIGENT MODEL SELECTION**: ALWAYS use `IntelligentModelSelector` - NEVER hard-code model choice
- **Memory Limit**: 3.7GB total RAM, ~2.0GB available during business hours (LibreOffice active)
- **Thermal Constraint**: Aging Mac mini requires thermal monitoring during intensive processing
- **Business Hours Priority**: LibreOffice must have priority 6am-7pm Mon-Fri
- **Established Architecture**: Standalone voice engine with dual-mode operation
- **Processing Protocol**: Voice memo → transcription → content extraction → document generation
- **Selection Priority**: System viability > Quality preferences (85% complete beats 95% crash)

### Voice Processing Decision Rules

**Squirt-Specific Constraints:**
```python
# Voice memos are typically short (<5 minutes)
# LibreOffice uses ~500-800MB during business hours
# Thermal safety requires conservative model selection

SQUIRT_CONSTRAINTS = {
    "business_hours": {
        "available_ram": "1.5-2.0GB",  # LibreOffice active
        "recommended_model": "faster-whisper tiny or base",
        "thermal_risk": "moderate"
    },
    "after_hours": {
        "available_ram": "2.5-3.0GB",  # LibreOffice idle
        "recommended_model": "faster-whisper small",
        "thermal_risk": "low"
    }
}
```

### MANDATORY PRE-PROCESSING VALIDATION

**PHASE 1: Model Selection (MANDATORY FIRST STEP):**
```bash
# Check current system state
python3 -c "
from intelligent_model_selector import IntelligentModelSelector, QualityPreference
selector = IntelligentModelSelector()

# Short voice memos (typical Squirt use case)
selection = selector.select_model(
    audio_path='voice_memo.m4a',
    quality_preference=QualityPreference.BALANCED
)
selector.log_selection(selection)
assert selector.validate_selection(selection), 'Model exceeds constraints'
"
```

### CRITICAL FAILURE INDICATORS

**🚨 RED FLAGS - STOP IMPLEMENTATION:**

**MODEL SELECTION VIOLATIONS (HIGHEST PRIORITY):**
- ❌ Selecting ANY voice model without using IntelligentModelSelector
- ❌ Hard-coding model choice in voice processing code
- ❌ Selecting OpenAI Whisper large-v3 during business hours (<2GB available)
- ❌ Ignoring thermal constraints for aging hardware
- ❌ Bypassing intelligent selection with "for best results" comments
- ❌ Processing long audio (>30min) without chunking strategy

**BUSINESS LOGIC VIOLATIONS:**
- ❌ Voice processing blocking LibreOffice during business hours
- ❌ Thermal load exceeding safety thresholds
- ❌ Processing taking >5 minutes for typical voice memos
- ❌ **MATHEMATICAL ERRORS IN DOCUMENT GENERATION (CRITICAL - ZERO TOLERANCE)**

**MATHEMATICAL ACCURACY VIOLATIONS (ZERO TOLERANCE):**
- ❌ Using template defaults without verifying source document quantities
- ❌ Skipping sections that exist in source (e.g., Equipment, Truck Fee)
- ❌ Incorrect hours/quantities (e.g., 4.0 hrs when source says 4.5 hrs)
- ❌ Wrong subtotals, tax calculations, or final totals
- ❌ Generating documents without reading source ODS/CSV line-by-line
- ❌ Failing to independently verify ALL arithmetic

### CORRECT IMPLEMENTATION PATTERN

```python
# ✅ CORRECT: Squirt voice processing with intelligent selection
from intelligent_model_selector import IntelligentModelSelector, QualityPreference
import datetime

def process_voice_memo(audio_path: str):
    # Step 1: Check if business hours
    now = datetime.datetime.now()
    is_business_hours = (
        now.weekday() < 5 and  # Mon-Fri
        6 <= now.hour < 19     # 6am-7pm
    )

    # Step 2: Use intelligent model selection
    selector = IntelligentModelSelector()
    selection = selector.select_model(
        audio_path=audio_path,
        quality_preference=QualityPreference.BALANCED
    )

    # Step 3: Business hours constraint check
    if is_business_hours and selection.estimated_ram_mb > 400:
        print("⚠️ Business hours: LibreOffice priority, using faster model")
        selection = selector.select_model(
            audio_path=audio_path,
            quality_preference=QualityPreference.MINIMUM  # Force tiny model
        )

    # Step 4: Validate before processing
    if not selector.validate_selection(selection):
        raise RuntimeError("Cannot safely process - insufficient RAM")

    # Step 5: Process with selected model
    return transcribe_with_model(audio_path, selection)

# ❌ WRONG: Hard-coded model selection
import whisper
model = whisper.load_model("medium")  # Ignores constraints!
```

## Key Principles

1. **Voice Memos Are Short**: Typical Squirt memos <5min, optimize for speed
2. **LibreOffice Priority**: Document generation always takes precedence during business hours
3. **Thermal Safety**: Conservative model selection on aging hardware
4. **Fast Turnaround**: <5min total processing time maintains competitive advantage
5. **System Viability**: Completed 85% accurate transcription > crashed 95% attempt

## Integration Points

**Cross-System Coordination:**
- **Sherlock**: Share speaker profiles and business intelligence
- **Johny5Alive**: Thermal monitoring and system health coordination
- **LibreOffice**: Priority scheduling and resource coordination

**Safety Protocols:**
- Thermal monitoring during voice processing
- RAM validation before model loading
- Business hours awareness for priority management
- Graceful degradation under thermal stress

---

**This file provides automatic context injection for Claude Code when working in the Squirt system. Model selection prevents OOM crashes and maintains thermal safety for production operations.**