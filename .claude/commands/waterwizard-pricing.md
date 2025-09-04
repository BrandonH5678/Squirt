Display and manage current WaterWizard pricing rates for materials and labor.

## Usage: /waterwizard-pricing [category] [item_name]

## Categories:
- materials: Show all material pricing
- labor: Show labor rates
- elements: Show complete element pricing
- update [item]: Update pricing for specific item

## Current Pricing Structure:

### Labor Rates:
- Standard labor: $65.00/hour
- Trenching rates vary by soil condition:
  - Regular turf: $6.50/foot (0.1 hr/ft)
  - Rocky soil: $9.75/foot (0.15 hr/ft) 
  - Hard clay: $7.80/foot (0.12 hr/ft)
  - Root systems: $11.70/foot (0.18 hr/ft)

### Key Materials:
- Electronic control valve: $85.00 each
- Rain Bird PRS-45 head: $15.00 each
- 1" Schedule 40 PVC: $1.25/foot
- Valve box (standard): $25.00 each
- Swing joint assembly: $8.50 each

### Complete Elements:
- Valve installation (complete): ~$175.00
- Sprinkler head (installed): ~$45.00
- Lateral pipe (per foot): ~$4.85

## Process:
1. Load current pricing from elements.json template
2. Display requested category with last update dates
3. For updates: Validate new pricing and update template file
4. Show impact on typical project costs
5. Generate pricing summary for reference

## Output Format:
- Clean table format with item, unit, current price
- Last updated dates
- Typical markup percentages
- Notes on price variations or seasonal adjustments

Use this command to maintain consistent pricing across all contract and invoice generation.