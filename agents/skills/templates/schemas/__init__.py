"""
ResearchFlow Schemas Package

JSON Schema validation for scoping review data.

Schemas:
    - data-charting-schema.json: Data charting form validation

Usage:
    from agents.skills.templates.schemas import validate_data_charting
    
    # Validate data
    data = {
        "study_id": "S001",
        "citation": {...},
        ...
    }
    
    errors = validate_data_charting(data)
    if errors:
        print("Validation errors:", errors)
"""

import json
from pathlib import Path
from typing import Any, Optional

SCHEMAS_DIR = Path(__file__).parent


def load_schema(schema_name: str) -> dict:
    """
    Load a JSON schema.
    
    Args:
        schema_name: Schema name without .json extension
        
    Returns:
        Schema as dictionary
    """
    path = SCHEMAS_DIR / f"{schema_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_schemas() -> list[str]:
    """List all available schemas."""
    schemas = []
    for file in SCHEMAS_DIR.iterdir():
        if file.is_file() and file.suffix == '.json':
            schemas.append(file.stem)
    return sorted(schemas)


def validate_json(data: dict, schema_name: str) -> list[str]:
    """
    Validate data against a JSON schema.
    
    Args:
        data: Data to validate
        schema_name: Schema name without .json extension
        
    Returns:
        List of validation error messages (empty if valid)
    """
    try:
        import jsonschema
        from jsonschema import validate as js_validate, ValidationError
    except ImportError:
        return ["jsonschema package not installed. Run: pip install jsonschema"]
    
    schema = load_schema(schema_name)
    
    errors = []
    try:
        js_validate(instance=data, schema=schema)
    except ValidationError as e:
        # Get path to the error
        path = " -> ".join(str(p) for p in e.absolute_path)
        errors.append(f"{path}: {e.message}" if path else e.message)
    except Exception as e:
        errors.append(str(e))
    
    return errors


def validate_data_charting(data: dict) -> list[str]:
    """
    Validate data charting form data.
    
    Args:
        data: Data charting data to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    return validate_json(data, "data-charting-schema")


def create_empty_data_charting() -> dict:
    """
    Create an empty data charting form structure matching the JSON schema.
    
    Returns:
        Empty data charting form with required fields
    """
    return {
        "study_id": "",
        "reviewer": "",
        "extraction_date": "",
        "double_checked": False,
        "bibliographic": {
            "authors": "",
            "year": None,
            "title": "",
            "journal": "",
            "volume": "",
            "issue": "",
            "pages": "",
            "doi": "",
            "publication_type": "article",
            "open_access": False
        },
        "methodology": {
            "study_design": {
                "type": "",
                "subtype": "",
                "data_collection": [],
                "analysis_method": ""
            },
            "sample": {
                "size": None,
                "response_rate": None,
                "demographics": ""
            },
            "context": {
                "countries": [],
                "industries": [],
                "organization_size": "",
                "sector": "",
                "data_collection_period": ""
            }
        },
        "pcc": {
            "population": {
                "primary": "",
                "secondary": "",
                "sample_description": ""
            },
            "concept": {
                "ai_technologies": [],
                "hr_functions": [],
                "psychosocial_risks": [],
                "organizational_culture_factors": [],
                "theoretical_frameworks": [],
                "other_concepts": ""
            },
            "context": {
                "geographic_scope": "",
                "organizational_context": "",
                "implementation_stage": "",
                "policy_environment": ""
            }
        },
        "findings": {
            "key_results": [],
            "effect_direction": "",
            "psychosocial_outcomes": {
                "positive": [],
                "negative": [],
                "neutral": []
            },
            "organizational_outcomes": {
                "positive": [],
                "negative": []
            },
            "recommendations": [],
            "limitations_noted": []
        },
        "quality_notes": "",
        "extraction_notes": ""
    }


__all__ = [
    "SCHEMAS_DIR",
    "load_schema",
    "list_schemas",
    "validate_json",
    "validate_data_charting",
    "create_empty_data_charting",
]
