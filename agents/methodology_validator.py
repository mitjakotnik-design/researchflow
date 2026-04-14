"""Methodology Validator Agent: Validates PRISMA-ScR compliance."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory
from config import PRISMASection, ComplianceLevel


logger = structlog.get_logger()


# PRISMA-ScR Checklist Items
PRISMA_SCR_CHECKLIST = {
    "title": {
        "item": 1,
        "description": "Identify the report as a scoping review",
        "section": "title"
    },
    "abstract_structured": {
        "item": 2,
        "description": "Provide a structured summary",
        "section": "abstract"
    },
    "rationale": {
        "item": 3,
        "description": "Describe the rationale for the review",
        "section": "introduction"
    },
    "objectives": {
        "item": 4,
        "description": "Provide explicit statement of objectives/research questions",
        "section": "introduction"
    },
    "protocol": {
        "item": 5,
        "description": "Indicate protocol registration/publication",
        "section": "methods"
    },
    "eligibility": {
        "item": 6,
        "description": "Specify eligibility criteria (PCC)",
        "section": "methods"
    },
    "information_sources": {
        "item": 7,
        "description": "Describe all information sources",
        "section": "methods"
    },
    "search": {
        "item": 8,
        "description": "Present full search strategy for at least one database",
        "section": "methods"
    },
    "selection": {
        "item": 9,
        "description": "Describe selection/screening process",
        "section": "methods"
    },
    "data_charting": {
        "item": 10,
        "description": "Describe data charting process",
        "section": "methods"
    },
    "data_items": {
        "item": 11,
        "description": "List and define data items extracted",
        "section": "methods"
    },
    "critical_appraisal": {
        "item": 12,
        "description": "Describe critical appraisal if conducted",
        "section": "methods"
    },
    "synthesis_methods": {
        "item": 13,
        "description": "Describe synthesis methods",
        "section": "methods"
    },
    "selection_results": {
        "item": 14,
        "description": "Report selection results with flow diagram",
        "section": "results"
    },
    "characteristics": {
        "item": 15,
        "description": "Report characteristics of included sources",
        "section": "results"
    },
    "critical_appraisal_results": {
        "item": 16,
        "description": "Present critical appraisal results",
        "section": "results"
    },
    "individual_results": {
        "item": 17,
        "description": "Present results for individual sources",
        "section": "results"
    },
    "synthesis_results": {
        "item": 18,
        "description": "Present synthesis results",
        "section": "results"
    },
    "limitations": {
        "item": 19,
        "description": "Discuss limitations",
        "section": "discussion"
    },
    "conclusions": {
        "item": 20,
        "description": "Provide summary and implications",
        "section": "discussion"
    },
    "funding": {
        "item": 21,
        "description": "Describe funding sources",
        "section": "other"
    },
    "conflicts": {
        "item": 22,
        "description": "Describe conflict of interest",
        "section": "other"
    }
}


class MethodologyValidatorAgent(BaseAgent):
    """
    Agent responsible for methodology validation.
    
    Capabilities:
    - Validate PRISMA-ScR compliance
    - Check methodological rigor
    - Assess reproducibility
    - Generate compliance report
    """
    
    def __init__(self):
        super().__init__(
            name="methodology_validator",
            role=AgentRole.QUALITY,
            description="Validates PRISMA-ScR compliance and methodological rigor",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._compliance_report: Optional[dict] = None
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute methodology validator actions."""
        if action == "validate":
            return await self._validate_methodology(**kwargs)
        elif action == "check_prisma":
            return await self._check_prisma_compliance(**kwargs)
        elif action == "check_rigor":
            return await self._check_methodological_rigor(**kwargs)
        elif action == "generate_report":
            return await self._generate_compliance_report(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _validate_methodology(self, **kwargs) -> dict:
        """Comprehensive methodology validation."""
        
        # Get all section content
        content_by_section = {}
        for section_id, section_state in self.state.sections.items():
            if section_state.content:
                content_by_section[section_id] = section_state.content
        
        if not content_by_section:
            return {"error": "No content to validate"}
        
        # PRISMA compliance check
        prisma_result = await self._check_prisma_compliance(
            content=content_by_section
        )
        
        # Methodological rigor check
        rigor_result = await self._check_methodological_rigor(
            methods_content=content_by_section.get("methods", "")
        )
        
        # Generate report
        report = await self._generate_compliance_report(
            prisma_result=prisma_result,
            rigor_result=rigor_result
        )
        
        self._compliance_report = report
        
        self.log.info(
            "methodology_validation_completed",
            prisma_items=prisma_result.get("items_met", 0),
            compliance_level=prisma_result.get("compliance_level", "unknown")
        )
        
        return report
    
    async def _check_prisma_compliance(
        self,
        content: dict[str, str],
        **kwargs
    ) -> dict:
        """Check PRISMA-ScR checklist compliance."""
        
        # Combine all content
        all_content = "\n\n".join([
            f"## {section}\n{text}" 
            for section, text in content.items()
        ])
        
        system_prompt = """You are a systematic review methodology expert.
Assess compliance with PRISMA-ScR (PRISMA Extension for Scoping Reviews) checklist.
Be strict but fair in your assessment."""
        
        # Check items in batches
        checklist_text = json.dumps(PRISMA_SCR_CHECKLIST, indent=2)
        
        prompt = f"""Assess PRISMA-ScR compliance:

## Article Content
{all_content[:8000]}

## PRISMA-ScR Checklist
{checklist_text}

## Output JSON
{{
    "item_compliance": {{
        "item_key": {{
            "met": true/false,
            "evidence": "where found or why not met",
            "quality": "full|partial|missing"
        }}
    }},
    "items_met": <number of fully met items>,
    "items_partial": <number of partially met>,
    "items_missing": <number of missing>,
    "compliance_level": "full|high|acceptable|low",
    "critical_gaps": ["most important missing items"],
    "recommendations": ["how to improve compliance"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            json_mode=True
        )
        
        try:
            result = json.loads(response.content)
            
            # Determine compliance level
            items_met = result.get("items_met", 0)
            if items_met >= 22:
                result["compliance_level"] = ComplianceLevel.FULL.value
            elif items_met >= 20:
                result["compliance_level"] = ComplianceLevel.HIGH.value
            elif items_met >= 18:
                result["compliance_level"] = ComplianceLevel.ACCEPTABLE.value
            else:
                result["compliance_level"] = ComplianceLevel.LOW.value
            
            return result
            
        except json.JSONDecodeError:
            return {
                "items_met": 0,
                "compliance_level": "unknown",
                "error": "Parsing failed"
            }
    
    async def _check_methodological_rigor(
        self,
        methods_content: str,
        **kwargs
    ) -> dict:
        """Check methodological rigor."""
        
        if not methods_content:
            return {"error": "No methods section to check"}
        
        prompt = f"""Assess methodological rigor of this methods section:

{methods_content[:4000]}

## Criteria
1. Search Strategy: Comprehensive, reproducible
2. Selection Process: Clear, systematic
3. Data Extraction: Standardized, complete
4. Quality Assessment: Appropriate tools used
5. Synthesis: Appropriate for scoping review

## Output JSON
{{
    "rigor_assessment": {{
        "search_strategy": {{
            "score": <1-10>,
            "strengths": ["what's good"],
            "weaknesses": ["what's missing"]
        }},
        "selection_process": {{
            "score": <1-10>,
            "strengths": [],
            "weaknesses": []
        }},
        "data_extraction": {{
            "score": <1-10>,
            "strengths": [],
            "weaknesses": []
        }},
        "quality_assessment": {{
            "score": <1-10>,
            "strengths": [],
            "weaknesses": []
        }},
        "synthesis_approach": {{
            "score": <1-10>,
            "strengths": [],
            "weaknesses": []
        }}
    }},
    "overall_rigor_score": <1-100>,
    "reproducibility_assessment": "high|moderate|low",
    "critical_improvements": ["most important fixes needed"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"overall_rigor_score": 50, "error": "Parsing failed"}
    
    async def _generate_compliance_report(
        self,
        prisma_result: dict,
        rigor_result: dict,
        **kwargs
    ) -> dict:
        """Generate comprehensive compliance report."""
        
        report = {
            "title": f"Methodology Compliance Report - {self.state.title[:50]}",
            "generated_at": "",  # Will be set by state manager
            "summary": {
                "prisma_compliance": prisma_result.get("compliance_level", "unknown"),
                "items_met": f"{prisma_result.get('items_met', 0)}/22",
                "methodological_rigor": rigor_result.get("overall_rigor_score", 0),
                "reproducibility": rigor_result.get("reproducibility_assessment", "unknown")
            },
            "prisma_details": prisma_result,
            "rigor_details": rigor_result,
            "overall_assessment": "",
            "action_items": []
        }
        
        # Generate overall assessment
        compliance = prisma_result.get("compliance_level", "unknown")
        rigor = rigor_result.get("overall_rigor_score", 0)
        
        if compliance in ["full", "high"] and rigor >= 80:
            report["overall_assessment"] = "Methodology meets high standards for scoping reviews."
        elif compliance in ["acceptable", "high"] and rigor >= 60:
            report["overall_assessment"] = "Methodology is acceptable but has areas for improvement."
        else:
            report["overall_assessment"] = "Methodology requires significant improvements before publication."
        
        # Compile action items
        action_items = []
        
        for gap in prisma_result.get("critical_gaps", []):
            action_items.append({
                "category": "PRISMA Compliance",
                "action": f"Address missing item: {gap}",
                "priority": "high"
            })
        
        for improvement in rigor_result.get("critical_improvements", []):
            action_items.append({
                "category": "Methodological Rigor",
                "action": improvement,
                "priority": "high"
            })
        
        report["action_items"] = action_items
        
        return report
    
    def get_compliance_report(self) -> Optional[dict]:
        """Get the stored compliance report."""
        return self._compliance_report
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add methodology validator metadata."""
        if isinstance(result.output, dict):
            summary = result.output.get("summary", {})
            result.handoff_data = {
                "validation_complete": True,
                "prisma_compliance": summary.get("prisma_compliance", "unknown"),
                "rigor_score": summary.get("methodological_rigor", 0),
                "action_items_count": len(result.output.get("action_items", []))
            }
            
            # If low compliance, suggest revisions
            if summary.get("prisma_compliance") == "low":
                result.suggested_next_agents = ["writer"]
        
        return result
