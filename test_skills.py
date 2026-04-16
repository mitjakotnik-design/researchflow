#!/usr/bin/env python3
"""
ResearchFlow Skills Test Suite

Comprehensive tests for skills, templates, schemas, and integration.

Usage:
    # Run all tests
    python test_skills.py
    
    # Run with pytest (if installed)
    pytest test_skills.py -v
"""

import sys
import os
import json
import yaml
import unittest
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestSkillLoader(unittest.TestCase):
    """Tests for skill_loader.py functionality."""
    
    def test_import_skill_loader(self):
        """Test that skill_loader can be imported."""
        from agents import get_skill, list_all_skills, get_system_prompt
        self.assertTrue(callable(get_skill))
        self.assertTrue(callable(list_all_skills))
        self.assertTrue(callable(get_system_prompt))
    
    def test_list_all_skills(self):
        """Test that all 20 skills are discovered."""
        from agents import list_all_skills
        skills = list_all_skills()
        
        self.assertIsInstance(skills, list)
        self.assertEqual(len(skills), 20, f"Expected 20 skills, got {len(skills)}")
        
        # Check cluster entry points exist
        self.assertIn("research-cluster", skills)
        self.assertIn("writing-cluster", skills)
        self.assertIn("quality-cluster", skills)
    
    def test_load_skill_metadata(self):
        """Test that skill metadata is parsed correctly."""
        from agents import get_skill
        
        skill = get_skill("research-cluster/researcher")
        
        self.assertEqual(skill.name, "researcher")
        self.assertIsNotNone(skill.description)
        self.assertIsNotNone(skill.file_path)
        self.assertEqual(skill.cluster, "research-cluster")
        self.assertEqual(skill.agent_name, "researcher")
    
    def test_get_system_prompt(self):
        """Test system prompt extraction."""
        from agents import get_system_prompt
        
        prompt = get_system_prompt("researcher")
        
        self.assertIsNotNone(prompt)
        self.assertIn("scoping review", prompt.lower())
    
    def test_skill_caching(self):
        """Test that skills are cached properly."""
        from agents.skill_loader import SkillLoader
        
        loader = SkillLoader()
        skill1 = loader.load_skill("research-cluster")
        skill2 = loader.load_skill("research-cluster")
        
        # Should be same object (cached)
        self.assertIs(skill1, skill2)
    
    def test_all_skills_have_required_fields(self):
        """Test that all skills have required YAML fields."""
        from agents import list_all_skills, get_skill
        
        for skill_path in list_all_skills():
            with self.subTest(skill=skill_path):
                skill = get_skill(skill_path)
                self.assertIsNotNone(skill.name, f"{skill_path}: missing name")
                self.assertIsNotNone(skill.description, f"{skill_path}: missing description")


class TestTemplates(unittest.TestCase):
    """Tests for templates functionality."""
    
    def test_import_templates(self):
        """Test that templates module can be imported."""
        from agents.skills import list_templates, load_template
        self.assertTrue(callable(list_templates))
        self.assertTrue(callable(load_template))
    
    def test_list_templates(self):
        """Test that templates are discovered."""
        from agents.skills import list_templates
        templates = list_templates()
        
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 5)
        
        # Check key templates exist
        self.assertIn("data-charting-form", templates)
        self.assertIn("screening-form", templates)
        self.assertIn("prisma-scr-checklist", templates)
    
    def test_load_template(self):
        """Test template loading."""
        from agents.skills import load_template
        
        content = load_template("data-charting-form")
        
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 1000)
        self.assertIn("Data Charting", content)
    
    def test_template_not_found(self):
        """Test error handling for missing template."""
        from agents.skills import load_template
        
        with self.assertRaises(FileNotFoundError):
            load_template("nonexistent-template")


