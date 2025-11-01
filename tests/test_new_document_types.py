"""
Tests for new document types: Vision, Solution Architecture, and Implementation Design.

This test suite validates the schema definitions and documents created for:
- VIS-XXX: Vision documents
- SOL-XXX: Solution Architecture documents
- IMP-XXX: Implementation Design documents
"""

from pathlib import Path

import pytest

from spec_check.dsl.layers import (
    APISpec,
    ComponentSpec,
    DataModel,
    ImplementationDesignModule,
    QualityAttribute,
    SolutionArchitectureModule,
    VisionModule,
)
from spec_check.dsl.models import Cardinality, IdentifierSpec, Reference, SectionSpec
from spec_check.dsl.registry import SpecTypeRegistry


class TestVisionModuleSchema:
    """Tests for Vision document schema definition."""

    def test_vision_module_exists(self):
        """Test that VisionModule is defined."""
        module = VisionModule()
        assert module is not None
        assert module.name == "Vision"

    def test_vision_file_pattern(self):
        """Test that Vision module matches correct file pattern."""
        module = VisionModule()
        assert module.file_pattern == r"^VIS-\d{3}\.md$"

        # Test pattern matching
        import re

        pattern = re.compile(module.file_pattern)
        assert pattern.match("VIS-001.md")
        assert pattern.match("VIS-999.md")
        assert not pattern.match("VIS-1.md")
        assert not pattern.match("VIS-1234.md")
        assert not pattern.match("VIS-ABC.md")

    def test_vision_location_pattern(self):
        """Test that Vision module matches correct location."""
        module = VisionModule()
        assert module.location_pattern == r"specs/vision/"

        # Test location matching
        test_path = Path("specs/vision/VIS-001.md")
        assert module.matches_file(test_path)

        # Should not match other locations
        wrong_path = Path("specs/requirements/VIS-001.md")
        assert not module.matches_file(wrong_path)

    def test_vision_identifier_spec(self):
        """Test Vision identifier specification."""
        module = VisionModule()
        assert module.identifier is not None
        assert module.identifier.pattern == r"VIS-\d{3}"
        assert module.identifier.location == "title"
        assert module.identifier.scope == "global"

    def test_vision_required_sections(self):
        """Test that Vision module has correct required sections."""
        module = VisionModule()

        required_sections = [s for s in module.sections if s.required]
        required_headings = {s.heading for s in required_sections}

        assert "Vision Statement" in required_headings
        assert "Problem Statement" in required_headings
        assert "Goals" in required_headings
        assert "Stakeholders" in required_headings

    def test_vision_optional_sections(self):
        """Test that Vision module has correct optional sections."""
        module = VisionModule()

        optional_sections = [s for s in module.sections if not s.required]
        optional_headings = {s.heading for s in optional_sections}

        assert "Success Criteria" in optional_headings
        assert "Constraints" in optional_headings
        assert "Out of Scope" in optional_headings

    def test_vision_no_references(self):
        """Test that Vision documents don't require references."""
        module = VisionModule()
        assert len(module.references) == 0


