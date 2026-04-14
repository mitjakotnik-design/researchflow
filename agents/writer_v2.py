"""
Writer Agent V2: Enhanced version with DI, retry, and validation.

This is the new version of WriterAgent that uses:
- Dependency Injection for all dependencies
- Pydantic validation for inputs
- Built-in retry with exponential backoff
- Circuit breaker for resilience
- Rate limiting for API calls
"""

from typing import Any, Optional
from pydantic import BaseModel, Field

import structlog

from agents.base_agent_v2 import EnhancedBaseAgent, AgentDependencies, AgentRole
from agents.request_models import WriteSectionRequest, ReviseSectionRequest, get_request_model
from core.retry import retry_llm_call


logger = structlog.get_logger()


class WriterAgentV2(EnhancedBaseAgent):
    """
    Enhanced Writer Agent with dependency injection and resilience.
    
    Capabilities:
    - Generate initial drafts based on research
    - Revise content based on feedback
    - Maintain academic writing standards
    - Follow PRISMA-ScR guidelines
    """
    
    def __init__(self, deps: AgentDependencies):
        super().__init__(
            name="writer",
            role=AgentRole.WRITING,
            deps=deps,
            description="Generates and revises scientific article sections",
            version="2.0.0"
        )
        
        # Section-specific system prompts
        self._section_prompts = {
            "introduction": self._get_introduction_prompt(),
            "methods": self._get_methods_prompt(),
            "results": self._get_results_prompt(),
            "discussion": self._get_discussion_prompt(),
            "conclusion": self._get_conclusion_prompt(),
        }
    
    def get_request_model(self, action: str) -> Optional[type[BaseModel]]:
        """Get Pydantic model for action validation."""
        return get_request_model("writer", action)
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute writer actions."""
        if action == "write_section":
            return await self._write_section(**kwargs)
        elif action == "revise_section":
            return await self._revise_section(**kwargs)
        elif action == "expand":
            return await self._expand_content(**kwargs)
        elif action == "condense":
            return await self._condense_content(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _write_section(
        self,
        section_id: str,
        section_name: str,
        min_words: int,
        max_words: int,
        guidelines: str = "",
        avoid: str = "",
        research_context: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Generate initial section draft with research integration."""
        
        # Get research context from RAG if not provided
        if not research_context and self._rag:
            title = self.article_state.title if self.article_state else "AI in HR"
            rag_results = await self.query_rag(
                query=f"Research for {section_name} section about {title}",
                top_k=15
            )
            research_context = self._format_rag_results(rag_results)
        
        # Get section-specific system prompt
        system_prompt = self._section_prompts.get(
            section_id,
            self._get_default_prompt()
        )
        
        title = self.article_state.title if self.article_state else "Scoping Review"
        
        prompt = f"""Write the {section_name} section for a scoping review article.

## Article Title
{title}

## Section Requirements
- Word count: {min_words}-{max_words} words
- Academic writing style
- Follow PRISMA-ScR guidelines

## Content Guidelines
{guidelines or "Follow standard academic conventions."}

## What to Avoid
{avoid or "Avoid informal language and unsupported claims."}

## Research Context
{research_context or "No additional context available."}

## Output Format
Write the complete section content. Use proper academic structure with paragraphs.
Include in-text citations in [Author, Year] format where appropriate.

Begin writing:"""
        
        # Generate with retry (handled by base class)
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_words * 2
        )
        
        content = response.content.strip()
        word_count = len(content.split())
        
        self.log.info(
            "section_written",
            section=section_id,
            word_count=word_count,
            tokens_used=response.input_tokens + response.output_tokens
        )
        
        return {
            "content": content,
            "word_count": word_count,
            "section_id": section_id,
            "tokens_used": response.input_tokens + response.output_tokens,
            "model": response.model,
        }
    
    async def _revise_section(
        self,
        section_id: str,
        current_content: str,
        feedback: str,
        improvement_focus: Optional[list[str]] = None,
        preserve_citations: bool = True,
        **kwargs
    ) -> dict:
        """Revise section based on feedback."""
        
        system_prompt = """You are an expert academic editor revising a scientific article.
Maintain the overall structure while addressing the feedback.
Preserve citations and factual claims unless specifically asked to change them.
Improve clarity, coherence, and academic rigor."""
        
        focus_text = ""
        if improvement_focus:
            focus_text = "\n## Priority Focus Areas\n" + "\n".join(
                f"- {area}" for area in improvement_focus
            )
        
        prompt = f"""Revise this section based on the feedback provided.

## Current Content
{current_content}

## Feedback to Address
{feedback}
{focus_text}

## Revision Guidelines
- Address the most critical issues first
- Maintain word count within 10% of current
- {"Preserve accurate citations" if preserve_citations else "Update citations as needed"}
- Improve clarity and flow

## Output
Provide the revised section in full. Do not include meta-commentary about the changes."""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=len(current_content.split()) * 3
        )
        
        revised_content = response.content.strip()
        
        self.log.info(
            "section_revised",
            section=section_id,
            original_words=len(current_content.split()),
            revised_words=len(revised_content.split())
        )
        
        return {
            "content": revised_content,
            "original_word_count": len(current_content.split()),
            "revised_word_count": len(revised_content.split()),
            "section_id": section_id,
        }
    
    async def _expand_content(
        self,
        content: str,
        target_words: int,
        focus_areas: Optional[list[str]] = None,
        **kwargs
    ) -> dict:
        """Expand content to meet word count."""
        current_words = len(content.split())
        
        if current_words >= target_words:
            return {
                "content": content,
                "word_count": current_words,
                "expanded": False,
            }
        
        focus_text = ""
        if focus_areas:
            focus_text = "\n## Areas to Expand\n" + "\n".join(
                f"- {area}" for area in focus_areas
            )
        
        prompt = f"""Expand this content to approximately {target_words} words.

## Current Content ({current_words} words)
{content}
{focus_text}

## Expansion Guidelines
- Add depth to existing points
- Include additional relevant details
- Maintain academic tone
- Do not add unsupported claims

## Output
Provide the expanded content only."""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=target_words * 2
        )
        
        expanded = response.content.strip()
        
        return {
            "content": expanded,
            "original_word_count": current_words,
            "word_count": len(expanded.split()),
            "expanded": True,
        }
    
    async def _condense_content(
        self,
        content: str,
        target_words: int,
        preserve_elements: Optional[list[str]] = None,
        **kwargs
    ) -> dict:
        """Condense content to meet word count."""
        current_words = len(content.split())
        
        if current_words <= target_words:
            return {
                "content": content,
                "word_count": current_words,
                "condensed": False,
            }
        
        preserve_text = ""
        if preserve_elements:
            preserve_text = "\n## Elements to Preserve\n" + "\n".join(
                f"- {elem}" for elem in preserve_elements
            )
        
        prompt = f"""Condense this content to approximately {target_words} words.

## Current Content ({current_words} words)
{content}
{preserve_text}

## Condensing Guidelines
- Preserve key arguments and evidence
- Remove redundancy
- Maintain academic rigor
- Keep essential citations

## Output
Provide the condensed content only."""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=target_words * 2
        )
        
        condensed = response.content.strip()
        
        return {
            "content": condensed,
            "original_word_count": current_words,
            "word_count": len(condensed.split()),
            "condensed": True,
        }
    
    def _format_rag_results(self, results: list[dict]) -> str:
        """Format RAG results for inclusion in prompts."""
        if not results:
            return "No relevant sources found."
        
        formatted = []
        for i, r in enumerate(results[:10], 1):
            source = r.get("source", "Unknown")
            content = r.get("content", "")[:400]
            formatted.append(f"[{i}] {source}\n{content}")
        
        return "\n\n".join(formatted)
    
    # Section-specific prompts
    def _get_introduction_prompt(self) -> str:
        return """You are an expert academic writer specializing in scoping review introductions.

Write academically rigorous introductions that:
- Establish the research context and significance
- Identify the knowledge gap being addressed
- Present clear research questions/objectives
- Outline the scope of the review
- Follow PRISMA-ScR guidelines for introduction sections

Use formal academic language, cite sources appropriately, and build a logical argument
for why this review is needed."""
    
    def _get_methods_prompt(self) -> str:
        return """You are an expert in research methodology for scoping reviews.

Write methods sections that:
- Follow PRISMA-ScR reporting guidelines precisely
- Describe the search strategy transparently
- Explain eligibility criteria clearly
- Detail the selection process
- Describe data charting/extraction methods
- Explain the synthesis approach

Be precise, reproducible, and comprehensive. Include all methodological details
necessary for replication."""
    
    def _get_results_prompt(self) -> str:
        return """You are an expert academic writer specializing in presenting research findings.

Write results sections that:
- Present findings objectively without interpretation
- Use clear organization (themes, categories, or chronology)
- Include quantitative summaries where appropriate
- Reference tables and figures
- Maintain PRISMA-ScR compliance

Present data systematically and let the evidence speak for itself."""
    
    def _get_discussion_prompt(self) -> str:
        return """You are an expert academic writer specializing in research discussion sections.

Write discussion sections that:
- Interpret findings in context of existing literature
- Address each research question
- Acknowledge limitations
- Discuss practical and theoretical implications
- Suggest future research directions

Balance synthesis with critical analysis. Relate findings back to the broader field."""
    
    def _get_conclusion_prompt(self) -> str:
        return """You are an expert academic writer specializing in research conclusions.

Write conclusions that:
- Summarize key findings concisely
- State implications clearly
- Provide actionable recommendations
- Avoid introducing new information
- End with a strong closing statement

Be concise but impactful. Leave the reader with clear takeaways."""
    
    def _get_default_prompt(self) -> str:
        return """You are an expert academic writer specializing in scoping reviews.

Write content that is:
- Academically rigorous
- Well-structured
- Properly cited
- Following PRISMA-ScR guidelines

Maintain objectivity and scholarly tone throughout."""
