"""Terminology Guardian Agent: Ensures consistent terminology."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class TerminologyGuardianAgent(BaseAgent):
    """
    Agent responsible for terminology consistency.
    
    Capabilities:
    - Build terminology glossary
    - Detect inconsistent terms
    - Suggest standardizations
    - Track acronyms
    """
    
    def __init__(self):
        super().__init__(
            name="terminology_guardian",
            role=AgentRole.QUALITY,
            description="Ensures consistent terminology throughout",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._glossary: dict[str, dict] = {}
        self._acronyms: dict[str, str] = {}
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute terminology guardian actions."""
        if action == "check":
            return await self._check_terminology(**kwargs)
        elif action == "build_glossary":
            return await self._build_glossary(**kwargs)
        elif action == "standardize":
            return await self._standardize_terms(**kwargs)
        elif action == "track_acronyms":
            return await self._track_acronyms(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _check_terminology(
        self,
        content: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Check terminology consistency."""
        
        # Get all content if not provided
        if not content:
            all_content = []
            for section_state in self.state.sections.values():
                if section_state.content:
                    all_content.append(section_state.content)
            content = "\n\n".join(all_content)
        
        if not content:
            return {"error": "No content to check"}
        
        # Build glossary first
        glossary = await self._build_glossary(content=content)
        
        # Track acronyms
        acronyms = await self._track_acronyms(content=content)
        
        # Find inconsistencies
        system_prompt = """You are a terminology consistency expert.
Identify terms used inconsistently throughout the text.
Look for:
- Same concept with different names
- Undefined acronyms
- Mixed capitalizations
- Spelling variations"""
        
        prompt = f"""Check terminology consistency:

## Content
{content[:6000]}

## Known Glossary
{json.dumps(glossary.get('terms', {}), indent=2)[:1000]}

## Output JSON
{{
    "inconsistencies": [
        {{
            "term": "inconsistent term",
            "variations": ["variation1", "variation2"],
            "suggested_standard": "preferred term",
            "severity": "high|medium|low"
        }}
    ],
    "undefined_acronyms": ["acronyms used without definition"],
    "consistency_score": <0.0-1.0>,
    "recommendations": ["specific fixes"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            result = json.loads(response.content)
            result["glossary"] = glossary
            result["acronyms"] = acronyms
            return result
        except json.JSONDecodeError:
            return {"inconsistencies": [], "consistency_score": 0.8}
    
    async def _build_glossary(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Build terminology glossary from content."""
        
        prompt = f"""Extract key terms and their definitions from this academic text:

{content[:5000]}

## Output JSON
{{
    "terms": {{
        "term_name": {{
            "definition": "how the term is used/defined in the text",
            "first_occurrence": "section where first used",
            "frequency": "high|medium|low"
        }}
    }},
    "domain_specific_terms": ["list of specialized terms"],
    "abbreviations": {{"abbrev": "full form"}}
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1200,
            json_mode=True
        )
        
        try:
            glossary = json.loads(response.content)
            self._glossary.update(glossary.get("terms", {}))
            return glossary
        except json.JSONDecodeError:
            return {"terms": {}, "domain_specific_terms": []}
    
    async def _track_acronyms(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Track acronyms and their definitions."""
        
        import re
        
        # Find potential acronyms (2-6 uppercase letters)
        acronyms = re.findall(r'\b([A-Z]{2,6})\b', content)
        unique_acronyms = list(set(acronyms))
        
        # Find definitions (full form followed by acronym in parentheses)
        definitions = re.findall(
            r'([A-Z][a-z]+(?:\s+[A-Za-z]+){1,5})\s*\(([A-Z]{2,6})\)',
            content
        )
        
        acronym_map = {}
        for full_form, abbrev in definitions:
            acronym_map[abbrev] = full_form
        
        # Find undefined acronyms
        undefined = [a for a in unique_acronyms if a not in acronym_map]
        
        self._acronyms.update(acronym_map)
        
        return {
            "defined_acronyms": acronym_map,
            "undefined_acronyms": undefined[:20],
            "total_acronyms_found": len(unique_acronyms)
        }
    
    async def _standardize_terms(
        self,
        content: str,
        standards: Optional[dict[str, str]] = None,
        **kwargs
    ) -> str:
        """Standardize terminology in content."""
        
        if not standards:
            return content
        
        # Create replacement prompt
        replacements_text = "\n".join([
            f"- Replace '{old}' with '{new}'"
            for old, new in standards.items()
        ])
        
        prompt = f"""Standardize terminology in this text:

## Standardizations Required
{replacements_text}

## Content
{content}

## Output
Return the text with terminology standardized.
Maintain all other content unchanged."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=len(content.split()) * 3
        )
        
        return response.content.strip()
    
    def get_glossary(self) -> dict:
        """Get current glossary."""
        return self._glossary
    
    def get_acronyms(self) -> dict:
        """Get tracked acronyms."""
        return self._acronyms
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add terminology guardian metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "terminology_checked": True,
                "consistency_score": result.output.get("consistency_score", 0),
                "issues_found": len(result.output.get("inconsistencies", []))
            }
        return result
