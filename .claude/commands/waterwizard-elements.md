Access and manage the WaterWizard template library of project elements.

## Usage: /waterwizard-elements [action] [element_name]

## Actions:
- list: Show all available elements
- show [element_name]: Display detailed element template
- add [element_name]: Add new element to library
- update [element_name]: Modify existing element
- pricing: Show current pricing rates

## Standard Elements Library:

### Installation Elements:
- valve_install: Electronic control valve installation
- sprinkler_head: PRS-45 head installation with swing joint
- pipe_assembly: Lateral distribution pipe (1" Sch 40 PVC)
- connection_mainline: Tap into existing main line

### Labor Elements:  
- trenching_turf: Hand trenching through regular turf (0.1 hr/ft)
- trenching_rocky: Hand trenching through rocky soil (0.15 hr/ft)
- trenching_clay: Hand trenching through hard clay (0.12 hr/ft)
- trenching_roots: Hand trenching through root systems (0.18 hr/ft)

### Materials Pricing:
- pvc_pipe_1in: 1" Schedule 40 PVC pipe (per foot)
- valve_electronic: Hunter/Rain Bird control valve
- sprinkler_prs45: Rain Bird PRS-45 sprinkler head
- fittings_standard: Elbows, tees, couplings (per joint)

## Process:
1. When listing: Show element name, description, typical pricing
2. When showing: Display full template with materials list, labor requirements, pricing structure
3. When adding/updating: Guide through template creation with required fields
4. For pricing: Show current rates with last update date

Each element template includes: description, materials list, labor requirements, pricing structure, typical quantities, and notes for variations.