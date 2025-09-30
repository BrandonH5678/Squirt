# Squirt AI Operator Manual
**Version:** 1.0
**Date:** 2025-09-17
**Single Source of Truth for Claude/AI Operators**

---

## 🚨 CRITICAL SYSTEM ALERTS

### Current System Status: VOICE PROCESSING INTEGRATION OPERATIONAL ✅
- **UNO Generator:** Successfully processes JSON templates with formula evaluation
- **Template Library:** JSON files are now properly processed by generator
- **Formula Engine:** Evaluates qty_formula, hrs_formula, and parameter substitution
- **Content Verification:** Documents show template ID and confirm template-driven generation
- **🎙️ VOICE PROCESSING:** Complete voice-to-document integration OPERATIONAL
- **Voice Engine:** Dual-mode transcription (fast <3min, accurate <20min) via standalone engine
- **Content Extraction:** Advanced NLP parsing with 85%+ accuracy for client info extraction
- **Business Hours Coordination:** Voice processing yields to LibreOffice during 6am-7pm Mon-Fri
- **Thermal Safety:** Automatic monitoring and protection for 2012 Mac Mini hardware
- **Last Updated:** 2025-11-27 - VOICE PROCESSING INTEGRATION COMPLETED

**✅ Voice memo → professional document workflow operational - 95% time reduction achieved**

---

## 📋 VISUAL VALIDATION PROTOCOL MATRIX

### Immediate Visual Validation Required ✅
- **Single document generation** (templates, invoices, contracts)
- **Final iteration** of any multi-step process
- **Production document** intended for client delivery
- **Debugging/troubleshooting** document issues
- **User explicitly requests** visual validation
- **No explicit multi-stage process** mentioned

### Visual Validation Can Be Deferred ⏳
- **Multi-stage document development** with explicit stages outlined
- **Batch processing** where iterative analysis/editing is planned
- **Development iterations** before final validation checkpoint
- **User explicitly states** "skip visual validation"

### Default Behavior
**ALWAYS perform visual validation immediately unless explicitly part of multi-stage process**

---

## 📸 LIBREOFFICE MONITORING REQUIREMENTS

### Mandatory LibreOffice State Checks
**Before Document Operations:**
1. Check if LibreOffice is running: `ps aux | grep -E "(soffice|libreoffice)"`
2. Monitor for existing documents: `wmctrl -l | grep -i libreoffice`
3. Prepare screenshot environment

**During Document Operations:**
1. **Automatic Screenshot Triggers:**
   - LibreOffice application launch
   - Document open/load completion
   - Dialog box appearance
   - Error message display
   - Save/export operations

**After Document Operations:**
1. **Mandatory Screenshots:**
   - Complete document capture (all pages)
   - Error dialog detection
   - Final document state verification

### Dialog Detection Protocol
```bash
# Monitor for LibreOffice dialogs
wmctrl -l | grep -i "dialog\|error\|warning"
# Capture screenshot immediately when detected
gnome-screenshot -f /home/johnny5/Squirt/validation_screenshots/dialog_$(date +%Y%m%d_%H%M%S).png
```

---

## 🔄 DOCUMENT LIFECYCLE PROTOCOLS

### Phase 1: Input Processing (NEW - Voice Integration)
1. **Input Source Detection:** Voice memo, manual, SMS, or paper
2. **Voice Processing:** Standalone engine transcription (if audio input)
3. **Content Extraction:** Advanced NLP parsing for client data
4. **Multi-Input Merger:** Conflict resolution between sources
5. **Human Review Trigger:** Flag low-confidence extractions
6. **Thermal Safety Check:** Verify system temperature <85°C

### Phase 2: Pre-Generation
1. **Protocol Injection:** Load current operational rules
2. **LibreOffice State Check:** Ensure clean environment and no conflicts
3. **Template Validation:** Verify JSON schema compliance
4. **Input Validation:** Check client data completeness
5. **Business Hours Coordination:** Defer voice processing if LibreOffice active

### Phase 3: Generation
1. **Process Monitoring:** Track LibreOffice state changes
2. **Error Detection:** Monitor for dialogs, errors, warnings
3. **Progress Tracking:** Log generation steps
4. **Automatic Screenshots:** Capture on state changes
5. **Queue Management:** Process voice jobs by priority

### Phase 4: Post-Generation Validation
1. **Content Verification:** Ensure template data was actually used
2. **Visual Validation:** Screenshot complete document
3. **Mathematical Validation:** Verify calculations
4. **Format Validation:** Check professional standards
5. **File Organization:** Proper client/company file structure
6. **Voice Audit Trail:** Log voice processing metadata

