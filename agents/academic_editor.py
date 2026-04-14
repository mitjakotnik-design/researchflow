"""Academic Editor Agent: Edits for academic style and clarity."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class AcademicEditorAgent(BaseAgent):
    """
    Agent responsible for academic editing.
    
    Capabilities:
    - Improve academic writing style
    - Ensure clarity and precision
    - Fix grammar and punctuation
    - Enhance readability
    """
    
    def __init__(self):
        super().__init__(
            name="academic_editor",
            role=AgentRole.WRITING,
            description="Edits for academic style and clarity",
            version="1.0.0"
        )
        
        self._llm_client = None
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute academic editor actions."""
        if action == "edit":
            return await self._edit_content(**kwargs)
        elif action == "check_style":
            return await self._check_style(**kwargs)
        elif action == "improve_clarity":
            return await self._improve_clarity(**kwargs)
        elif action == "polish":
            return await self._polish_section(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _edit_content(
        self,
        content: Optional[str] = None,
        section: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Edit content for academic quality."""
        
        # Get content from state if not provided
        if not content and section:
            section_state = self.state.sections.get(section)
            if section_state:
                content = section_state.content
        
        if not content:
            return {"error": "No content to edit"}
        
        # Check style issues
        style_issues = await self._check_style(content=content)
        
        # Improve clarity
        improved = await self._improve_clarity(content=content)
        
        # Polish final version
        polished = await self._polish_section(content=improved)
        
        self.log.info(
            "editing_completed",
            section=section,
            issues_found=len(style_issues.get("issues", []))
        )
        
        return {
            "edited_content": polished,
            "style_issues": style_issues,
            "changes_made": style_issues.get("issues", []),
            "word_count": len(polished.split())
        }
    
    async def _check_style(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Check for style issues."""
        
        system_prompt = """You are an academic writing style checker.
Identify issues with:
- Passive voice overuse
- Hedging language
- Wordiness
- Informal language
- Unclear references
- Sentence structure problems"""
        
        prompt = f"""Check this academic text for style issues:

{content[:4000]}

## Output JSON
{{
    "issues": [
        {{
            "type": "passive_voice|wordiness|informal|unclear|structure",
            "text": "problematic phrase",
            "suggestion": "improved version",
            "location": "approximate location"
        }}
    ],
    "overall_quality": "excellent|good|acceptable|needs_work",
    "readability_score": <1-10>,
    "main_recommendations": ["top 3 improvements needed"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"issues": [], "overall_quality": "unknown"}
    
    async def _improve_clarity(
        self,
        content: str,
        **kwargs
    ) -> str:
        """Improve text clarity."""
        
        system_prompt = """You are an academic text clarity specialist.
Improve clarity while maintaining:
- Academic tone
- Precise terminology
- Original meaning
- Citation formats
Only make necessary changes."""
        
        prompt = f"""Improve the clarity of this academic text:

{content}

## Guidelines
- Simplify complex sentences
- Remove redundancy
- Clarify ambiguous references
- Maintain academic register
- Preserve all citations

## Output
Return the improved text only, no commentary."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=len(content.split()) * 3
        )
        
        return response.content.strip()
    
    async def _polish_section(
        self,
        content: str,
        **kwargs
    ) -> str:
        """Final polish of section."""
        
        prompt = f"""Polish this academic text for final publication:

{content}

## Polish Guidelines
- Fix any remaining grammar issues
- Ensure consistent tense usage
- Check subject-verb agreement
- Smooth transitions between paragraphs
- Maintain scholarly tone

## Output
Return the polished text only."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=len(content.split()) * 3
        )
        
        return response.content.strip()
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add editor metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "editing_complete": True,
                "quality": result.output.get("style_issues", {}).get("overall_quality", "unknown")
            }
        return result
