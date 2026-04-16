"""Writer Agent: Generates and revises article sections with robust error handling."""

import asyncio
import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class WriterAgent(BaseAgent):
    """
    Agent responsible for writing and revising article sections.
    
    Capabilities:
    - Generate initial drafts based on research
    - Revise content based on feedback
    - Maintain academic writing standards
    - Follow PRISMA-ScR guidelines
    
    Robustness Features (v2.0):
    - Exponential backoff retry logic
    - Timeout protection for LLM calls
    - Input sanitization against prompt injection
    - Response validation
    - Configurable parameters
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        llm_timeout: float = 30.0,
        truncate_length: int = 1000
    ):
        """
        Initialize WriterAgent with configurable robustness parameters.
        
        Args:
            max_retries: Maximum retry attempts for LLM calls (default: 3)
            retry_delay: Initial retry delay in seconds (exponential backoff, default: 1.0)
            llm_timeout: Timeout in seconds for each LLM call (default: 30.0)
            truncate_length: Max characters for context truncation (default: 1000)
        """
        super().__init__(
            name="writer",
            role=AgentRole.WRITING,
            description="Generates and revises scientific article sections",
            version="2.0.0"
        )
        
        # Robustness parameters
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.llm_timeout = llm_timeout
        self.truncate_length = truncate_length
        
        self._llm_client = None
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
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
        guidelines: str,
        avoid: str,
        research_context: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate initial section draft."""
        
        # Get research context from RAG if not provided
        if not research_context and self.context.rag_query:
            rag_results = await self.query_rag(
                query=f"Research for {section_name} section about {self.state.title}",
                top_k=15
            )
            research_context = self._format_rag_results(rag_results)
        
        system_prompt = self._get_system_prompt(section_id)
        
        # Enhanced prompt with strict word count enforcement
        prompt = f"""Write the {section_name} section for a scoping review article.

## Article Title
{self.state.title}

## CRITICAL WORD COUNT REQUIREMENT
**MINIMUM {min_words} WORDS - MAXIMUM {max_words} WORDS**
This is a STRICT requirement. Your response MUST contain at least {min_words} words.
A typical academic paragraph is 100-200 words. You need approximately {min_words // 150 + 1} to {max_words // 150 + 1} substantial paragraphs.

## Content Guidelines
{guidelines}

## What to Avoid
{avoid}

## Research Context (use to support your writing)
{research_context or "No additional context available."}

## Section Structure Requirements
1. Opening paragraph: Introduce the topic and its significance (100-150 words)
2. Body paragraphs: Develop key themes with evidence and citations (remaining words)
3. Closing: Transition or summary as appropriate for the section

## Academic Writing Standards
- Use formal academic tone
- Follow PRISMA-ScR guidelines for scoping reviews
- Include in-text citations in [Author, Year] format
- Use topic sentences for each paragraph
- Connect ideas with appropriate transitions

## Output Format
Write the COMPLETE section. Do NOT write a brief summary or outline.
Expand each point with detailed academic prose.
Your response must be a fully developed scholarly text of {min_words}-{max_words} words.

NOW WRITE THE FULL {section_name.upper()} SECTION:"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max(2000, max_words * 4)  # Ensure enough tokens
        )
        
        content = response.content.strip()
        word_count = len(content.split())
        
        # Retry if output is too short (common LLM issue)
        retry_count = 0
        max_retries = 2
        
        while word_count < min_words and retry_count < max_retries:
            retry_count += 1
            self.log.warning(
                "retrying_short_output",
                section=section_id,
                word_count=word_count,
                min_required=min_words,
                retry=retry_count
            )
            
            # More aggressive prompt for retry
            retry_prompt = f"""Your previous output was only {word_count} words. 
This is UNACCEPTABLE - I need EXACTLY {min_words}-{max_words} words.