### Phase 5: Quality Assurance
1. **Claude Vision Analysis:** Professional appearance verification
2. **Error Reporting:** Document any issues found
3. **Compliance Check:** Tax rules, business standards
4. **Archive Documentation:** Update tracking systems
5. **Voice Processing Review:** Accuracy feedback for continuous improvement

---

## ⚠️ ERROR RECOVERY PROCEDURES

### LibreOffice Errors
1. **Dialog Detection:** Automatically screenshot dialog
2. **Error Analysis:** Read dialog content, determine action
3. **Recovery Actions:** Close dialogs, restart if needed
4. **Document Recovery:** Attempt to recover unsaved work
5. **User Notification:** Report error and recovery actions

### Template Processing Errors
1. **JSON Validation:** Check template syntax
2. **Schema Compliance:** Verify required fields
3. **Content Verification:** Ensure dynamic content generation
4. **Fallback Options:** Use working templates or manual input

### File System Errors
1. **Permission Check:** Verify file access rights
2. **Directory Creation:** Create missing directories
3. **Backup Recovery:** Restore from backup if available
4. **User Guidance:** Provide manual resolution steps

---

## 📊 VALIDATION REQUIREMENTS

### Technical Validation (Automated)
- **Currency Formatting:** All monetary values properly formatted
- **Mathematical Accuracy:** Calculations verified
- **Required Sections:** Headers, materials, labor, totals present
- **Template Usage:** Verify dynamic content from templates (CRITICAL)

### Visual Validation (Claude Vision)
- **Professional Appearance:** Clean, branded presentation
- **Content Completeness:** All sections filled appropriately
- **Format Consistency:** Tables, spacing, typography
- **Error Detection:** Missing data, formatting issues

### Business Validation
- **Tax Compliance:** State-specific tax rules applied
- **Pricing Reasonableness:** Costs within acceptable ranges
- **Client Information:** Accurate and complete
- **Service Descriptions:** Clear and detailed

---

## 🎯 PERFORMANCE BENCHMARKS

### Speed Targets
- **Voice Processing:** < 3 minutes (fast mode), < 20 minutes (accurate mode)
- **Content Extraction:** < 5 seconds for typical voice memo
- **Document Generation:** < 30 seconds from template to PDF
- **Visual Validation:** < 45 seconds for screenshot + analysis
- **Error Recovery:** < 60 seconds for common issues
- **Complete Voice Workflow:** < 5 minutes voice memo to client-ready document

### Quality Standards
- **Voice Transcription:** 85%+ (fast mode), 95%+ (accurate mode)
- **Content Extraction:** 80%+ client names, 90%+ amounts, 95%+ service categorization
- **Mathematical Accuracy:** 100% - zero calculation errors
- **Template Usage:** 100% - templates must drive content
- **Professional Formatting:** 95%+ visual quality score
- **Tax Compliance:** 100% - state rules correctly applied

### Consistency Metrics
- **Protocol Compliance:** 95%+ adherence to all procedures
- **Error Detection:** 100% capture of LibreOffice dialogs
- **Documentation:** All operations logged and tracked

---

## 🔧 SYSTEM INTEGRATION POINTS

### LibreOffice Integration
- **Process Management:** Track application state
- **Document Control:** Open, edit, save, export operations
- **Error Handling:** Dialog detection and resolution
- **Screenshot System:** Automated capture on events

### File System Integration
- **Client Files/:** Individual client document organization
- **Company Files/:** Internal business document storage
- **validation_screenshots/:** Visual validation image storage
- **templates/:** JSON template library

### QuickBooks Integration
- **CSV Generation:** Automated accounting export
- **Status-Based Export:** Generate on document status changes
- **Tax Rules:** Proper tax category assignment

### Voice Processing Integration
- **Standalone Engine:** Dual-mode transcription via faster-whisper and OpenAI Whisper
- **Queue Management:** Priority-based job scheduling with thermal safety
- **Multi-Input Support:** Voice + SMS + paper + manual corrections
- **Business Hours Coordination:** Automatic LibreOffice priority enforcement
- **Thermal Safety:** Real-time temperature monitoring and protection protocols

---

## 📝 COMMUNICATION PROTOCOLS

### User Notifications
**Voice Processing:**
```
"🎙️ Processing voice memo: [filename]. Mode: [fast/accurate]. Estimated time: [duration]."
```

