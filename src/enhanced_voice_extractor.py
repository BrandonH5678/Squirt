#!/usr/bin/env python3
"""
Enhanced Voice Content Extractor
Advanced NLP parsing for voice memo content extraction
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging


@dataclass
class ExtractionConfidence:
    """Confidence scores for different extraction types"""
    overall: float
    client_name: float
    address: float
    service: float
    amount: float
    urgency: float
    contact: float


class EnhancedVoiceExtractor:
    """Advanced voice content extractor with improved NLP"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Enhanced patterns with context awareness
        self.client_patterns = [
            # Direct client mentions
            r"(?:client|customer)\s+(?:is\s+|name\s+is\s+)?([A-Za-z\s]+?)(?:\s+(?:at|lives|on|in|\.|,|phone|contact))",
            r"for\s+([A-Za-z\s]+?)(?:\s+(?:at|on|in|who|living|\.|,))",
            r"(?:this\s+is\s+for\s+|estimate\s+for\s+|working\s+for\s+)([A-Za-z\s]+?)(?:\s+(?:at|on|in|\.|,))",
            r"(?:mr\.?|mrs\.?|ms\.?|miss)\s+([A-Za-z\s]+?)(?:\s+(?:at|on|in|\.|,))",
            # Name patterns
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:at|on|in|lives|wants|needs|\.|,))",
            # Company patterns
            r"([A-Z][a-z]+\s+(?:LLC|Inc|Corporation|Company|Corp|Co\.))(?:\s+(?:at|on|in|\.|,))"
        ]

        self.address_patterns = [
            # Full address patterns
            r"(?:at|address|located\s+at|property\s+at|house\s+at)\s+(\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|boulevard|blvd)(?:\s*,?\s*[A-Za-z\s]*)?)",
            # Street only patterns
            r"(\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|boulevard|blvd))",
            # Partial address patterns
            r"(?:on|at)\s+([A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|boulevard|blvd))",
            # City/area patterns
            r"(?:in|at)\s+([A-Za-z\s]+(?:Portland|Beaverton|Tigard|Lake Oswego|Milwaukie|Gresham))",
            # Generic location
            r"property\s+(?:is\s+)?(?:at|on|in)\s+([A-Za-z0-9\s,.-]+?)(?:\s+(?:and|for|needs|\.|,))"
        ]

        self.service_patterns = [
            # Fall cleanup specific
            r"(?:fall\s+cleanup|leaf\s+cleanup|autumn\s+cleanup|seasonal\s+cleanup)",
            r"(?:clean\s+up\s+(?:leaves|debris|yard))",
            r"(?:remove\s+(?:leaves|debris))",

            # Irrigation specific
            r"(?:irrigation|sprinkler)\s+(?:repair|fix|maintenance|service|installation|install)",
            r"(?:fix|repair)\s+(?:irrigation|sprinkler|water\s+system)",
            r"(?:sprinkler\s+(?:heads|zones|system|repair))",

            # Landscaping
            r"(?:landscape|landscaping)\s+(?:installation|install|design|maintenance|work)",
            r"(?:plant|planting|plants)\s+(?:installation|install|new|trees|shrubs)",
            r"(?:garden|gardening)\s+(?:work|maintenance|installation)",

            # Maintenance
            r"(?:maintenance|trim|trimming|prune|pruning)\s+(?:shrubs|trees|bushes|plants)",
            r"(?:lawn\s+(?:care|maintenance|service))",
            r"(?:yard\s+(?:work|maintenance|cleanup))",

            # General service extraction
            r"(?:need|needs|want|wants|for|service)\s+([A-Za-z\s]+?)(?:\s+(?:at|for|estimate|quote|\.|,))",
            r"(?:estimate|quote)\s+for\s+([A-Za-z\s]+?)(?:\s+(?:at|for|\.|,))"
        ]

        self.amount_patterns = [
            # Explicit dollar amounts
            r"\$([0-9,]+(?:\.[0-9]{2})?)",
            r"([0-9,]+)\s*dollars?",
            # Estimated amounts
            r"(?:about|around|roughly|approximately|estimate)\s+\$?([0-9,]+(?:\.[0-9]{2})?)",
            r"(?:should\s+be|probably|maybe)\s+(?:about|around)?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
            # Range amounts
            r"(?:between|from)\s+\$?([0-9,]+)(?:\s+(?:to|and)\s+\$?([0-9,]+))?",
            # Written numbers
            r"(?:about|around)\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+hundred",
            r"(one|two|three|four|five)\s+thousand"
        ]

        self.urgency_patterns = {
            "high": [
                r"urgent|emergency|asap|as\s+soon\s+as\s+possible|immediately|today|right\s+away",
                r"need\s+(?:it\s+)?(?:done\s+)?(?:by\s+)?today",
                r"emergency|critical|urgent"
            ],
            "medium": [
                r"soon|this\s+week|next\s+few\s+days|quickly|prompt",
                r"need\s+(?:it\s+)?(?:done\s+)?(?:by\s+)?(?:this\s+)?week",
                r"when\s+(?:can\s+)?you\s+(?:do\s+it|come\s+out)"
            ],
            "low": [
                r"no\s+rush|when\s+(?:you\s+)?(?:have\s+)?time|eventually|flexible",
                r"not\s+urgent|take\s+your\s+time"
            ]
        }

        self.contact_patterns = [
            # Phone numbers
            r"(?:phone|call|contact|number)\s*(?:is\s*|:)?\s*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            # Email addresses
            r"(?:email|e-mail)\s*(?:is\s*|:)?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        ]

        # Service categorization mapping
        self.service_categories = {
            "cleanup": ["fall", "leaf", "debris", "seasonal", "autumn", "cleanup", "clean", "remove"],
            "irrigation_repair": ["irrigation", "sprinkler", "water", "system", "repair", "fix", "heads", "zones"],
            "irrigation_zone": ["new", "install", "installation", "zone", "coverage", "system"],
            "planting": ["plant", "planting", "trees", "shrubs", "garden", "flowers", "landscaping"],
            "maintenance": ["maintenance", "trim", "prune", "care", "service", "lawn", "yard"],
            "drainage": ["drainage", "drain", "standing", "water", "wet", "flooding", "runoff"],
            "hardscape": ["patio", "walkway", "driveway", "concrete", "stone", "pavers"],
            "lighting": ["lighting", "lights", "illuminate", "outdoor", "landscape", "path"]
        }

        # Written number conversion
        self.written_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
            "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20
        }

    def extract_data(self, transcription: str) -> Dict[str, Any]:
        """Extract structured data with enhanced NLP"""
        text = transcription.lower().strip()

        extracted = {
            "client_name": None,
            "property_address": None,
            "project_description": None,
            "estimated_amount": None,
            "amount_range": None,
            "contact_phone": None,
            "contact_email": None,
            "service_type": None,
            "urgency": "normal",
            "urgency_reason": None,
            "project_scope": {},
            "special_notes": [],
            "confidence_scores": {},
            "extraction_metadata": {
                "timestamp": datetime.now().isoformat(),
                "text_length": len(text),
                "word_count": len(text.split())
            }
        }

        # Extract with confidence scoring
        extracted.update(self._extract_client_info(text))
        extracted.update(self._extract_address_info(text))
        extracted.update(self._extract_service_info(text))
        extracted.update(self._extract_amount_info(text))
        extracted.update(self._extract_contact_info(text))
        extracted.update(self._extract_urgency_info(text))
        extracted.update(self._extract_scope_details(text))

        # Calculate overall confidence
        confidence_scores = extracted.get("confidence_scores", {})
        if confidence_scores:
            extracted["overall_confidence"] = sum(confidence_scores.values()) / len(confidence_scores)
        else:
            extracted["overall_confidence"] = 0.0

        # Add contextual validation
        extracted = self._validate_and_enhance(extracted, text)

        return extracted

    def _extract_client_info(self, text: str) -> Dict[str, Any]:
        """Extract client name with confidence scoring"""
        client_info = {"confidence_scores": {}}

        best_match = None
        best_confidence = 0.0

        for pattern in self.client_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                candidate = match.group(1).strip()
                confidence = self._score_client_name(candidate, match, text)

                if confidence > best_confidence:
                    best_match = candidate
                    best_confidence = confidence

        if best_match:
            client_info["client_name"] = self._clean_name(best_match)
            client_info["confidence_scores"]["client_name"] = best_confidence

        return client_info

    def _extract_address_info(self, text: str) -> Dict[str, Any]:
        """Extract address with geographic validation"""
        address_info = {"confidence_scores": {}}

        best_address = None
        best_confidence = 0.0

        for pattern in self.address_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                candidate = match.group(1).strip()
                confidence = self._score_address(candidate)

                if confidence > best_confidence:
                    best_address = candidate
                    best_confidence = confidence

        if best_address:
            address_info["property_address"] = self._clean_address(best_address)
            address_info["confidence_scores"]["property_address"] = best_confidence

        return address_info

    def _extract_service_info(self, text: str) -> Dict[str, Any]:
        """Extract service information with categorization"""
        service_info = {"confidence_scores": {}}

        # Direct service detection
        services_found = []
        for pattern in self.service_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            services_found.extend(matches)

        if services_found:
            # Take the first/best service found
            primary_service = services_found[0] if isinstance(services_found[0], str) else ""
            service_info["project_description"] = primary_service
            service_info["service_type"] = self._categorize_service(primary_service)
            service_info["confidence_scores"]["service_type"] = 0.9

        # Fallback: extract from general patterns
        if not services_found:
            general_patterns = [
                r"(?:need|needs|want|wants|for)\s+([^.]+?)(?:\s+(?:at|for|estimate))",
                r"(?:quote|estimate)\s+for\s+([^.]+?)(?:\.|$)"
            ]

            for pattern in general_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    service_description = match.group(1).strip()
                    service_info["project_description"] = service_description
                    service_info["service_type"] = self._categorize_service(service_description)
                    service_info["confidence_scores"]["service_type"] = 0.6
                    break

        return service_info

    def _extract_amount_info(self, text: str) -> Dict[str, Any]:
        """Extract monetary amounts with range detection"""
        amount_info = {"confidence_scores": {}}

        amounts_found = []

        for pattern in self.amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:  # Range pattern
                    low = self._parse_amount(match.group(1))
                    high = self._parse_amount(match.group(2)) if match.group(2) else low * 1.5
                    amounts_found.append(("range", low, high))
                else:
                    amount = self._parse_amount(match.group(1))
                    amounts_found.append(("single", amount, amount))

        # Handle written numbers
        written_amounts = self._extract_written_amounts(text)
        amounts_found.extend(written_amounts)

        if amounts_found:
            # Use the first reasonable amount found
            amount_type, low, high = amounts_found[0]

            if amount_type == "range":
                amount_info["amount_range"] = {"low": low, "high": high}
                amount_info["estimated_amount"] = (low + high) / 2
            else:
                amount_info["estimated_amount"] = low

            amount_info["confidence_scores"]["estimated_amount"] = 0.8

        return amount_info

    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""
        contact_info = {"confidence_scores": {}}

        # Extract phone numbers
        for pattern in self.contact_patterns[:2]:  # Phone patterns
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = self._clean_phone(match.group(1))
                if self._validate_phone(phone):
                    contact_info["contact_phone"] = phone
                    contact_info["confidence_scores"]["contact_phone"] = 0.9
                    break

        # Extract email addresses
        for pattern in self.contact_patterns[2:]:  # Email patterns
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                email = match.group(1).lower()
                if self._validate_email(email):
                    contact_info["contact_email"] = email
                    contact_info["confidence_scores"]["contact_email"] = 0.9
                    break

        return contact_info

    def _extract_urgency_info(self, text: str) -> Dict[str, Any]:
        """Extract urgency level with reasoning"""
        urgency_info = {}

        for level, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    urgency_info["urgency"] = level
                    urgency_info["urgency_reason"] = f"Detected: {pattern}"
                    return urgency_info

        urgency_info["urgency"] = "normal"
        return urgency_info

    def _extract_scope_details(self, text: str) -> Dict[str, Any]:
        """Extract project scope details"""
        scope_info = {"project_scope": {}, "special_notes": []}

        # Size indicators
        size_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:acre|acres)",
            r"(\d+(?:\.\d+)?)\s*(?:sq\s*ft|square\s*feet)",
            r"(small|medium|large|huge)\s+(?:yard|property|lot)"
        ]

        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scope_info["project_scope"]["size"] = match.group(1)
                break

        # Access difficulties
        access_patterns = [
            r"(?:hard to reach|difficult access|limited access|tight space)",
            r"(?:steep|hill|slope|incline)",
            r"(?:gate|fence|locked)"
        ]

        for pattern in access_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scope_info["special_notes"].append(f"Access consideration: {pattern}")

        # Equipment needs
        equipment_patterns = [
            r"(?:ladder|truck|equipment)",
            r"(?:heavy|large|small)\s+(?:equipment|tools)"
        ]

        for pattern in equipment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scope_info["special_notes"].append(f"Equipment note: {match.group(0)}")

        return scope_info

    def _score_client_name(self, candidate: str, match, full_text: str) -> float:
        """Score client name candidate"""
        score = 0.5  # Base score

        # Name-like patterns
        if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', candidate):
            score += 0.3

        # Context clues
        context_before = full_text[max(0, match.start()-20):match.start()]
        context_after = full_text[match.end():match.end()+20]

        if any(word in context_before.lower() for word in ["client", "customer", "for"]):
            score += 0.2

        if any(word in context_after.lower() for word in ["at", "lives", "wants"]):
            score += 0.1

        # Penalize common words
        if candidate.lower() in ["and", "the", "for", "at", "on", "in"]:
            score -= 0.5

        return min(1.0, max(0.0, score))

    def _score_address(self, candidate: str) -> float:
        """Score address candidate"""
        score = 0.5

        # Has street number
        if re.match(r'^\d+', candidate):
            score += 0.3

        # Has street type
        street_types = ["street", "st", "avenue", "ave", "road", "rd", "drive", "dr", "lane", "ln", "way", "blvd"]
        if any(st in candidate.lower() for st in street_types):
            score += 0.2

        # Has city
        cities = ["portland", "beaverton", "tigard", "lake oswego", "milwaukie", "gresham"]
        if any(city in candidate.lower() for city in cities):
            score += 0.2

        return min(1.0, score)

    def _categorize_service(self, service_text: str) -> str:
        """Categorize service type with confidence"""
        service_lower = service_text.lower()

        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.service_categories.items():
            score = sum(1 for keyword in keywords if keyword in service_lower)
            if score > 0:
                category_scores[category] = score

        if category_scores:
            return max(category_scores, key=category_scores.get)

        return "maintenance"  # Default category

    def _extract_written_amounts(self, text: str) -> List[Tuple[str, float, float]]:
        """Extract written number amounts"""
        amounts = []

        # "Five hundred" patterns
        hundred_pattern = r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+hundred"
        matches = re.finditer(hundred_pattern, text, re.IGNORECASE)

        for match in matches:
            number_word = match.group(1).lower()
            if number_word in self.written_numbers:
                amount = self.written_numbers[number_word] * 100
                amounts.append(("single", amount, amount))

        # "Five thousand" patterns
        thousand_pattern = r"(one|two|three|four|five|six|seven|eight|nine|ten)\s+thousand"
        matches = re.finditer(thousand_pattern, text, re.IGNORECASE)

        for match in matches:
            number_word = match.group(1).lower()
            if number_word in self.written_numbers:
                amount = self.written_numbers[number_word] * 1000
                amounts.append(("single", amount, amount))

        return amounts

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove commas and convert
            cleaned = amount_str.replace(',', '').replace('$', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0

    def _clean_name(self, name: str) -> str:
        """Clean and format client name"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())

        # Capitalize properly
        words = name.split()
        cleaned_words = []

        for word in words:
            if word.lower() in ["and", "or", "the"]:
                cleaned_words.append(word.lower())
            else:
                cleaned_words.append(word.capitalize())

        return ' '.join(cleaned_words)

    def _clean_address(self, address: str) -> str:
        """Clean and format address"""
        # Remove extra whitespace
        address = re.sub(r'\s+', ' ', address.strip())

        # Standardize street types
        street_abbrevs = {
            "street": "St", "avenue": "Ave", "road": "Rd", "drive": "Dr",
            "lane": "Ln", "way": "Way", "boulevard": "Blvd", "court": "Ct"
        }

        for full, abbrev in street_abbrevs.items():
            address = re.sub(r'\b' + full + r'\b', abbrev, address, flags=re.IGNORECASE)

        return address.title()

    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number"""
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        digits = re.sub(r'[^\d]', '', phone)
        return len(digits) in [10, 11]

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_and_enhance(self, extracted: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Validate and enhance extracted data"""

        # Cross-validate client name and address
        if extracted.get("client_name") and extracted.get("property_address"):
            name_confidence = extracted.get("confidence_scores", {}).get("client_name", 0)
            addr_confidence = extracted.get("confidence_scores", {}).get("property_address", 0)

            # If both are low confidence, flag for review
            if name_confidence < 0.6 and addr_confidence < 0.6:
                extracted["special_notes"].append("Low confidence on client and address - review recommended")

        # Validate service type against amount
        if extracted.get("estimated_amount") and extracted.get("service_type"):
            amount = extracted["estimated_amount"]
            service = extracted["service_type"]

            # Basic sanity checks
            if service == "cleanup" and amount > 2000:
                extracted["special_notes"].append("High amount for cleanup service - verify scope")
            elif service == "irrigation_repair" and amount < 100:
                extracted["special_notes"].append("Low amount for irrigation repair - verify scope")

        # Add missing required fields to notes
        required_fields = ["client_name", "project_description"]
        missing_fields = [field for field in required_fields if not extracted.get(field)]

        if missing_fields:
            extracted["special_notes"].append(f"Missing required fields: {', '.join(missing_fields)}")

        return extracted


def main():
    """Test the enhanced extractor"""
    test_transcriptions = [
        "This is an estimate for John Smith at 123 Oak Street. He needs fall cleanup for about $500. His phone is 503-555-1234.",
        "Quote for Jane Wilson, property at 456 Main Avenue in Portland. Irrigation repair needed urgently, around fifteen hundred dollars.",
        "Customer is ABC Landscaping LLC, located on Elm Drive. They want maintenance service, roughly $800 to $1000."
    ]

    extractor = EnhancedVoiceExtractor()

    for i, text in enumerate(test_transcriptions, 1):
        print(f"\n=== Test {i} ===")
        print(f"Input: {text}")

        result = extractor.extract_data(text)

        print(f"Client: {result.get('client_name')}")
        print(f"Address: {result.get('property_address')}")
        print(f"Service: {result.get('project_description')}")
        print(f"Amount: ${result.get('estimated_amount', 0):,.2f}")
        print(f"Confidence: {result.get('overall_confidence', 0):.2f}")


if __name__ == "__main__":
    main()