#!/usr/bin/env python3
"""
WaterWizard Tax Rules Engine
State-specific tax handling for accurate invoicing and contracts
"""

from decimal import Decimal
from typing import Dict, Tuple

class TaxRulesEngine:
    def __init__(self):
        """Initialize tax rules for different states"""
        
        # State-specific tax rates and rules
        self.state_tax_rules = {
            'OR': {
                'state_tax_rate': Decimal('0.0000'),  # Oregon has NO state sales tax
                'description': 'Oregon - No state sales tax',
                'local_tax_possible': False,
                'tax_exempt': True
            },
            'TX': {
                'state_tax_rate': Decimal('0.0625'),  # Texas state sales tax
                'description': 'Texas - 6.25% state sales tax',
                'local_tax_possible': True,
                'local_tax_range': (Decimal('0.0000'), Decimal('0.02')),  # Up to 2% local
                'typical_combined': Decimal('0.0825')  # 8.25% typical combined
            },
            'CA': {
                'state_tax_rate': Decimal('0.075'),   # California state sales tax
                'description': 'California - 7.5% state sales tax',
                'local_tax_possible': True,
                'local_tax_range': (Decimal('0.0010'), Decimal('0.03')),
                'typical_combined': Decimal('0.0875')  # 8.75% typical combined
            },
            'WA': {
                'state_tax_rate': Decimal('0.065'),   # Washington state sales tax
                'description': 'Washington - 6.5% state sales tax',
                'local_tax_possible': True,
                'local_tax_range': (Decimal('0.0050'), Decimal('0.039')),
                'typical_combined': Decimal('0.092')   # 9.2% typical combined
            }
        }
        
        # Default tax rate for unknown states
        self.default_tax_rate = Decimal('0.0750')  # 7.5% generic rate
    
    def get_tax_rate(self, state_code: str, local_override: Decimal = None) -> Tuple[Decimal, str]:
        """
        Get tax rate for a specific state
        Returns: (tax_rate, description)
        """
        state_code = state_code.upper().strip()
        
        if state_code not in self.state_tax_rules:
            return self.default_tax_rate, f"{state_code} - Using default 7.5% rate"
        
        rules = self.state_tax_rules[state_code]
        
        # Handle tax-exempt states (like Oregon)
        if rules.get('tax_exempt', False):
            return Decimal('0.0000'), rules['description']
        
        # Use local override if provided and valid
        if local_override is not None:
            local_range = rules.get('local_tax_range')
            if local_range and local_range[0] <= local_override <= local_range[1]:
                total_rate = rules['state_tax_rate'] + local_override
                return total_rate, f"{rules['description']} + {local_override:.2%} local"
        
        # Use typical combined rate or state rate
        return rules.get('typical_combined', rules['state_tax_rate']), rules['description']
    
    def calculate_tax(self, subtotal: Decimal, state_code: str, local_override: Decimal = None) -> Tuple[Decimal, Decimal, str]:
        """
        Calculate tax amount for a given subtotal and state
        Returns: (tax_amount, total_with_tax, tax_description)
        """
        tax_rate, description = self.get_tax_rate(state_code, local_override)
        
        tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'))
        total_with_tax = subtotal + tax_amount
        
        return tax_amount, total_with_tax, description
    
    def is_tax_exempt_state(self, state_code: str) -> bool:
        """Check if a state is tax exempt"""
        state_code = state_code.upper().strip()
        rules = self.state_tax_rules.get(state_code, {})
        return rules.get('tax_exempt', False)

def main():
    """Demo the tax rules engine"""
    
    tax_engine = TaxRulesEngine()
    
    print("🏛️ WATERWIZARD TAX RULES ENGINE")
    print("=" * 50)
    
    # Test various states with sample $1000 project
    test_subtotal = Decimal('1000.00')
    test_states = ['OR', 'TX', 'CA', 'WA', 'FL', 'NY']
    
    print(f"Sample project: ${test_subtotal}")
    print("\nTax calculations by state:")
    
    for state in test_states:
        tax_amount, total, description = tax_engine.calculate_tax(test_subtotal, state)
        print(f"{state}: ${tax_amount:>6.2f} tax | ${total:>8.2f} total | {description}")
    
    print(f"\n🔍 Oregon-specific test:")
    oregon_tax, oregon_total, oregon_desc = tax_engine.calculate_tax(Decimal('777.50'), 'OR')
    print(f"   Subtotal: $777.50")
    print(f"   Tax: ${oregon_tax:.2f}")
    print(f"   Total: ${oregon_total:.2f}")
    print(f"   Rule: {oregon_desc}")

if __name__ == "__main__":
    main()