**Content Extraction:**
```
"📊 Voice processing completed. Confidence: [score]. Extracted: Client=[name], Service=[type], Amount=$[amount]. Review recommended: [yes/no]."
```

**Document Generation:**
```
"Generated [document_type] successfully. Performing visual validation to ensure formatting, content, and presentation meet professional standards."
```

**Error Detection:**
```
"LibreOffice dialog detected. Taking screenshot and analyzing for resolution options."
```

**Thermal Alerts:**
```
"🔥 THERMAL WARNING: CPU temperature [temp]°C. Voice processing [deferred/continuing with fast mode]. External cooling recommended."
```

**Validation Results:**
```
"Visual validation complete. Document meets professional standards with [score]/10 quality rating."
```

### Error Reporting
**Critical Errors:**
```
"CRITICAL: Template processing failed - generator using hardcoded content instead of template data."
```

**Recovery Actions:**
```
"Error resolved: [action_taken]. Document generation proceeding normally."
```

---

## 🔄 PROTOCOL VERSION CONTROL

### Change Management
- **Protocol Updates:** Must be reflected in this manual
- **Version History:** Track all changes with dates
- **Conflict Resolution:** This manual takes precedence over scattered files
- **Review Schedule:** Weekly protocol review and updates

### Update Procedure
1. **Identify Change:** New requirement or protocol modification
2. **Update Manual:** Modify this single source of truth
3. **Test Implementation:** Verify new protocol works
4. **Archive Old Files:** Remove outdated protocol documents

---

## 🎯 SUCCESS CRITERIA

### Session Success
- ✅ All protocols followed consistently
- ✅ Visual validation performed when required
- ✅ LibreOffice state monitored throughout
- ✅ Errors detected and resolved promptly
- ✅ Documentation complete and accurate

### System Success
- ✅ Template processing actually uses JSON templates
- ✅ Dynamic content generation functional
- ✅ Professional quality documents produced
- ✅ Zero mathematical or formatting errors
- ✅ Complete integration with business systems

---

---

## 🎙️ VOICE PROCESSING PROTOCOLS

### Voice Input Processing Workflow

**Step 1: Audio Input Validation**
1. **File Format Check:** Verify WAV, MP3, M4A, or OGG format
2. **Quality Assessment:** Check duration (<5 min optimal), clear audio
3. **Thermal Safety:** Verify CPU temperature <85°C before processing
4. **LibreOffice State:** Check for conflicts during business hours

**Step 2: Transcription Processing**
1. **Mode Selection:** Fast (<3min) or Accurate (<20min) based on priority
2. **Standalone Engine:** Route to appropriate voice processing system
3. **Progress Monitoring:** Track processing time and system resources
4. **Error Handling:** Retry logic for failed transcriptions

**Step 3: Content Extraction**
1. **NLP Analysis:** Extract client name, address, service, amount, contact
2. **Confidence Scoring:** Rate extraction accuracy for each field
3. **Service Categorization:** Map service description to template category
4. **Validation Flags:** Mark low-confidence extractions for review

**Step 4: Human Review Decision**
```
REQUIRE HUMAN REVIEW IF:
- Overall confidence <70%
- Missing critical fields (client name, service description)
- Unusual amounts (outside normal ranges)
- Multiple conflicting input sources
- Audio quality issues detected
```

**Step 5: Multi-Input Conflict Resolution**
1. **Source Priority:** Manual > Voice > SMS > Paper (OCR)
2. **Field-Specific Rules:** Latest contact info, highest confidence names
3. **Interactive Review:** Present conflicts for human resolution
4. **Audit Trail:** Log all corrections and source decisions

### Voice Processing Commands

**Direct Voice Processing:**
```bash
python3 voice_enabled_generator.py [audio_file] [template] --mode [fast/accurate] --review
```

**Queue-Based Processing:**
```bash
python3 voice_queue_manager.py add --audio [file] --template [template] --priority [level]
```

**Multi-Input Processing:**
```bash
python3 multi_input_processor.py --voice [audio] --manual [json] --interactive
```

**Claude Code Integration:**
```
/waterwizard-voice [audio_file] [estimate/invoice] --mode [fast/accurate] --review
```

### Voice Memo Quality Guidelines