class TestSchemas(unittest.TestCase):
    """Tests for schema validation functionality."""
    
    def test_import_schemas(self):
        """Test that schemas module can be imported."""
        from agents.skills.templates.schemas import (
            list_schemas,
            load_schema,
            validate_data_charting,
            create_empty_data_charting
        )
        self.assertTrue(callable(list_schemas))
        self.assertTrue(callable(load_schema))
        self.assertTrue(callable(validate_data_charting))
        self.assertTrue(callable(create_empty_data_charting))
    
    def test_list_schemas(self):
        """Test that schemas are discovered."""
        from agents.skills.templates.schemas import list_schemas
        schemas = list_schemas()
        
        self.assertIsInstance(schemas, list)
        self.assertIn("data-charting-schema", schemas)
    
    def test_load_schema(self):
        """Test schema loading."""
        from agents.skills.templates.schemas import load_schema
        
        schema = load_schema("data-charting-schema")
        
        self.assertIsInstance(schema, dict)
        self.assertIn("$schema", schema)
        self.assertIn("properties", schema)
    
    def test_create_empty_data_charting(self):
        """Test empty form creation."""
        from agents.skills.templates.schemas import create_empty_data_charting
        
        form = create_empty_data_charting()
        
        self.assertIsInstance(form, dict)
        # Check required top-level fields matching JSON schema
        self.assertIn("study_id", form)
        self.assertIn("reviewer", form)
        self.assertIn("extraction_date", form)
        self.assertIn("bibliographic", form)
        self.assertIn("methodology", form)
        self.assertIn("pcc", form)
        self.assertIn("findings", form)
    
    def test_validate_valid_data(self):
        """Test validation with valid data."""
        from agents.skills.templates.schemas import validate_data_charting
        
        # Valid data matching the schema structure
        valid_data = {
            "study_id": "Smith2024a",
            "reviewer": "John Doe",
            "extraction_date": "2024-04-16",
            "bibliographic": {
                "authors": "Smith, J.; Doe, A.",
                "year": 2024,
                "title": "Test Study on AI in HR"
            },
            "methodology": {
                "study_design": {
                    "type": "quantitative",
                    "subtype": "cross-sectional",
                    "data_collection": ["survey"]
                }
            },
            "pcc": {
                "population": {
                    "primary": "HR professionals"
                },
                "concept": {
                    "ai_technologies": ["machine_learning"],
                    "hr_functions": ["recruitment"]
                },
                "context": {
                    "geographic_scope": "North America"
                }
            }
        }
        
        errors = validate_data_charting(valid_data)
        self.assertEqual(len(errors), 0, f"Expected no errors, got: {errors}")