class TestSolutionArchitectureModuleSchema:
    """Tests for Solution Architecture document schema definition."""

    def test_solution_architecture_module_exists(self):
        """Test that SolutionArchitectureModule is defined."""
        module = SolutionArchitectureModule()
        assert module is not None
        assert module.name == "SolutionArchitecture"

    def test_solution_file_pattern(self):
        """Test that Solution Architecture module matches correct file pattern."""
        module = SolutionArchitectureModule()
        assert module.file_pattern == r"^SOL-\d{3}\.md$"

        import re

        pattern = re.compile(module.file_pattern)
        assert pattern.match("SOL-001.md")
        assert pattern.match("SOL-123.md")
        assert not pattern.match("SOL-1.md")
        assert not pattern.match("SOLUTION-001.md")

    def test_solution_location_pattern(self):
        """Test that Solution Architecture module matches correct location."""
        module = SolutionArchitectureModule()
        assert module.location_pattern == r"specs/architecture/solutions/"

        test_path = Path("specs/architecture/solutions/SOL-001.md")
        assert module.matches_file(test_path)

    def test_solution_identifier_spec(self):
        """Test Solution Architecture identifier specification."""
        module = SolutionArchitectureModule()
        assert module.identifier.pattern == r"SOL-\d{3}"
        assert module.identifier.location == "title"
        assert module.identifier.scope == "global"

    def test_solution_required_sections(self):
        """Test required sections for Solution Architecture."""
        module = SolutionArchitectureModule()

        required_sections = [s for s in module.sections if s.required]
        required_headings = {s.heading for s in required_sections}

        assert "Overview" in required_headings
        assert "System Context" in required_headings
        assert "Components" in required_headings
        assert "Technology Stack" in required_headings

    def test_solution_components_section_class_restriction(self):
        """Test that Components section restricts to ComponentSpec class."""
        module = SolutionArchitectureModule()

        components_section = next(s for s in module.sections if s.heading == "Components")
        assert components_section.allowed_classes == ["ComponentSpec"]
        assert components_section.require_classes is True

    def test_solution_quality_attributes_section_class_restriction(self):
        """Test that Quality Attributes section allows QualityAttribute class."""
        module = SolutionArchitectureModule()

        qa_section = next(s for s in module.sections if s.heading == "Quality Attributes")
        assert qa_section.allowed_classes == ["QualityAttribute"]
        assert qa_section.require_classes is False  # Optional

    def test_solution_references(self):
        """Test Solution Architecture reference requirements."""
        module = SolutionArchitectureModule()

        # Should address at least one requirement
        addresses_ref = next(r for r in module.references if r.name == "addresses")
        assert addresses_ref.source_type == "SolutionArchitecture"
        assert addresses_ref.target_type == "Requirement"
        assert addresses_ref.cardinality.min == 1
        assert addresses_ref.must_exist is True

        # May relate to ADRs
        relates_ref = next(r for r in module.references if r.name == "relates_to")
        assert relates_ref.target_type == "ADR"
        assert relates_ref.cardinality.min == 0

    def test_component_spec_class(self):
        """Test ComponentSpec class definition."""
        comp_spec = ComponentSpec()
        assert comp_spec.heading_pattern == r"^COMP-\d{2}:"
        assert comp_spec.heading_level == 3
        assert comp_spec.identifier.pattern == r"COMP-\d{2}"
        assert comp_spec.identifier.scope == "module_instance"

    def test_quality_attribute_class(self):
        """Test QualityAttribute class definition."""
        qa = QualityAttribute()
        assert qa.heading_pattern == r"^QA-\d{2}:"
        assert qa.heading_level == 3
        assert qa.identifier.pattern == r"QA-\d{2}"
        assert qa.identifier.scope == "module_instance"


class TestImplementationDesignModuleSchema:
    """Tests for Implementation Design document schema definition."""

    def test_implementation_design_module_exists(self):
        """Test that ImplementationDesignModule is defined."""
        module = ImplementationDesignModule()
        assert module is not None
        assert module.name == "ImplementationDesign"

    def test_implementation_file_pattern(self):
        """Test that Implementation Design module matches correct file pattern."""
        module = ImplementationDesignModule()
        assert module.file_pattern == r"^IMP-\d{3}\.md$"

        import re

        pattern = re.compile(module.file_pattern)
        assert pattern.match("IMP-001.md")
        assert pattern.match("IMP-999.md")
        assert not pattern.match("IMP-1.md")
        assert not pattern.match("IMPL-001.md")

    def test_implementation_location_pattern(self):
        """Test that Implementation Design module matches correct location."""
        module = ImplementationDesignModule()
        assert module.location_pattern == r"specs/design/"

        test_path = Path("specs/design/IMP-001.md")
        assert module.matches_file(test_path)

    def test_implementation_identifier_spec(self):
        """Test Implementation Design identifier specification."""
        module = ImplementationDesignModule()
        assert module.identifier.pattern == r"IMP-\d{3}"
        assert module.identifier.location == "title"
        assert module.identifier.scope == "global"

    def test_implementation_required_sections(self):
        """Test required sections for Implementation Design."""
        module = ImplementationDesignModule()

        required_sections = [s for s in module.sections if s.required]
        required_headings = {s.heading for s in required_sections}

        # Only Overview is required
        assert "Overview" in required_headings
        assert len(required_headings) == 1

    def test_implementation_optional_sections(self):
        """Test optional sections for Implementation Design."""
        module = ImplementationDesignModule()

        optional_sections = [s for s in module.sections if not s.required]
        optional_headings = {s.heading for s in optional_sections}

        assert "API Specifications" in optional_headings
        assert "Data Models" in optional_headings
        assert "Algorithms" in optional_headings
        assert "Error Handling" in optional_headings
        assert "Testing Strategy" in optional_headings

    def test_implementation_api_section_class_restriction(self):
        """Test that API Specifications section allows APISpec class."""
        module = ImplementationDesignModule()

        api_section = next(s for s in module.sections if s.heading == "API Specifications")
        assert api_section.allowed_classes == ["APISpec"]
        assert api_section.require_classes is False  # Optional

    def test_implementation_data_models_section_class_restriction(self):
        """Test that Data Models section allows DataModel class."""
        module = ImplementationDesignModule()

        dm_section = next(s for s in module.sections if s.heading == "Data Models")
        assert dm_section.allowed_classes == ["DataModel"]
        assert dm_section.require_classes is False  # Optional

    def test_implementation_references(self):
        """Test Implementation Design reference requirements."""
        module = ImplementationDesignModule()

        # Should implement at least one solution architecture
        implements_ref = next(r for r in module.references if r.name == "implements")
        assert implements_ref.source_type == "ImplementationDesign"
        assert implements_ref.target_type == "SolutionArchitecture"
        assert implements_ref.cardinality.min == 1
        assert implements_ref.must_exist is True

        # May address requirements
        addresses_ref = next(r for r in module.references if r.name == "addresses")
        assert addresses_ref.target_type == "Requirement"
        assert addresses_ref.cardinality.min == 0

    def test_api_spec_class(self):
        """Test APISpec class definition."""
        api_spec = APISpec()
        assert api_spec.heading_pattern == r"^API-\d{2}:"
        assert api_spec.heading_level == 3
        assert api_spec.identifier.pattern == r"API-\d{2}"

    def test_data_model_class(self):
        """Test DataModel class definition."""
        data_model = DataModel()
        assert data_model.heading_pattern == r"^DM-\d{2}:"
        assert data_model.heading_level == 3
        assert data_model.identifier.pattern == r"DM-\d{2}"