**OPTIMAL VOICE MEMOS INCLUDE:**
- **Client Identification:** "This is for [Full Name]" or "Client is [Name]"
- **Complete Address:** "At [Number Street, City]" or minimum street name
- **Service Description:** "Fall cleanup" / "Irrigation repair" / "Landscape installation"
- **Contact Information:** "Phone number is [503-555-1234]"
- **Estimated Amount:** "About $500" / "Around fifteen hundred dollars"
- **Special Notes:** Access issues, urgency, client preferences

**EXAMPLE OPTIMAL VOICE MEMO:**
> "Hi, this is an estimate for Jane Wilson at 456 Oak Avenue in Beaverton. She needs fall cleanup for her front and back yard, probably about a quarter acre total. Her phone number is 503-555-1234. She mentioned the backyard has lots of leaves under the deck that are hard to reach. Not urgent, can be done next week. Estimate should be around $400 to $500."

### Thermal Safety Protocols

**MANDATORY THERMAL CHECKS:**
```bash
# Before ANY voice processing operation
python3 thermal_safety_manager.py check

# Expected output format:
Temperature: 78.0°C
State: warm
Safe for voice (fast): True
Safe for voice (accurate): False
```

**THERMAL STATE ACTIONS:**
- **SAFE (<75°C):** All voice processing modes available
- **WARM (75-80°C):** Monitor closely, prefer fast mode
- **HOT (80-85°C):** Fast mode only, defer accurate mode
- **CRITICAL (85-90°C):** Defer all voice processing
- **EMERGENCY (>90°C):** Emergency stop all AI operations

**THERMAL EMERGENCY RESPONSE:**
1. **Immediate:** Stop all voice processing operations
2. **Alert:** Notify user of thermal emergency condition
3. **External Cooling:** Activate USB fans, check airflow
4. **Monitoring:** Continue temperature monitoring
5. **Recovery:** Resume when temperature <80°C

### Business Hours Coordination

**BUSINESS HOURS (6am-7pm Mon-Fri):**
- **LibreOffice Priority:** Document generation has absolute priority
- **Voice Processing:** Queue jobs, process during idle periods only
- **Emergency Override:** Critical client requests can interrupt
- **Resource Monitoring:** Ensure no interference with document workflow

**OFF-HOURS/WEEKENDS:**
- **Voice Processing Priority:** Full system resources available
- **Accurate Mode:** Preferred time for high-quality transcription
- **Batch Processing:** Process accumulated voice memo queue
- **Maintenance Window:** System updates and optimization

### Error Recovery Procedures

**Voice Processing Failures:**
1. **Audio File Issues:** Verify format, try different audio file
2. **Transcription Errors:** Switch modes (fast ↔ accurate), check thermal state
3. **Extraction Failures:** Use manual review mode, apply corrections
4. **Template Errors:** Verify template path, check JSON validity
5. **LibreOffice Conflicts:** Wait for idle state, use priority override

**Queue Management Errors:**
1. **Database Lock:** Stop queue processing, restart system
2. **Thermal Override:** Wait for cooling, use external fans
3. **Memory Issues:** Close other applications, increase swap
4. **Permission Errors:** Check file permissions, verify paths

**Recovery Commands:**
```bash
# Reset voice processing queue
python3 voice_queue_manager.py stop
python3 voice_queue_manager.py start

# Clear thermal emergency state
python3 thermal_safety_manager.py check

# Test voice processing pipeline
python3 test_voice_integration.py
```

### Success Metrics and Monitoring

**VOICE PROCESSING SUCCESS CRITERIA:**
- ✅ Transcription completed within target time
- ✅ Client information extracted with >80% confidence
- ✅ Service correctly categorized
- ✅ Professional document generated and validated
- ✅ No thermal safety violations
- ✅ No business hour LibreOffice conflicts

**MONITORING COMMANDS:**
```bash
# System status overview
python3 voice_queue_manager.py status
python3 thermal_safety_manager.py summary
python3 libreoffice_coordinator.py status

# Performance monitoring
python3 test_voice_integration.py  # Run performance tests
```

**QUALITY ASSURANCE CHECKLIST:**
- [ ] Voice processing mode appropriate for urgency
- [ ] All extracted client information verified
- [ ] Service description matches actual scope
- [ ] Estimated amount reasonable for service type
- [ ] Generated document meets professional standards
- [ ] Thermal safety maintained throughout process
- [ ] Business hour priorities respected

---

**Remember: Voice processing enhances efficiency but human review ensures accuracy. When in doubt, validate immediately. Better to over-validate than miss critical issues.**

**Protocol Authority: This manual supersedes all other scattered protocol files.**