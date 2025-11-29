#!/usr/bin/env python3
"""
Template Engine Test Suite
Phase 4: Visual Capabilities - Template System Validation

Tests all template loading, parameter validation, and prompt generation.
"""

import pytest
import yaml
from pathlib import Path
from template_engine import (
    PromptTemplateEngine,
    PromptTemplate,
    get_template_engine,
    generate_prompt_from_template
)


# Test fixtures
@pytest.fixture
def engine():
    """Get template engine with default templates directory"""
    return PromptTemplateEngine()


@pytest.fixture
def template_dir():
    """Get templates directory path"""
    return Path(__file__).parent / "templates"


class TestTemplateLoading:
    """Tests for template file loading"""

    def test_list_templates(self, engine):
        """Should list all available templates"""
        templates = engine.list_templates()
        assert len(templates) >= 12, f"Expected at least 12 templates, got {len(templates)}"
        assert "irrigation_layout" in templates
        assert "deck_concept" in templates

    def test_load_valid_template(self, engine):
        """Should load a valid template"""
        template = engine.load_template("irrigation_layout")
        assert template.name == "Irrigation System Layout"
        assert template.base_prompt is not None
        assert len(template.parameters) > 0

    def test_load_nonexistent_template(self, engine):
        """Should raise error for missing template"""
        with pytest.raises(FileNotFoundError):
            engine.load_template("nonexistent_template")

    def test_template_caching(self, engine):
        """Should cache loaded templates"""
        template1 = engine.load_template("irrigation_layout")
        template2 = engine.load_template("irrigation_layout")
        assert template1 is template2


class TestAllTemplatesValid:
    """Validate all template files have correct format"""

    def test_all_templates_load(self, engine):
        """All templates should load without errors"""
        templates = engine.list_templates()
        for template_name in templates:
            template = engine.load_template(template_name)
            assert template.name, f"Template {template_name} missing name"
            assert template.description, f"Template {template_name} missing description"
            assert template.base_prompt, f"Template {template_name} missing base_prompt"
            assert template.parameters, f"Template {template_name} missing parameters"

    def test_all_templates_have_constraints(self, engine):
        """All templates should have parameter constraints"""
        templates = engine.list_templates()
        for template_name in templates:
            template = engine.load_template(template_name)
            # At least some parameters should have constraints
            assert len(template.constraints) > 0, \
                f"Template {template_name} has no constraints"

    def test_all_templates_have_negative_prompts(self, engine):
        """All templates should have negative prompts"""
        templates = engine.list_templates()
        for template_name in templates:
            template = engine.load_template(template_name)
            assert template.negative_prompt, \
                f"Template {template_name} missing negative_prompt"


class TestParameterValidation:
    """Tests for parameter validation"""

    def test_valid_parameters(self, engine):
        """Should accept valid parameters"""
        result = engine.generate_prompt(
            "irrigation_layout",
            {
                "num_zones": 5,
                "head_type": "rotary",
                "spacing": "10 feet",
                "coverage_type": "full",
                "property_size": "quarter acre",
                "style": "technical"
            }
        )
        assert "prompt" in result
        assert "5" in result["prompt"] or "five" in result["prompt"].lower()

    def test_missing_required_parameter(self, engine):
        """Should reject missing required parameters"""
        with pytest.raises(ValueError) as exc_info:
            engine.generate_prompt(
                "irrigation_layout",
                {"num_zones": 5}  # Missing other required params
            )
        assert "Missing required parameters" in str(exc_info.value)

    def test_invalid_enum_value(self, engine):
        """Should reject invalid enum values"""
        with pytest.raises(ValueError) as exc_info:
            engine.generate_prompt(
                "irrigation_layout",
                {
                    "num_zones": 5,
                    "head_type": "invalid_type",  # Not in enum
                    "spacing": "10 feet",
                    "coverage_type": "full",
                    "property_size": "quarter acre",
                    "style": "technical"
                }
            )
        assert "must be one of" in str(exc_info.value)

    def test_invalid_range_value(self, engine):
        """Should reject out-of-range values"""
        with pytest.raises(ValueError) as exc_info:
            engine.generate_prompt(
                "irrigation_layout",
                {
                    "num_zones": 100,  # Over max of 20
                    "head_type": "rotary",
                    "spacing": "10 feet",
                    "coverage_type": "full",
                    "property_size": "quarter acre",
                    "style": "technical"
                }
            )
        assert "must be <=" in str(exc_info.value)


