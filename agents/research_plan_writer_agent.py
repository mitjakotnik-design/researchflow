"""
ResearchPlanWriterAgent

Agent responsible for writing research plan sections using LLM.
Integrates with research_plan_sections config and follows PRISMA-ScR guidelines.

Capabilities:
- write_section: Generate a section from scratch based on context
- revise_section: Improve existing section based on evaluator feedback
- synthesize_plan: Combine all sections into a cohesive research plan

Implementation:
- Uses Gemini 2.5 Flash for generation (fast, cost-effective)
- Template-based prompting for consistency
- Context-aware generation (uses section dependencies)
- Iterative refinement support
"""

import os
import time
import asyncio
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

import structlog

from config.research_plan_sections import (
    get_section_spec,
    validate_word_count,
    check_required_elements,
    get_all_sections,
    SECTION_ORDER,
    ResearchPlanSection
)
from agents.llm_client import GeminiClient, LLMResponse


logger = structlog.get_logger()


@dataclass
class SectionContext:
    """Context provided for section generation."""
    
    # Core information
    research_topic: str
    research_question: Optional[str] = None
    
    # Completed sections (for dependencies)
    completed_sections: Dict[str, str] = None
    
    # User inputs (from interviewer or manual)
    user_inputs: Dict[str, any] = None
    
    # Guidance
    additional_instructions: Optional[str] = None
    
    # Metadata
    target_journal: Optional[str] = None
    timeline_weeks: int = 21
    
    def __post_init__(self):
        if self.completed_sections is None:
            self.completed_sections = {}
        if self.user_inputs is None:
            self.user_inputs = {}


@dataclass
class RevisionFeedback:
    """Feedback for section revision."""
    
    # Scores
    overall_score: float
    criterion_scores: Dict[str, float]
    
    # Issues identified
    issues: List[str]
    strengths: List[str]
    
    # Specific improvement areas
    missing_elements: List[str] = None
    word_count_issue: Optional[str] = None
    clarity_issues: List[str] = None
    
    # Suggestions
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.missing_elements is None:
            self.missing_elements = []
        if self.clarity_issues is None:
            self.clarity_issues = []
        if self.suggestions is None:
            self.suggestions = []


