# Squirt AI Operator Manual
**Version:** 1.0
**Date:** 2025-09-17
**Single Source of Truth for Claude/AI Operators**

---

## 🚨 CRITICAL SYSTEM ALERTS

### Current System Status: TEMPLATE PROCESSING OPERATIONAL ✅
- **UNO Generator:** Successfully processes JSON templates with formula evaluation
- **Template Library:** JSON files are now properly processed by generator
- **Formula Engine:** Evaluates qty_formula, hrs_formula, and parameter substitution
- **Content Verification:** Documents show template ID and confirm template-driven generation
- **Last Updated:** 2025-09-18 - Template processing core issue RESOLVED

**✅ Template generation now working - always verify content shows template data usage**

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

### Phase 1: Pre-Generation
1. **Protocol Injection:** Load current operational rules
2. **LibreOffice State Check:** Ensure clean environment
3. **Template Validation:** Verify JSON schema compliance
4. **Input Validation:** Check client data completeness

### Phase 2: Generation
1. **Process Monitoring:** Track LibreOffice state changes
2. **Error Detection:** Monitor for dialogs, errors, warnings
3. **Progress Tracking:** Log generation steps
4. **Automatic Screenshots:** Capture on state changes

### Phase 3: Post-Generation Validation
1. **Content Verification:** Ensure template data was actually used
2. **Visual Validation:** Screenshot complete document
3. **Mathematical Validation:** Verify calculations
4. **Format Validation:** Check professional standards
5. **File Organization:** Proper client/company file structure

### Phase 4: Quality Assurance
1. **Claude Vision Analysis:** Professional appearance verification
2. **Error Reporting:** Document any issues found
3. **Compliance Check:** Tax rules, business standards
4. **Archive Documentation:** Update tracking systems

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
- **Document Generation:** < 30 seconds from template to PDF
- **Visual Validation:** < 45 seconds for screenshot + analysis
- **Error Recovery:** < 60 seconds for common issues

### Quality Standards
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

---

## 📝 COMMUNICATION PROTOCOLS

### User Notifications
**Document Generation:**
```
"Generated [document_type] successfully. Performing visual validation to ensure formatting, content, and presentation meet professional standards."
```

**Error Detection:**
```
"LibreOffice dialog detected. Taking screenshot and analyzing for resolution options."
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

**Remember: When in doubt, validate immediately. Better to over-validate than miss critical issues.**

**Protocol Authority: This manual supersedes all other scattered protocol files.**