class TestSkillMDFormat(unittest.TestCase):
    """Tests for SKILL.md file format validity."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skills_dir = PROJECT_ROOT / "agents" / "skills"
        # Accept both Slovenian and English section names
        self.required_sections = [("## Opis", "## Vloga"), ("## Akcije", "## Actions")]
    
    def get_all_skill_files(self) -> List[Path]:
        """Get all SKILL.md files."""
        skill_files = []
        for pattern in ["**/SKILL.md"]:
            skill_files.extend(self.skills_dir.glob(pattern))
        return skill_files
    
    def test_all_skills_have_valid_yaml(self):
        """Test that all SKILL.md files have valid YAML frontmatter."""
        import re
        
        for skill_file in self.get_all_skill_files():
            with self.subTest(file=str(skill_file)):
                content = skill_file.read_text(encoding='utf-8')
                
                # Check for YAML frontmatter
                yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                self.assertIsNotNone(yaml_match, f"No YAML frontmatter in {skill_file.name}")
                
                # Parse YAML
                try:
                    frontmatter = yaml.safe_load(yaml_match.group(1))
                except yaml.YAMLError as e:
                    self.fail(f"Invalid YAML in {skill_file}: {e}")
                
                # Check required fields
                self.assertIn("name", frontmatter, f"Missing 'name' in {skill_file}")
                self.assertIn("description", frontmatter, f"Missing 'description' in {skill_file}")
    
    def test_agent_skills_have_all_sections(self):
        """Test that agent SKILL.md files have required sections."""
        import re
        
        # Only test agent-level skills (not cluster entry points)
        for skill_file in self.get_all_skill_files():
            # Skip cluster entry points
            if skill_file.parent.name.endswith("-cluster"):
                continue
            
            with self.subTest(file=str(skill_file)):
                content = skill_file.read_text(encoding='utf-8')
                
                # Check for key sections (accept multiple alternatives)
                for section_alternatives in self.required_sections:
                    if isinstance(section_alternatives, tuple):
                        found = any(alt in content for alt in section_alternatives)
                        self.assertTrue(
                            found,
                            f"Missing any of {section_alternatives} in {skill_file.relative_to(self.skills_dir)}"
                        )
                    else:
                        self.assertIn(
                            section_alternatives, content,
                            f"Missing '{section_alternatives}' in {skill_file.relative_to(self.skills_dir)}"
                        )


class TestConfigYAML(unittest.TestCase):
    """Tests for config.yaml validity."""
    
    def test_config_exists(self):
        """Test that config.yaml exists."""
        config_path = PROJECT_ROOT / "agents" / "skills" / "config.yaml"
        self.assertTrue(config_path.exists(), "config.yaml not found")
    
    def test_config_valid_yaml(self):
        """Test that config.yaml is valid YAML."""
        config_path = PROJECT_ROOT / "agents" / "skills" / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.fail(f"Invalid YAML in config.yaml: {e}")
        
        self.assertIsInstance(config, dict)
    
    def test_config_has_required_sections(self):
        """Test that config.yaml has required sections."""
        from agents.skill_loader import load_config
        
        config = load_config()
        
        # Check for actual keys in the config
        expected_sections = ["models", "quality", "timeouts"]
        for section in expected_sections:
            self.assertIn(section, config, f"Missing '{section}' in config.yaml")


class TestIntegration(unittest.TestCase):
    """Integration tests for the full system."""
    
    def test_skill_to_agent_mapping(self):
        """Test that skills map to existing agents."""
        from agents import list_all_skills, get_skill
        
        # Map skill names to agent class names
        agent_skill_map = {
            "researcher": "ResearcherAgent",
            "writer": "WriterAgent",
            "data-extractor": "DataExtractorAgent",
            "meta-analyst": "MetaAnalystAgent",
            "multi-evaluator": "MultiEvaluatorAgent",
        }
        
        for skill_path in list_all_skills():
            if "/" in skill_path:
                agent_name = skill_path.split("/")[1]
                if agent_name in agent_skill_map:
                    with self.subTest(agent=agent_name):
                        skill = get_skill(skill_path)
                        self.assertIsNotNone(skill.description)
    
    def test_full_workflow_import(self):
        """Test that full workflow can be set up."""
        from agents import (
            get_skill,
            get_system_prompt,
            list_all_skills,
            SkillLoader,
            SkillMetadata
        )
        from agents.skills import (
            list_templates,
            load_template
        )
        from agents.skills.templates.schemas import (
            validate_data_charting,
            create_empty_data_charting
        )
        
        # All imports should work
        self.assertTrue(True)


class TestScriptsIntegration(unittest.TestCase):
    """Tests for IRR calculator and PRISMA generator."""
    
    def test_irr_calculator_import(self):
        """Test that IRR calculator can be imported."""
        try:
            from agents.skills.templates.scripts import calculate_kappa
            self.assertTrue(callable(calculate_kappa))
        except ImportError as e:
            self.skipTest(f"IRR calculator dependencies not installed: {e}")
    
    def test_prisma_generator_import(self):
        """Test that PRISMA generator can be imported."""
        try:
            from agents.skills.templates.scripts import generate_prisma_diagram
            self.assertTrue(callable(generate_prisma_diagram))
        except ImportError as e:
            self.skipTest(f"PRISMA generator dependencies not installed: {e}")
    
    def test_irr_calculation(self):
        """Test IRR calculation with sample data."""
        try:
            from agents.skills.templates.scripts import quick_kappa
            
            rater1 = ["include", "include", "exclude", "include", "exclude"]
            rater2 = ["include", "exclude", "exclude", "include", "exclude"]
            
            result = quick_kappa(rater1, rater2)
            
            self.assertIn("kappa", result)
            self.assertIn("percent_agreement", result)
            self.assertIn("interpretation", result)
            
            self.assertGreaterEqual(result["kappa"], -1)
            self.assertLessEqual(result["kappa"], 1)
            
        except ImportError:
            self.skipTest("IRR calculator dependencies not installed")
    
    def test_prisma_ascii_generation(self):
        """Test PRISMA ASCII diagram generation."""
        try:
            from agents.skills.templates.scripts import generate_prisma_diagram
            
            counts = {
                "identified": 100,
                "duplicates_removed": 20,
                "screened": 80,
                "excluded_screening": 50,
                "sought_retrieval": 30,
                "not_retrieved": 5,
                "assessed_eligibility": 25,
                "excluded_eligibility": 15,
                "included": 10
            }
            
            diagram = generate_prisma_diagram(counts, format="ascii")
            
            self.assertIsInstance(diagram, str)
            self.assertIn("IDENTIFICATION", diagram)
            self.assertIn("SCREENING", diagram)
            self.assertIn("INCLUDED", diagram)
            
        except ImportError:
            self.skipTest("PRISMA generator dependencies not installed")


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSkillLoader,
        TestTemplates,
        TestSchemas,
        TestSkillMDFormat,
        TestConfigYAML,
        TestIntegration,
        TestScriptsIntegration,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
