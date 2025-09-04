# WaterWizard Contract Generator

Generate a professional WaterWizard irrigation contract based on project specifications.

## Usage: /waterwizard-contract [project_name] [client_name] [zones] [trench_feet] [soil_type]

## Arguments:
- project_name: Brief project description (e.g., "Sprinkler System Expansion")
- client_name: Customer name for contract
- zones: Number of sprinkler zones to install  
- trench_feet: Total feet of trenching required
- soil_type: "turf", "rocky", "clay", or "roots"

## Process:
1. Load WaterWizard context and Kim Sherertz contract formatting example
2. Calculate materials needed:
   - Zones × materials per zone (valves, heads, pipe, fittings)
   - Trench_feet × soil multiplier for labor hours
   - Apply current pricing rates from templates
3. Generate contract with:
   - Professional heading with project name and cost
   - Element-by-element breakdown (Zone 1: $X, Zone 2: $Y)
   - Narrative descriptions for each element
   - Itemized materials and labor tables
   - Subtotals, tax calculation, total
   - Standard terms and signature blocks
4. Validate all required sections present
5. Generate accompanying CSV for QuickBooks import

Maintain the exact formatting style from the Kim Sherertz contract example - fonts, colors, organization, mathematical precision.