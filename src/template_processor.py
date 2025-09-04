#!/usr/bin/env python3
"""
WaterWizard Template Processor
Processes templates with parameters to generate itemized documents
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any
import re
from pathlib import Path

class TemplateProcessor:
    def __init__(self, elements_file="src/data/elements.json"):
        """Initialize with element library"""
        self.elements_file = elements_file
        self.elements = self.load_elements()
        self.soil_modifiers = {
            "turf": Decimal("1.0"),
            "rocky": Decimal("1.5"), 
            "clay": Decimal("1.3"),
            "roots": Decimal("1.4")
        }
    
    def load_elements(self) -> Dict:
        """Load element library from JSON"""
        try:
            with open(self.elements_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Elements file not found: {self.elements_file}")
            return {}
    
    def load_template(self, template_path: str) -> Dict:
        """Load template from JSON file"""
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def evaluate_formula(self, formula: str, params: Dict[str, Any]) -> Decimal:
        """Safely evaluate quantity formulas with parameters"""
        # For conditional expressions, evaluate before parameter replacement
        if " if " in formula and " else " in formula:
            try:
                # Create a safe evaluation context with parameters
                eval_context = params.copy()
                result = eval(formula, {"__builtins__": {}}, eval_context)
                return Decimal(str(result))
            except Exception as e:
                print(f"Error evaluating conditional formula '{formula}': {e}")
                return Decimal("0")
        
        # Standard formula evaluation with parameter replacement
        safe_formula = formula
        for param, value in params.items():
            safe_formula = safe_formula.replace(param, str(value))
        
        try:
            result = eval(safe_formula)
            return Decimal(str(result))
        except Exception as e:
            print(f"Error evaluating formula '{formula}': {e}")
            return Decimal("0")
    
    def evaluate_condition(self, condition: str, params: Dict[str, Any]) -> bool:
        """Evaluate simple boolean conditions"""
        # Handle "not variable"
        if condition.startswith("not "):
            var = condition[4:].strip()
            return not params.get(var, False)
        
        # Handle "variable == value"  
        if "==" in condition:
            var, value = condition.split("==")
            var = var.strip()
            value = value.strip().strip('"\'')
            return str(params.get(var, "")) == value
        
        # Handle direct boolean
        return params.get(condition.strip(), False)
    
    def get_element_rate(self, element_id: str, soil_type: str = "turf") -> Decimal:
        """Get element rate with soil modifier if applicable"""
        # Find element in any category
        element = None
        for category in self.elements.values():
            if element_id in category:
                element = category[element_id]
                break
        
        if not element:
            print(f"Element not found: {element_id}")
            return Decimal("0")
        
        base_rate = Decimal(element["base_rate"])
        
        # Apply soil modifier if element supports it
        if "soil_modifiers" in element and soil_type in element["soil_modifiers"]:
            modifier = Decimal(element["soil_modifiers"][soil_type])
            return base_rate * modifier
        
        return base_rate
    
    def process_template(self, template_path: str, parameters: Dict[str, Any]) -> Dict:
        """Process template with parameters to generate line items"""
        template = self.load_template(template_path)
        
        # Apply default values for missing parameters
        if "parameters" in template:
            for param_name, param_def in template["parameters"].items():
                if param_name not in parameters and "default" in param_def:
                    parameters[param_name] = param_def["default"]
        
        line_items = []
        subtotal = Decimal("0")
        
        # Process each element in template
        for element_spec in template["element_list"]:
            element_id = element_spec["element_id"]
            
            # Calculate quantity using formula
            quantity = self.evaluate_formula(element_spec["quantity_formula"], parameters)
            
            # Skip zero quantities
            if quantity <= 0:
                continue
            
            # Get unit rate (with soil modifier if applicable)
            soil_type = parameters.get("soil_type", "turf")
            if element_spec.get("soil_modifier", False):
                unit_rate = self.get_element_rate(element_id, soil_type)
            else:
                unit_rate = self.get_element_rate(element_id)
            
            # Calculate line total
            line_total = quantity * unit_rate
            line_total = line_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Format description with parameters
            description = element_spec["description"].format(**parameters)
            
            # Get element info for category
            element_info = self.find_element(element_id)
            category = element_info.get("category", "unknown") if element_info else "unknown"
            
            line_items.append({
                "element_id": element_id,
                "description": description,
                "quantity": float(quantity),
                "unit_rate": float(unit_rate),
                "line_total": float(line_total),
                "category": category,
                "unit": element_info.get("unit", "each") if element_info else "each"
            })
            
            subtotal += line_total
        
        # Process conditional text first, add to parameters
        conditional_params = parameters.copy()
        if "conditional_text" in template:
            for text_key, conditions in template["conditional_text"].items():
                if self.evaluate_condition(conditions["condition"], parameters):
                    replacement = conditions["true"]
                else:
                    replacement = conditions.get("false", "")
                conditional_params[text_key] = replacement
        
        # Generate narrative with all parameters including conditional text
        narrative = template["narrative_template"].format(**conditional_params)
        
        return {
            "template_id": template["template_id"],
            "template_name": template["name"],
            "parameters": parameters,
            "line_items": line_items,
            "subtotal": float(subtotal),
            "narrative": narrative,
            "terms": template.get("terms", ""),
            "category": template.get("category", "service")
        }
    
    def find_element(self, element_id: str) -> Dict:
        """Find element in any category"""
        for category in self.elements.values():
            if element_id in category:
                return category[element_id]
        return {}

def main():
    """Test the template processor"""
    processor = TemplateProcessor()
    
    # Test sprinkler zone template
    print("=== Testing Sprinkler Zone Template ===")
    params = {
        "zone_number": 1,
        "head_count": 6,
        "trench_feet": 120,
        "soil_type": "clay"
    }
    
    result = processor.process_template("src/templates/sprinkler_zone.json", params)
    
    print(f"Template: {result['template_name']}")
    print(f"Parameters: {result['parameters']}")
    print("\nLine Items:")
    for item in result['line_items']:
        print(f"  {item['description']}")
        print(f"    {item['quantity']} {item['unit']} × ${item['unit_rate']:.2f} = ${item['line_total']:.2f}")
    
    print(f"\nSubtotal: ${result['subtotal']:.2f}")
    print(f"\nNarrative: {result['narrative']}")
    print(f"\nTerms: {result['terms']}")

if __name__ == "__main__":
    main()