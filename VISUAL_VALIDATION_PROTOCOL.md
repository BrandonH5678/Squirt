# Squirt Visual Validation Protocol

## Core Principle
**Every document generation should include visual validation via screenshot capture and Claude Vision analysis, unless explicitly part of a multi-stage development process.**

## 🔍 Validation Decision Matrix

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
- **User explicitly states** "skip visual validation" or "postpone validation"
- **Clear indication** of additional turns/iterations planned

## 📋 Multi-Stage Process Guidelines

### When Multi-Stage is Appropriate:
```
Example Valid Multi-Stage Process:
1. "Generate 5 templates for batch review" 
2. "Analyze and edit templates based on specifications"
3. "Refine formatting and content" 
4. "Final visual validation of all templates"
```

### Required Elements for Deferred Validation:
1. **Explicit Stage Definition**: Clear indication of multiple steps
2. **Planned Validation Point**: Visual validation scheduled for later stage
3. **Logical Development Flow**: Makes sense to defer validation
4. **User Agreement**: User understands validation timing

## 🎯 Implementation Protocol

### Default Behavior (Standard):
```python
def generate_document():
    document = create_document()
    save_document(document)
    
    # DEFAULT: Immediate visual validation
    screenshot = capture_complete_document(document)
    vision_analysis = analyze_with_claude_vision(screenshot)
    return document, vision_analysis
```

### Multi-Stage Behavior (When Appropriate):
```python
def generate_document_multi_stage(stage_info):
    document = create_document()
    save_document(document)
    
    if stage_info.is_final_stage or stage_info.validation_required:
        # Visual validation at planned checkpoint
        screenshot = capture_complete_document(document)
        vision_analysis = analyze_with_claude_vision(screenshot)
        return document, vision_analysis
    else:
        # Deferred validation - log for later
        log_validation_deferred(document, stage_info.next_validation_point)
        return document, None
```

## 📸 Complete Document Capture Requirements

### Multi-Page Document Protocol:
1. **Automatic Scrolling**: Scroll through entire document
2. **Complete Coverage**: Capture all pages, not just first page
3. **Error Detection**: Screenshot any LibreOffice dialogs or errors
4. **Comprehensive Review**: Ensure full visual verification

### Screenshot Standards:
- **Format**: PNG with timestamp naming
- **Storage**: `validation_screenshots/` directory  
- **Base64 Encoding**: Ready for Claude Vision API
- **Metadata**: Document path, generation parameters, validation stage

## 🔄 Image Monitoring Integration

### Project Folder Monitoring:
**Watch this folder:** `validation_screenshots/` for new project images prior to each response. If a new image is detected:
1. **Consider carefully** as part of response context
2. **If user doesn't mention it**: Remind user you noticed it
3. **Ask appropriately**: When timing seems right in conversation flow
4. **Integrate context**: Use visual information to inform next actions

## ⚖️ Decision Framework

### Ask These Questions:
1. **Is this a single document generation?** → Immediate validation
2. **Did user outline multiple stages?** → Consider deferment  
3. **Is this the final iteration?** → Validation required
4. **Are more edits explicitly planned?** → Deferment may be appropriate
5. **When in doubt?** → Default to immediate validation

### Red Flags for Deferment:
- No clear multi-stage process outlined
- User expects immediate results
- Production/client-ready document
- Debugging or error troubleshooting
- First time generating this type of document

## 📝 Communication Protocol

### When Deferring Validation:
```
"I'm generating these templates as part of our multi-stage process. 
Since you mentioned iterative analysis and editing, I'll defer visual 
validation until we reach the final refinement stage. Visual validation 
will be performed before final delivery."
```

### When Performing Immediate Validation:
```
"Generated template successfully. Performing visual validation now to 
ensure formatting, content, and presentation meet professional standards."
```

### When Uncertain:
```
"I can generate this document now. Should I perform immediate visual 
validation, or is this part of a multi-stage process where validation 
would be better deferred until a later checkpoint?"
```

## 🎯 Success Metrics

### Validation Effectiveness:
- **Catch formatting issues** before human review
- **Detect LibreOffice errors** and dialogs
- **Verify complete document** rendering
- **Ensure professional presentation** standards

### Process Efficiency:
- **Avoid unnecessary validation** during development iterations
- **Maintain quality standards** at appropriate checkpoints
- **Support iterative workflows** while ensuring final quality
- **Balance automation with intelligent decision-making**

---

## Summary

**Default**: Perform visual validation immediately unless explicitly part of a multi-stage process.

**Exception**: Defer validation when user outlines clear multi-stage development with planned validation checkpoints.

**Principle**: When in doubt, validate immediately - better to over-validate than miss critical visual issues.