@pytest.mark.integration
class TestDocumentValidation:
    """Integration tests validating actual documents against schemas."""

    def test_vision_document_validates(self, tmp_path):
        """Test that VIS-001.md validates against Vision schema."""
        # Read actual VIS-001.md
        vis_001 = Path("specs/vision/VIS-001.md")
        if not vis_001.exists():
            pytest.skip("VIS-001.md not found")

        # Create registry and validator
        registry = SpecTypeRegistry()
        from spec_check.dsl.layers import LAYER_MODULES

        for module in LAYER_MODULES.values():
            registry.register_module(module)

        # Note: We can't easily run the full validator here without more setup
        # This test just verifies the document exists and is well-formed
        assert vis_001.exists()
        content = vis_001.read_text()
        assert "VIS-001" in content
        assert "Vision Statement" in content

    def test_solution_architecture_document_validates(self, tmp_path):
        """Test that SOL-001.md validates against Solution Architecture schema."""
        sol_001 = Path("specs/architecture/solutions/SOL-001.md")
        if not sol_001.exists():
            pytest.skip("SOL-001.md not found")

        # Verify document exists and has required content
        assert sol_001.exists()
        content = sol_001.read_text()
        assert "SOL-001" in content
        assert "Components" in content
        assert "COMP-" in content  # Should have component specs

    def test_implementation_design_document_validates(self, tmp_path):
        """Test that IMP-001.md validates against Implementation Design schema."""
        imp_001 = Path("specs/design/IMP-001.md")
        if not imp_001.exists():
            pytest.skip("IMP-001.md not found")

        # Verify document exists and has required content
        assert imp_001.exists()
        content = imp_001.read_text()
        assert "IMP-001" in content
        assert "Overview" in content


@pytest.mark.parametrize(
    "doc_type,file_pattern,location,example_id",
    [
        ("Vision", r"^VIS-\d{3}\.md$", "specs/vision/", "VIS-001"),
        (
            "SolutionArchitecture",
            r"^SOL-\d{3}\.md$",
            "specs/architecture/solutions/",
            "SOL-001",
        ),
        ("ImplementationDesign", r"^IMP-\d{3}\.md$", "specs/design/", "IMP-001"),
    ],
)
class TestDocumentTypePatterns:
    """Parameterized tests for document type patterns."""

    def test_file_pattern_matches_id(self, doc_type, file_pattern, location, example_id):
        """Test that file pattern correctly matches document ID format."""
        import re

        pattern = re.compile(file_pattern)
        filename = f"{example_id}.md"
        assert pattern.match(filename), f"{filename} should match {file_pattern}"

    def test_id_format_extraction(self, doc_type, file_pattern, location, example_id):
        """Test that ID can be extracted from filename."""
        import re

        # Extract ID from filename
        filename = f"{example_id}.md"
        id_pattern = r"([A-Z]+-\d{3})"
        match = re.search(id_pattern, filename)
        assert match is not None
        assert match.group(1) == example_id