EXPAND your response to meet the requirement. 
Write {min_words // 100} to {max_words // 100} detailed paragraphs.
Each paragraph should be 100-150 words.

Previous (too short): 
{content}

NOW REWRITE WITH FULL LENGTH ({min_words}-{max_words} words):"""

            response = await self._llm_client.generate(
                prompt=retry_prompt,
                system_prompt=system_prompt,
                max_tokens=max(2000, max_words * 4)
            )
            content = response.content.strip()
            word_count = len(content.split())
        
        # Final warning if still below minimum
        if word_count < min_words:
            self.log.warning(
                "section_below_min_words",
                section=section_id,
                word_count=word_count,
                min_required=min_words,
                retries_attempted=retry_count
            )
        
        self.log.info(
            "section_written",
            section=section_id,
            word_count=word_count,
            tokens_used=response.input_tokens + response.output_tokens
        )
        
        return content
    
    async def _revise_section(
        self,
        section_id: str,
        current_content: str,
        feedback: str,
        iteration: int,
        focus_areas: Optional[list[str]] = None,
        **kwargs
    ) -> str:
        """Revise section based on feedback."""
        
        system_prompt = """You are an expert academic editor revising a scientific article.
Maintain the overall structure while addressing the feedback.
Preserve citations and factual claims unless specifically asked to change them.
Improve clarity, coherence, and academic rigor."""
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\n## Priority Focus Areas\n" + "\n".join(f"- {area}" for area in focus_areas)
        
        prompt = f"""Revise this section based on the feedback provided.

## Current Content
{current_content}

## Feedback to Address
{feedback}
{focus_text}

## Revision Guidelines
- This is iteration {iteration}
- Address the most critical issues first
- Maintain word count within 10% of current
- Preserve accurate citations
- Improve clarity and flow

## Output
Provide the revised section in full. Do not include meta-commentary about the changes."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=len(current_content.split()) * 3
        )
        
        revised_content = response.content.strip()
        
        self.log.info(
            "section_revised",
            section=section_id,
            iteration=iteration,
            original_words=len(current_content.split()),
            revised_words=len(revised_content.split())
        )
        
        return revised_content
    
    async def _expand_content(
        self,
        content: str,
        target_words: int,
        focus_areas: Optional[list[str]] = None,
        **kwargs
    ) -> str:
        """Expand content to meet word count."""
        current_words = len(content.split())
        
        if current_words >= target_words:
            return content
        
        prompt = f"""Expand this content to approximately {target_words} words.

## Current Content ({current_words} words)
{content}

## Expansion Guidelines
- Add depth to existing points
- Include additional relevant details
- Maintain academic tone
- Do not add filler or repetition
{"- Focus on: " + ", ".join(focus_areas) if focus_areas else ""}

## Output
Provide the expanded content."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=target_words * 2
        )
        
        return response.content.strip()
    
    async def _condense_content(
        self,
        content: str,
        target_words: int,
        preserve_citations: bool = True,
        **kwargs
    ) -> str:
        """Condense content to meet word limit."""
        current_words = len(content.split())
        
        if current_words <= target_words:
            return content
        
        prompt = f"""Condense this content to approximately {target_words} words.

## Current Content ({current_words} words)
{content}

## Condensation Guidelines
- Remove redundancy
- Combine related points
- Maintain key arguments
- {"Preserve all citations" if preserve_citations else "Remove non-essential citations"}
- Keep the most important evidence