class ResearchPlanWriterAgent:
    """
    Agent for writing research plan sections using LLM.
    
    Uses template-based prompting with section-specific guidelines
    to generate high-quality research plan content.
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        dep_truncate_length: int = 1000,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the writer agent.
        
        Args:
            model: Gemini model to use (default: gemini-2.5-flash)
            temperature: Sampling temperature (0.0-1.0, default 0.7)
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            dep_truncate_length: Max chars for dependency content (default: 1000)
            max_retries: Maximum retry attempts for LLM calls (default: 3)
            retry_delay: Initial retry delay in seconds (default: 1.0)
        """
        self.model = model
        self.temperature = temperature
        self.dep_truncate_length = dep_truncate_length
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.llm_client = GeminiClient(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
        self.log = structlog.get_logger().bind(agent="ResearchPlanWriterAgent")
        
        self.log.info(
            "writer_agent_initialized",
            model=model,
            temperature=temperature,
            dep_truncate_length=dep_truncate_length,
            max_retries=max_retries
        )
    
    async def write_section(
        self,
        section_id: str,
        context: SectionContext
    ) -> Tuple[str, Dict[str, any]]:
        """
        Write a research plan section from scratch.
        
        Args:
            section_id: ID of section to write (e.g., "research_question")
            context: Context information for generation
        
        Returns:
            Tuple of (generated_content, metadata)
            
        Raises:
            ValueError: If section_id is invalid
            RuntimeError: If generation fails
        """
        start_time = time.time()
        
        # Get section specification
        try:
            spec = get_section_spec(section_id)
        except ValueError as e:
            self.log.error("invalid_section_id", section_id=section_id, error=str(e))
            raise
        
        self.log.info(
            "writing_section",
            section_id=section_id,
            section_name=spec.name,
            word_range=f"{spec.min_words}-{spec.max_words}"
        )
        
        # Check dependencies
        missing_deps = self._check_dependencies(spec, context.completed_sections)
        if missing_deps:
            self.log.warning(
                "missing_dependencies",
                section_id=section_id,
                missing=missing_deps
            )
        
        # Build prompt
        prompt = self._build_section_prompt(spec, context)
        system_prompt = self._build_system_prompt(spec)
        
        # Generate content with retry logic
        try:
            response = await self._generate_with_retry(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=spec.max_words * 2,  # Conservative estimate (1 word ≈ 1.5 tokens)
                json_mode=False,
                operation="write_section",
                section_id=section_id
            )
            
            content = response.content
            
        except Exception as e:
            self.log.error(
                "generation_failed",
                section_id=section_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to generate section {section_id}: {e}")
        
        # Validate generated content
        validation_results = self._validate_content(content, spec)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Prepare metadata
        metadata = {
            "section_id": section_id,
            "section_name": spec.name,
            "model": self.model,
            "temperature": self.temperature,
            "duration_ms": duration_ms,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "validation": validation_results,
            "missing_dependencies": missing_deps
        }
        
        self.log.info(
            "section_written",
            section_id=section_id,
            duration_ms=duration_ms,
            word_count=validation_results.get("word_count", 0),
            validation_passed=validation_results.get("word_count_valid", False)
        )
        
        return content, metadata
    
    async def revise_section(
        self,
        section_id: str,
        current_content: str,
        feedback: RevisionFeedback,
        context: SectionContext
    ) -> Tuple[str, Dict[str, any]]:
        """
        Revise a section based on evaluator feedback.
        
        Args:
            section_id: ID of section to revise
            current_content: Current section content
            feedback: Evaluation feedback with issues and suggestions
            context: Context information
        
        Returns:
            Tuple of (revised_content, metadata)
        
        Raises:
            ValueError: If section_id is invalid
            RuntimeError: If revision fails
        """
        start_time = time.time()
        
        # Get section specification
        try:
            spec = get_section_spec(section_id)
        except ValueError as e:
            self.log.error("invalid_section_id", section_id=section_id, error=str(e))
            raise
        
        self.log.info(
            "revising_section",
            section_id=section_id,
            overall_score=feedback.overall_score,
            issues_count=len(feedback.issues)
        )
        
        # Build revision prompt
        prompt = self._build_revision_prompt(
            spec,
            current_content,
            feedback,
            context
        )
        system_prompt = self._build_system_prompt(spec, revision=True)
        
        # Generate revised content with retry logic
        try:
            response = await self._generate_with_retry(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=spec.max_words * 2,
                json_mode=False,
                operation="revise_section",
                section_id=section_id
            )
            
            revised_content = response.content
            
        except Exception as e:
            self.log.error(
                "revision_failed",
                section_id=section_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to revise section {section_id}: {e}")
        
        # Validate revised content
        validation_results = self._validate_content(revised_content, spec)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Prepare metadata
        metadata = {
            "section_id": section_id,
            "section_name": spec.name,
            "model": self.model,
            "temperature": self.temperature,
            "duration_ms": duration_ms,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "validation": validation_results,
            "previous_score": feedback.overall_score,
            "issues_addressed": len(feedback.issues)
        }
        
        self.log.info(
            "section_revised",
            section_id=section_id,
            duration_ms=duration_ms,
            word_count=validation_results.get("word_count", 0),
            validation_passed=validation_results.get("word_count_valid", False)
        )
        
        return revised_content, metadata
    
    async def synthesize_plan(
        self,
        sections: Dict[str, str],
        metadata: Dict[str, any] = None
    ) -> Tuple[str, Dict[str, any]]:
        """
        Synthesize all sections into a cohesive research plan.
        
        Args:
            sections: Dictionary mapping section_id to content
            metadata: Optional metadata about the research plan
        
        Returns:
            Tuple of (complete_plan, metadata)
        
        Raises:
            ValueError: If required sections are missing
        """
        start_time = time.time()
        
        self.log.info(
            "synthesizing_plan",
            sections_count=len(sections)
        )
        
        # Check that all required sections are present
        missing_sections = []
        for section_id in SECTION_ORDER:
            spec = get_section_spec(section_id)
            # Check if it's a must-have section (first 12)
            if SECTION_ORDER.index(section_id) < 12:  # Must-have sections
                if section_id not in sections:
                    missing_sections.append(section_id)
        
        if missing_sections:
            raise ValueError(
                f"Missing required sections: {', '.join(missing_sections)}"
            )
        
        # Build synthesized document
        plan_parts = []
        
        # Header
        if metadata:
            plan_parts.append(self._build_plan_header(metadata))
        
        # Add sections in proper order
        for section_id in SECTION_ORDER:
            if section_id in sections:
                spec = get_section_spec(section_id)
                plan_parts.append(f"\n\n## {spec.name}\n\n{sections[section_id]}")
        
        # Join all parts
        complete_plan = "\n".join(plan_parts)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Calculate statistics
        total_words = sum(
            len(content.split()) for content in sections.values()
        )
        
        synthesis_metadata = {
            "sections_count": len(sections),
            "total_words": total_words,
            "duration_ms": duration_ms,
            "sections_included": list(sections.keys())
        }
        
        self.log.info(
            "plan_synthesized",
            sections_count=len(sections),
            total_words=total_words,
            duration_ms=duration_ms
        )
        
        return complete_plan, synthesis_metadata
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _check_dependencies(
        self,
        spec: ResearchPlanSection,
        completed_sections: Dict[str, str]
    ) -> List[str]:
        """Check if section dependencies are satisfied."""
        missing = []
        for dep_id in spec.depends_on:
            if dep_id not in completed_sections:
                missing.append(dep_id)
        return missing
    
    def _validate_content(
        self,
        content: str,
        spec: ResearchPlanSection
    ) -> Dict[str, any]:
        """Validate generated content against section requirements."""
        results = {}
        
        # Word count validation
        word_count_valid, word_count_msg = validate_word_count(content, spec.section_id)
        word_count = len(content.split())
        
        results["word_count"] = word_count
        results["word_count_valid"] = word_count_valid
        results["word_count_message"] = word_count_msg
        
        # Required elements validation
        elements_valid, missing_elements = check_required_elements(content, spec.section_id)
        
        results["required_elements_valid"] = elements_valid
        results["missing_elements"] = missing_elements
        
        return results
    
    def _build_system_prompt(
        self,
        spec: ResearchPlanSection,
        revision: bool = False
    ) -> str:
        """Build system prompt for section generation."""
        if revision:
            role = "expert research plan editor"
        else:
            role = "expert research plan writer"
        
        return f"""You are an {role} specializing in scoping reviews following PRISMA-ScR guidelines.

Your task is to write the **{spec.name}** section of a research plan.

GUIDELINES:
- Follow academic writing conventions (formal, precise, clear)
- Use markdown formatting for structure
- Word count target: {spec.min_words}-{spec.max_words} words
- Include all required elements
- Maintain consistency with PRISMA-ScR methodology
- Be specific and actionable (avoid vague statements)

QUALITY CRITERIA:
- Clarity: Clear, unambiguous language
- Completeness: All required elements present
- Rigor: Methodologically sound
- Feasibility: Realistic and achievable

Generate content that would score ≥85/100 in evaluation."""
    
    def _build_section_prompt(
        self,
        spec: ResearchPlanSection,
        context: SectionContext
    ) -> str:
        """Build prompt for section generation."""
        prompt_parts = []
        
        # Section description
        prompt_parts.append(f"**Section:** {spec.name}")
        prompt_parts.append(f"**Description:** {spec.description}")
        prompt_parts.append("")
        
        # Research context
        prompt_parts.append("**RESEARCH CONTEXT:**")
        prompt_parts.append(f"- Topic: {context.research_topic}")
        if context.research_question:
            prompt_parts.append(f"- Research Question: {context.research_question}")
        if context.target_journal:
            prompt_parts.append(f"- Target Journal: {context.target_journal}")
        prompt_parts.append(f"- Timeline: {context.timeline_weeks} weeks")
        prompt_parts.append("")
        
        # Dependencies (completed sections)
        if spec.depends_on and context.completed_sections:
            prompt_parts.append("**COMPLETED SECTIONS (for reference):**")
            for dep_id in spec.depends_on:
                if dep_id in context.completed_sections:
                    dep_spec = get_section_spec(dep_id)
                    dep_content = context.completed_sections[dep_id]
                    # Truncate if too long (configurable threshold)
                    if len(dep_content) > self.dep_truncate_length:
                        dep_content = dep_content[:self.dep_truncate_length] + "... [truncated]"
                    prompt_parts.append(f"\n**{dep_spec.name}:**\n{dep_content}")
            prompt_parts.append("")
        
        # Required elements
        prompt_parts.append("**REQUIRED ELEMENTS:**")
        for element in spec.required_elements:
            element_name = element.replace("_", " ").title()
            prompt_parts.append(f"- {element_name}")
        prompt_parts.append("")
        
        # Optional elements
        if spec.optional_elements:
            prompt_parts.append("**OPTIONAL ELEMENTS (include if relevant):**")
            for element in spec.optional_elements:
                element_name = element.replace("_", " ").title()
                prompt_parts.append(f"- {element_name}")
            prompt_parts.append("")
        
        # User inputs (sanitized)
        if context.user_inputs:
            prompt_parts.append("**USER INPUTS:**")
            for key, value in context.user_inputs.items():
                sanitized_value = self._sanitize_user_input(value)
                prompt_parts.append(f"- {key}: {sanitized_value}")
            prompt_parts.append("")
        
        # Additional instructions
        if context.additional_instructions:
            prompt_parts.append("**ADDITIONAL INSTRUCTIONS:**")
            prompt_parts.append(context.additional_instructions)
            prompt_parts.append("")
        
        # Final instruction
        prompt_parts.append(f"**TASK:** Write the **{spec.name}** section following the guidelines above.")
        prompt_parts.append(f"Target length: {spec.min_words}-{spec.max_words} words.")
        prompt_parts.append("Output ONLY the section content in markdown format (no meta-commentary).")
        
        return "\n".join(prompt_parts)
    
    def _build_revision_prompt(
        self,
        spec: ResearchPlanSection,
        current_content: str,
        feedback: RevisionFeedback,
        context: SectionContext
    ) -> str:
        """Build prompt for section revision."""
        prompt_parts = []
        
        # Section info
        prompt_parts.append(f"**Section:** {spec.name}")
        prompt_parts.append(f"**Current Score:** {feedback.overall_score:.1f}/100")
        prompt_parts.append("")
        
        # Current content
        prompt_parts.append("**CURRENT CONTENT:**")
        prompt_parts.append("```markdown")
        prompt_parts.append(current_content)
        prompt_parts.append("```")
        prompt_parts.append("")
        
        # Feedback
        prompt_parts.append("**EVALUATION FEEDBACK:**")
        
        # Criterion scores
        prompt_parts.append("\n**Scores by Criterion:**")
        for criterion, score in feedback.criterion_scores.items():
            prompt_parts.append(f"- {criterion.title()}: {score:.1f}")
        prompt_parts.append("")
        
        # Issues
        if feedback.issues:
            prompt_parts.append("**Issues to Address:**")
            for i, issue in enumerate(feedback.issues, 1):
                prompt_parts.append(f"{i}. {issue}")
            prompt_parts.append("")
        
        # Missing elements
        if feedback.missing_elements:
            prompt_parts.append("**Missing Required Elements:**")
            for element in feedback.missing_elements:
                element_name = element.replace("_", " ").title()
                prompt_parts.append(f"- {element_name}")
            prompt_parts.append("")
        
        # Word count issue
        if feedback.word_count_issue:
            prompt_parts.append(f"**Word Count:** {feedback.word_count_issue}")
            prompt_parts.append("")
        
        # Clarity issues
        if feedback.clarity_issues:
            prompt_parts.append("**Clarity Issues:**")
            for issue in feedback.clarity_issues:
                prompt_parts.append(f"- {issue}")
            prompt_parts.append("")
        
        # Suggestions
        if feedback.suggestions:
            prompt_parts.append("**Suggestions for Improvement:**")
            for suggestion in feedback.suggestions:
                prompt_parts.append(f"- {suggestion}")
            prompt_parts.append("")
        
        # Strengths (to preserve)
        if feedback.strengths:
            prompt_parts.append("**Strengths to Preserve:**")
            for strength in feedback.strengths:
                prompt_parts.append(f"- {strength}")
            prompt_parts.append("")
        
        # Task
        prompt_parts.append("**TASK:**")
        prompt_parts.append(f"Revise the **{spec.name}** section addressing all issues above.")
        prompt_parts.append("Maintain the strengths while improving weak areas.")
        prompt_parts.append(f"Target: Score ≥85/100, {spec.min_words}-{spec.max_words} words.")
        prompt_parts.append("Output ONLY the revised content in markdown format (no meta-commentary).")
        
        return "\n".join(prompt_parts)
    
    def _build_plan_header(self, metadata: Dict[str, any]) -> str:
        """Build header for synthesized research plan."""
        header_parts = []
        
        header_parts.append("# Research Plan: Scoping Review")
        header_parts.append("")
        
        if "title" in metadata:
            header_parts.append(f"**Title:** {metadata['title']}")
        
        if "authors" in metadata:
            header_parts.append(f"**Authors:** {metadata['authors']}")
        
        if "institution" in metadata:
            header_parts.append(f"**Institution:** {metadata['institution']}")
        
        if "date" in metadata:
            header_parts.append(f"**Date:** {metadata['date']}")
        
        if "version" in metadata:
            header_parts.append(f"**Version:** {metadata['version']}")
        
        header_parts.append("")
        header_parts.append("---")
        
        return "\n".join(header_parts)
    
    async def _generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        json_mode: bool,
        operation: str,
        section_id: str
    ) -> 'LLMResponse':
        """
        Generate LLM response with exponential backoff retry.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate
            json_mode: Whether to use JSON mode
            operation: Operation name (for logging)
            section_id: Section being processed
        
        Returns:
            LLM response
        
        Raises:
            RuntimeError: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = await self.llm_client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    json_mode=json_mode
                )
                
                # Success
                if attempt > 0:
                    self.log.info(
                        "retry_succeeded",
                        operation=operation,
                        section_id=section_id,
                        attempt=attempt + 1
                    )
                
                return response
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    # Calculate backoff delay (exponential)
                    delay = self.retry_delay * (2 ** attempt)
                    
                    self.log.warning(
                        "llm_call_failed_retrying",
                        operation=operation,
                        section_id=section_id,
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        error=str(e),
                        retry_delay=delay
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    self.log.error(
                        "llm_call_failed_all_retries_exhausted",
                        operation=operation,
                        section_id=section_id,
                        attempts=self.max_retries,
                        error=str(e)
                    )
        
        # All retries exhausted
        raise RuntimeError(
            f"{operation} failed after {self.max_retries} attempts: {last_exception}"
        )
    
    def _sanitize_user_input(self, value: any) -> str:
        """
        Sanitize user input before adding to prompt.
        
        Removes potential prompt injection patterns and limits length.
        
        Args:
            value: User input value
        
        Returns:
            Sanitized string
        """
        # Convert to string
        str_value = str(value)
        
        # Remove potential prompt injection patterns
        str_value = str_value.replace("```", "")  # Remove code blocks
        str_value = str_value.replace("SYSTEM:", "")  # Remove system keywords
        str_value = str_value.replace("ASSISTANT:", "")  # Remove assistant keywords
        str_value = str_value.replace("USER:", "")  # Remove user keywords
        
        # Remove excessive newlines
        while "\n\n\n" in str_value:
            str_value = str_value.replace("\n\n\n", "\n\n")
        
        # Limit length
        max_input_length = 500
        if len(str_value) > max_input_length:
            str_value = str_value[:max_input_length] + "... [truncated]"
        
        return str_value.strip()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_writer_agent(
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7
) -> ResearchPlanWriterAgent:
    """
    Create a writer agent with default settings.
    
    Args:
        model: Gemini model to use
        temperature: Sampling temperature
    
    Returns:
        Configured ResearchPlanWriterAgent
    """
    return ResearchPlanWriterAgent(model=model, temperature=temperature)


if __name__ == "__main__":
    # Test initialization
    import asyncio
    
    async def test():
        agent = create_writer_agent()
        print(f"✅ ResearchPlanWriterAgent initialized (model: {agent.model})")
        
        # Test section info retrieval
        spec = get_section_spec("research_question")
        print(f"\n📋 Section: {spec.name}")
        print(f"   Word range: {spec.min_words}-{spec.max_words}")
        print(f"   Required elements: {len(spec.required_elements)}")
    
    asyncio.run(test())