class TestPromptGeneration:
    """Tests for prompt generation"""

    def test_basic_generation(self, engine):
        """Should generate prompt with substituted parameters"""
        result = engine.generate_prompt(
            "deck_concept",
            {
                "material": "composite",
                "size": "400 square feet",
                "features": "built-in seating",
                "style": "modern",
                "railing_type": "cable"
            }
        )
        assert "composite" in result["prompt"]
        assert "modern" in result["prompt"]
        assert "negative_prompt" in result

    def test_style_modifier(self, engine):
        """Should add style modifier to prompt"""
        result = engine.generate_prompt(
            "irrigation_layout",
            {
                "num_zones": 5,
                "head_type": "rotary",
                "spacing": "10 feet",
                "coverage_type": "full",
                "property_size": "quarter acre",
                "style": "technical"
            },
            style="blueprint"
        )
        assert "blueprint style" in result["prompt"]

    def test_additional_context(self, engine):
        """Should append additional context"""
        result = engine.generate_prompt(
            "irrigation_layout",
            {
                "num_zones": 5,
                "head_type": "rotary",
                "spacing": "10 feet",
                "coverage_type": "full",
                "property_size": "quarter acre",
                "style": "technical"
            },
            additional_context="Arizona desert climate"
        )
        assert "Arizona desert climate" in result["prompt"]


class TestTemplateInfo:
    """Tests for template metadata retrieval"""

    def test_get_template_info(self, engine):
        """Should return template metadata"""
        info = engine.get_template_info("irrigation_layout")
        assert info["name"] == "Irrigation System Layout"
        assert "parameters" in info
        assert "constraints" in info
        assert "style_modifiers" in info

    def test_info_contains_all_parameters(self, engine):
        """Template info should list all parameters"""
        info = engine.get_template_info("irrigation_layout")
        param_names = list(info["parameters"].keys())
        assert "num_zones" in param_names
        assert "head_type" in param_names


class TestModuleFunctions:
    """Tests for module-level convenience functions"""

    def test_get_template_engine_singleton(self):
        """Should return singleton instance"""
        engine1 = get_template_engine()
        engine2 = get_template_engine()
        assert engine1 is engine2

    def test_generate_prompt_convenience(self):
        """Convenience function should work"""
        result = generate_prompt_from_template(
            "deck_concept",
            {
                "material": "wood",
                "size": "300 square feet",
                "features": "stairs",
                "style": "traditional",
                "railing_type": "wood"
            }
        )
        assert "prompt" in result
        assert "wood" in result["prompt"]


class TestNewTemplates:
    """Tests for newly added templates in Phase 4"""

    def test_fence_design_template(self, engine):
        """Fence design template should work"""
        result = engine.generate_prompt(
            "fence_design",
            {
                "material": "wood",
                "height": "6 feet",
                "style": "privacy",
                "feature": "gate",
                "length": "100 feet"
            }
        )
        assert "wood" in result["prompt"]
        assert "privacy" in result["prompt"]

    def test_patio_layout_template(self, engine):
        """Patio layout template should work"""
        result = engine.generate_prompt(
            "patio_layout",
            {
                "material": "concrete pavers",
                "pattern": "herringbone",
                "size": "400 square feet",
                "shape": "rectangular",
                "edge_treatment": "soldier course",
                "furniture": "dining set"
            }
        )
        assert "herringbone" in result["prompt"]

    def test_landscape_lighting_template(self, engine):
        """Landscape lighting template should work"""
        result = engine.generate_prompt(
            "landscape_lighting",
            {
                "time": "evening",
                "fixture_type": "path lights",
                "lighting_style": "ambient",
                "focus_area": "pathway",
                "num_fixtures": 12
            }
        )
        assert "evening" in result["prompt"]
        assert "path lights" in result["prompt"]

    def test_water_feature_template(self, engine):
        """Water feature template should work"""
        result = engine.generate_prompt(
            "water_feature",
            {
                "feature_type": "fountain",
                "size": "medium focal point",
                "material": "natural stone",
                "style": "naturalistic",
                "water_effect": "cascading",
                "surrounding": "native plants"
            }
        )
        assert "fountain" in result["prompt"]
        assert "cascading" in result["prompt"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