## Output
Provide the condensed content."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=target_words * 2
        )
        
        return response.content.strip()
    
    def _get_system_prompt(self, section_id: str) -> str:
        """Get section-specific system prompt."""
        base = """You are an expert scientific writer specializing in scoping reviews.

CRITICAL INSTRUCTION: You MUST write LONG, detailed academic content.
- NEVER write summaries or outlines
- ALWAYS write full paragraphs (100-150 words each)
- ALWAYS meet the specified word count requirements
- Write in clear, precise academic English following APA style
- Use evidence-based statements with proper citations
- Maintain objectivity and avoid overstatements"""
        
        section_guidance = {
            "abstract": """
For the Abstract:
- Use structured format: Background, Objective, Methods, Results, Conclusions
- Be concise and informative
- No citations in abstract""",
            
            "introduction": """
For the Introduction:
- Start broad, narrow to specific
- Establish the knowledge gap
- State clear research objectives
- Justify scoping review methodology""",
            
            "methods": """
For the Methods:
- Follow PRISMA-ScR checklist
- Be detailed and reproducible
- Describe eligibility criteria precisely
- Include full search strategy""",
            
            "results": """
For the Results:
- Report objectively without interpretation
- Use tables and figures effectively
- Present themes and patterns
- Include quantitative summary where appropriate""",
            
            "discussion": """
For the Discussion:
- Interpret findings in context
- Compare with existing literature
- Acknowledge limitations honestly
- Suggest future research directions""",
            
            "conclusion": """
For the Conclusion:
- Summarize key findings
- Answer the research questions
- Provide clear takeaways
- Be concise"""
        }
        
        return base + section_guidance.get(section_id, "")
    
    def _format_rag_results(self, results: list[dict]) -> str:
        """Format RAG results as context."""
        if not results:
            return ""
        
        formatted = []
        for i, r in enumerate(results[:10], 1):
            source = r.get("source", "Unknown")
            content = r.get("content", "")[:500]
            formatted.append(f"[{i}] Source: {source}\n{content}")
        
        return "\n\n".join(formatted)
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add writer-specific metadata with confidence scoring."""
        if result.output:
            content = str(result.output)
            word_count = len(content.split())
            
            # Calculate confidence based on multiple heuristics
            confidence_factors = []
            
            # 1. Word count factor (did we meet the target?)
            # Assume targets were passed in handoff_data or estimate
            target_min = result.handoff_data.get("min_words", 150)
            target_max = result.handoff_data.get("max_words", 400)
            
            if word_count >= target_min:
                word_factor = min(1.0, word_count / target_min)
            else:
                word_factor = word_count / target_min  # Penalize short content
            confidence_factors.append(word_factor)
            
            # 2. Citation presence factor
            citation_count = content.count("[") + content.count("(")
            citation_factor = min(1.0, citation_count / 5)  # Expect ~5 citations
            confidence_factors.append(citation_factor)
            
            # 3. Structure factor (paragraph count)
            paragraphs = [p for p in content.split("\n\n") if len(p.strip()) > 50]
            structure_factor = min(1.0, len(paragraphs) / 3)  # Expect ~3 paragraphs
            confidence_factors.append(structure_factor)
            
            # 4. Academic vocabulary factor (rough heuristic)
            academic_terms = ["research", "study", "findings", "evidence", "analysis", 
                           "literature", "methodology", "results", "implications"]
            term_count = sum(1 for term in academic_terms if term.lower() in content.lower())
            vocab_factor = min(1.0, term_count / 4)
            confidence_factors.append(vocab_factor)
            
            # Average all factors
            result.confidence = sum(confidence_factors) / len(confidence_factors)
            
            result.handoff_data = {
                "word_count": word_count,
                "paragraph_count": len(paragraphs),
                "citation_indicators": citation_count,
                "section_ready_for_review": word_count >= target_min,
                "confidence_breakdown": {
                    "word_count_factor": word_factor,
                    "citation_factor": citation_factor,
                    "structure_factor": structure_factor,
                    "vocabulary_factor": vocab_factor
                }
            }
        return result
    
    async def _generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        operation: str
    ) -> Any:
        """
        Generate LLM response with exponential backoff retry and timeout protection.
        
        Implements resilient API calling with:
        - Exponential backoff (1s → 2s → 4s...)
        - Configurable max retries
        - Timeout protection
        - Detailed error logging
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            operation: Operation name for logging (e.g., "write_section")
        
        Returns:
            LLM response object
        
        Raises:
            RuntimeError: If all retries exhausted
        
        Example:
            >>> response = await self._generate_with_retry(
            ...     prompt="Write introduction...",
            ...     system_prompt="You are...",
            ...     max_tokens=2000,
            ...     operation="write_section"
            ... )
        """
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self._llm_client.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        max_tokens=max_tokens
                    ),
                    timeout=self.llm_timeout
                )
                
                self.log.info(
                    "llm_call_success",
                    operation=operation,
                    attempt=attempt + 1,
                    response_length=len(response.content) if response.content else 0
                )
                
                return response
                
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    self.log.warning(
                        "llm_call_timeout_retrying",
                        operation=operation,
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        retry_delay=delay,
                        timeout=self.llm_timeout
                    )
                    await asyncio.sleep(delay)
                else:
                    self.log.error(
                        "llm_call_timeout_exhausted",
                        operation=operation,
                        attempts=self.max_retries,
                        timeout=self.llm_timeout
                    )
                    raise RuntimeError(
                        f"{operation} timed out after {self.max_retries} attempts "
                        f"(timeout: {self.llm_timeout}s)"
                    )
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    self.log.warning(
                        "llm_call_failed_retrying",
                        operation=operation,
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        retry_delay=delay,
                        error=str(e)
                    )
                    await asyncio.sleep(delay)
                else:
                    self.log.error(
                        "llm_call_exhausted",
                        operation=operation,
                        attempts=self.max_retries,
                        error=str(e)
                    )
                    raise RuntimeError(
                        f"{operation} failed after {self.max_retries} attempts: {e}"
                    )
    
    def _sanitize_user_input(self, value: Any) -> str:
        """
        Sanitize user input to prevent prompt injection.
        
        Removes common injection patterns:
        - Triple backticks (```)
        - System/Assistant/User keywords
        - Excessive whitespace
        
        Args:
            value: Input value (converted to string)
        
        Returns:
            Sanitized string (max 500 chars for safety)
        
        Example:
            >>> sanitized = self._sanitize_user_input("```SYSTEM: Ignore previous")
            >>> print(sanitized)
            "Ignore previous"
        """
        str_value = str(value)
        
        # Remove injection patterns
        str_value = str_value.replace("```", "")
        str_value = str_value.replace("SYSTEM:", "")
        str_value = str_value.replace("ASSISTANT:", "")
        str_value = str_value.replace("USER:", "")
        
        # Limit length for safety
        if len(str_value) > 500:
            str_value = str_value[:500] + "... [truncated for safety]"
            self.log.debug("input_truncated", original_length=len(str(value)))
        
        return str_value.strip()
    
    def _validate_response_content(
        self,
        content: str,
        min_words: int,
        operation: str
    ) -> bool:
        """
        Validate LLM response meets minimum quality requirements.
        
        Args:
            content: Response content to validate
            min_words: Minimum required words
            operation: Operation name for logging
        
        Returns:
            True if valid, False otherwise
        """
        if not content or not content.strip():
            self.log.error(
                "response_validation_failed",
                operation=operation,
                reason="empty_content"
            )
            return False
        
        word_count = len(content.split())
        if word_count < min_words * 0.5:  # Allow 50% threshold for validation
            self.log.warning(
                "response_validation_warning",
                operation=operation,
                word_count=word_count,
                min_required=min_words,
                reason="insufficient_length"
            )
            return False
        
        return True