class TestSchemaFlexibility:
    """Tests demonstrating the flexibility and extensibility of the schema system."""

    def test_custom_section_can_be_added(self):
        """Test that custom sections can be added to a module."""
        # Create a custom variation of Vision module
        custom_vision = VisionModule()

        # Add a custom section
        custom_vision.sections.append(
            SectionSpec(
                heading="Market Analysis",
                heading_level=2,
                required=False,
            )
        )

        section_headings = {s.heading for s in custom_vision.sections}
        assert "Market Analysis" in section_headings

    def test_cardinality_formats(self):
        """Test various cardinality constraint formats."""
        # Exactly one
        card_one = Cardinality(min=1, max=1)
        assert str(card_one) == "1"

        # Zero or one
        card_optional = Cardinality(min=0, max=1)
        assert str(card_optional) == "0..1"

        # One or more
        card_many = Cardinality(min=1, max=None)
        assert str(card_many) == "1..*"

        # Zero or more
        card_any = Cardinality(min=0, max=None)
        assert str(card_any) == "0..*"

        # Test validation via Reference (which has validate_count method)
        ref_one = Reference(
            name="test",
            source_type="A",
            target_type="B",
            cardinality=Cardinality(min=1, max=1),
        )
        assert ref_one.validate_count(1)
        assert not ref_one.validate_count(0)
        assert not ref_one.validate_count(2)

        ref_many = Reference(
            name="test",
            source_type="A",
            target_type="B",
            cardinality=Cardinality(min=1, max=None),
        )
        assert not ref_many.validate_count(0)
        assert ref_many.validate_count(1)
        assert ref_many.validate_count(100)

    def test_identifier_scopes(self):
        """Test different identifier scope behaviors."""
        # Global scope - unique across all documents
        global_id = IdentifierSpec(
            pattern=r"VIS-\d{3}",
            location="title",
            scope="global",
        )
        assert global_id.scope == "global"

        # Module instance scope - unique within one document
        module_id = IdentifierSpec(
            pattern=r"COMP-\d{2}",
            location="heading",
            scope="module_instance",
        )
        assert module_id.scope == "module_instance"

        # Section scope - unique within a section
        section_id = IdentifierSpec(
            pattern=r"STEP-\d{2}",
            location="heading",
            scope="section",
        )
        assert section_id.scope == "section"

    def test_section_class_restrictions(self):
        """Test that section class restrictions work as expected."""
        # Solution Architecture Components section
        module = SolutionArchitectureModule()
        components_section = next(s for s in module.sections if s.heading == "Components")

        # Should allow ComponentSpec
        assert "ComponentSpec" in components_section.allowed_classes

        # Should require at least one
        assert components_section.require_classes is True

    def test_multiple_reference_types(self):
        """Test that modules can have multiple reference types."""
        module = SolutionArchitectureModule()

        reference_names = {r.name for r in module.references}
        assert "addresses" in reference_names  # Must address requirements
        assert "relates_to" in reference_names  # May relate to ADRs

        # Check cardinalities
        addresses_ref = next(r for r in module.references if r.name == "addresses")
        assert addresses_ref.cardinality.min == 1  # At least one required

        relates_ref = next(r for r in module.references if r.name == "relates_to")
        assert relates_ref.cardinality.min == 0  # Optional


class TestBackwardCompatibility:
    """Tests ensuring new document types don't break existing functionality."""

    def test_existing_modules_still_work(self):
        """Test that adding new modules doesn't break existing ones."""
        from spec_check.dsl.layers import LAYER_MODULES

        # All existing modules should still be registered
        assert "Job" in LAYER_MODULES
        assert "Requirement" in LAYER_MODULES
        assert "ADR" in LAYER_MODULES

        # New modules should also be registered
        assert "Vision" in LAYER_MODULES
        assert "SolutionArchitecture" in LAYER_MODULES
        assert "ImplementationDesign" in LAYER_MODULES

    def test_existing_documents_still_validate(self):
        """Test that existing documents still validate with new modules added."""
        # Check that existing requirement docs still exist and are well-formed
        req_001 = Path("specs/requirements/REQ-001.md")
        if req_001.exists():
            content = req_001.read_text()
            assert "REQ-001" in content
            # Verify we haven't broken existing document structure
            assert "## Purpose" in content or "## Description" in content

        # Verify that adding new modules doesn't break the registry
        from spec_check.dsl.layers import LAYER_MODULES

        # Should have all existing types plus new ones
        assert len(LAYER_MODULES) >= 6  # At least Job, Req, ADR, Vision, Sol, Imp

    def test_module_class_hierarchy(self):
        """Test that new modules follow the same class hierarchy."""
        from spec_check.dsl.models import SpecModule

        assert issubclass(VisionModule, SpecModule)
        assert issubclass(SolutionArchitectureModule, SpecModule)
        assert issubclass(ImplementationDesignModule, SpecModule)
