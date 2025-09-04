# WaterWizard Template Schema
# Element-based pricing structure for irrigation documents

from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Element:
    """Base element for all irrigation components"""
    id: str
    name: str
    category: str  # materials, equipment, labor, narrative
    unit: str  # each, ft, hr, sqft
    base_rate: Decimal
    description: str
    soil_modifiers: Optional[Dict[str, Decimal]] = None  # turf, rocky, clay, roots
    
@dataclass
class LineItem:
    """Individual line item in a document"""
    element_id: str
    quantity: Decimal
    unit_rate: Decimal
    line_total: Decimal
    description: str
    category: str

@dataclass
class Document:
    """Base structure for contracts/invoices/receipts"""
    doc_type: str  # contract, invoice, receipt
    doc_number: str
    date: str
    client_name: str
    client_address: str
    project_description: str
    line_items: List[LineItem]
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    terms: str
    prepared_by: str = "WaterWizard Irrigation & Landscape"

# Standard soil type modifiers
SOIL_MODIFIERS = {
    "turf": Decimal("1.0"),     # baseline
    "rocky": Decimal("1.5"),    # 50% more difficult
    "clay": Decimal("1.3"),     # 30% more difficult  
    "roots": Decimal("1.4")     # 40% more difficult
}

# Standard tax rate (configurable)
DEFAULT_TAX_RATE = Decimal("0.0875")  # 8.75%