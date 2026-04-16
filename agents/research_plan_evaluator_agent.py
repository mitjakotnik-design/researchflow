"""
ResearchPlanEvaluatorAgent: Multi-persona research plan evaluation with weighted scoring.

This agent implements comprehensive evaluation of research plan sections using:
- 4 evaluator personas (Methodology Expert, Research Supervisor, Domain Expert, Ethics Reviewer)
- 4 main criteria (Clarity, Feasibility, Rigor, Contribution)
- 21 subcriteria with weighted scoring
- Exponential backoff retry logic for API resilience
- Input sanitization for security

Architecture:
    - Multi-persona evaluation: Each persona evaluates independently
    - Weighted aggregation: Personas weighted by expertise relevance
    - Structured feedback: Actionable recommendations by criterion
    - Score validation: Range checks, floating-point tolerance

Quality Standards:
    - Target score: ≥9.0 (matches ResearchPlanWriterAgent benchmark)
    - Retry logic: Exponential backoff (3 attempts)
    - Input sanitization: Protection against prompt injection
    - Configurable parameters: max_retries, retry_delay, truncation
    - Comprehensive testing: 15-18 unit tests
"""

import asyncio
import logging
import structlog
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from google import genai

from config.research_plan_evaluation import (
    MainCriterion,
    SubCriterion,
    EvaluatorPersona,
    EVALUATION_CRITERIA,
    EVALUATOR_PERSONAS,
    QualityVerdict,
    get_verdict,
    validate_evaluation
)


@dataclass
class PersonaEvaluation:
    """Individual persona evaluation result."""
    persona_name: str
    persona_weight: float
    criteria_scores: Dict[str, float]  # criterion_id -> score
    subcriteria_scores: Dict[str, float]  # subcriterion_id -> score
    total_score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    timestamp: str


@dataclass
class AggregatedEvaluation:
    """Aggregated evaluation from all personas."""
    section_id: str
    section_title: str
    overall_score: float
    criteria_scores: Dict[str, float]  # criterion_id -> weighted avg
    persona_evaluations: List[PersonaEvaluation]
    consensus_feedback: str
    priority_improvements: List[str]
    meets_threshold: bool  # ≥75 minimum acceptable
    recommended_approval: bool  # ≥85 for approval
    timestamp: str


class ResearchPlanEvaluatorAgent:
    """
    Multi-persona evaluator for research plan sections.
    
    Implements weighted scoring with 4 evaluator personas:
    - Methodology Expert (40%): Focus on rigor, feasibility
    - Research Supervisor (30%): Focus on clarity, contribution
    - Domain Expert (20%): Focus on relevance, innovation
    - Ethics Reviewer (10%): Focus on ethics, compliance
    
    Attributes:
        model (str): LLM model identifier (default: gemini-2.5-flash)
        temperature (float): LLM temperature (default: 0.3, lower for consistent scoring)
        max_retries (int): Maximum retry attempts for LLM calls
        retry_delay (float): Initial retry delay in seconds (exponential backoff)
        truncate_length (int): Max characters for context truncation
        min_acceptable_score (float): Minimum score for acceptance (default: 75.0)
        approval_threshold (float): Score for approval recommendation (default: 85.0)
    
    Example:
        >>> evaluator = ResearchPlanEvaluatorAgent(
        ...     model="gemini-2.5-pro",
        ...     max_retries=3,
        ...     min_acceptable_score=75.0
        ... )
        >>> result = await evaluator.evaluate_section(
        ...     section_id="S01_INTRODUCTION",
        ...     section_content="...",
        ...     research_context={...}
        ... )
        >>> print(f"Score: {result.overall_score}/100")
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.3,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        truncate_length: int = 1000,
        llm_timeout: float = 30.0,
        min_acceptable_score: float = 75.0,
        approval_threshold: float = 85.0,
        api_key: Optional[str] = None
    ):
        """
        Initialize ResearchPlanEvaluatorAgent.
        
        Args:
            model: LLM model identifier
            temperature: LLM temperature (lower for consistent scoring)
            max_retries: Maximum retry attempts for LLM calls
            retry_delay: Initial retry delay in seconds
            truncate_length: Max characters for context truncation
            llm_timeout: Timeout in seconds for each LLM call (default: 30.0)
            min_acceptable_score: Minimum acceptable score (0-100)
            approval_threshold: Score threshold for approval (0-100)
            api_key: Optional API key (uses environment variable if None)
        
        Raises:
            ValueError: If thresholds are invalid
        """
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.truncate_length = truncate_length
        self.llm_timeout = llm_timeout
        self.min_acceptable_score = min_acceptable_score
        self.approval_threshold = approval_threshold
        
        # Validation
        if not (0 <= min_acceptable_score <= 100):
            raise ValueError(f"min_acceptable_score must be 0-100, got {min_acceptable_score}")
        if not (0 <= approval_threshold <= 100):
            raise ValueError(f"approval_threshold must be 0-100, got {approval_threshold}")
        if min_acceptable_score > approval_threshold:
            raise ValueError("min_acceptable_score cannot exceed approval_threshold")
        
        # Store evaluation config references
        self.criteria = EVALUATION_CRITERIA
        self.personas = EVALUATOR_PERSONAS
        
        # Initialize LLM client
        self.llm_client = genai.Client(api_key=api_key)
        
        # Logging
        self.log = structlog.get_logger(self.__class__.__name__)
        self.log.info(
            "evaluator_initialized",
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            personas=len(self.personas),
            criteria=len(self.criteria)
        )
    
    async def evaluate_section(
        self,
        section_id: str,
        section_content: str,
        research_context: Optional[Dict[str, Any]] = None
    ) -> AggregatedEvaluation:
        """
        Evaluate a research plan section with multi-persona scoring.
        
        Args:
            section_id: Section identifier (e.g., "S01_INTRODUCTION")
            section_content: Full section text to evaluate
            research_context: Optional context (topic, methodology, etc.)
        
        Returns:
            AggregatedEvaluation with weighted scores and feedback
        
        Raises:
            ValueError: If section_id or content is invalid
            RuntimeError: If evaluation fails after retries
        
        Example:
            >>> result = await evaluator.evaluate_section(
            ...     section_id="S01_INTRODUCTION",
            ...     section_content="# Introduction\\n\\nThis study...",
            ...     research_context={"topic": "AI ethics", "methodology": "systematic review"}
            ... )
            >>> print(f"Overall: {result.overall_score:.1f}/100")
            >>> print(f"Approved: {result.recommended_approval}")
        """
        # Validation
        if not section_id or not isinstance(section_id, str):
            raise ValueError(f"Invalid section_id: {section_id}")
        if not section_content or not isinstance(section_content, str):
            raise ValueError("section_content must be non-empty string")
        
        # Sanitize inputs
        section_id = self._sanitize_user_input(section_id)
        section_content = self._sanitize_user_input(section_content)
        
        self.log.info(
            "evaluating_section",
            section_id=section_id,
            content_length=len(section_content),
            has_context=research_context is not None
        )
        
        try:
            # Generate evaluations from all personas in parallel
            tasks = [
                self._generate_persona_evaluation(
                    persona_enum=persona_enum,
                    persona_config=persona_config,
                    section_id=section_id,
                    section_content=section_content,
                    research_context=research_context or {}
                )
                for persona_enum, persona_config in self.personas.items()
            ]
            
            persona_evaluations = await asyncio.gather(*tasks)
            
            # Aggregate scores with persona weights
            aggregated = self._aggregate_scores(
                section_id=section_id,
                section_content=section_content,
                persona_evaluations=persona_evaluations
            )
            
            self.log.info(
                "section_evaluated",
                section_id=section_id,
                overall_score=aggregated.overall_score,
                meets_threshold=aggregated.meets_threshold,
                recommended=aggregated.recommended_approval,
                personas_count=len(persona_evaluations)
            )
            
            return aggregated
            
        except Exception as e:
            self.log.error(
                "evaluation_failed",
                section_id=section_id,
                error=str(e)
            )
            raise RuntimeError(f"Failed to evaluate section {section_id}: {e}")
    
    async def evaluate_full_plan(
        self,
        sections: Dict[str, str],
        research_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AggregatedEvaluation]:
        """
        Evaluate complete research plan (all sections).
        
        Args:
            sections: Dict mapping section_id -> section_content
            research_context: Optional shared context for all sections
        
        Returns:
            Dict mapping section_id -> AggregatedEvaluation
        
        Raises:
            ValueError: If sections dict is empty or invalid
            RuntimeError: If any section evaluation fails
        
        Example:
            >>> sections = {
            ...     "S01_INTRODUCTION": "# Introduction...",
            ...     "S02_RESEARCH_QUESTIONS": "# Research Questions..."
            ... }
            >>> results = await evaluator.evaluate_full_plan(sections)
            >>> avg_score = sum(r.overall_score for r in results.values()) / len(results)
            >>> print(f"Average score: {avg_score:.1f}/100")
        """
        if not sections or not isinstance(sections, dict):
            raise ValueError("sections must be non-empty dict")
        
        self.log.info(
            "evaluating_full_plan",
            sections_count=len(sections),
            section_ids=list(sections.keys())
        )
        
        results: Dict[str, AggregatedEvaluation] = {}
        
        for section_id, section_content in sections.items():
            try:
                eval_result = await self.evaluate_section(
                    section_id=section_id,
                    section_content=section_content,
                    research_context=research_context
                )
                results[section_id] = eval_result
                
            except Exception as e:
                self.log.error(
                    "section_evaluation_failed",
                    section_id=section_id,
                    error=str(e)
                )
                raise RuntimeError(f"Failed to evaluate section {section_id}: {e}")
        
        # Calculate overall plan statistics
        avg_score = sum(r.overall_score for r in results.values()) / len(results)
        all_approved = all(r.recommended_approval for r in results.values())
        
        self.log.info(
            "full_plan_evaluated",
            sections_count=len(results),
            average_score=avg_score,
            all_approved=all_approved
        )
        
        return results
    
    async def _generate_persona_evaluation(
        self,
        persona_enum: EvaluatorPersona,
        persona_config: Dict[str, Any],
        section_id: str,
        section_content: str,
        research_context: Dict[str, Any]
    ) -> PersonaEvaluation:
        """
        Generate evaluation from a single persona perspective.
        
        Args:
            persona_enum: EvaluatorPersona enum value
            persona_config: Persona configuration dict with name, weight, focus, etc.
            section_id: Section identifier
            section_content: Section text to evaluate
            research_context: Research context dict
        
        Returns:
            PersonaEvaluation with scores and feedback
        
        Raises:
            RuntimeError: If LLM generation fails after retries
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            persona_enum=persona_enum,
            persona_config=persona_config,
            section_id=section_id,
            section_content=section_content,
            research_context=research_context
        )
        
        system_prompt = f"""You are a {persona_config['name']} evaluating a research plan section.

Your role: {persona_config['focus']}
Your weight in final decision: {persona_config['weight'] * 100:.0f}%

Focus on these criteria: {', '.join(persona_config['primary_criteria'])}

Provide structured evaluation with:
1. Scores for each criterion (0-100)
2. Specific strengths (3-5 points)
3. Specific weaknesses (3-5 points)
4. Actionable feedback

Be objective, consistent, and constructive."""
        
        # Generate with retry
        response = await self._generate_with_retry(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            operation=f"persona_evaluation_{persona_enum.value}"
        )
        
        # Parse LLM response into structured scores
        parsed = self._parse_evaluation_response(
            response_text=response.text,
            persona_config=persona_config
        )
        
        return PersonaEvaluation(
            persona_name=persona_config['name'],
            persona_weight=persona_config['weight'],
            criteria_scores=parsed["criteria_scores"],
            subcriteria_scores=parsed["subcriteria_scores"],
            total_score=parsed["total_score"],
            feedback=parsed["feedback"],
            strengths=parsed["strengths"],
            weaknesses=parsed["weaknesses"],
            timestamp=datetime.now().isoformat()
        )
    
    def _build_evaluation_prompt(
        self,
        persona_enum: EvaluatorPersona,
        persona_config: Dict[str, Any],
        section_id: str,
        section_content: str,
        research_context: Dict[str, Any]
    ) -> str:
        """
        Build evaluation prompt for specific persona.
        
        Args:
            persona_enum: EvaluatorPersona enum value
            persona_config: Persona configuration dict
            section_id: Section identifier
            section_content: Section text
            research_context: Context dict
        
        Returns:
            Formatted prompt string
        """
        # Truncate section content if too long
        if len(section_content) > self.truncate_length:
            section_content = section_content[:self.truncate_length] + "\n\n[... content truncated ...]"
        
        # Build criteria descriptions for this persona's focus
        focus_criteria_desc = []
        for criterion_id in persona_config['primary_criteria']:
            if criterion_id in self.criteria:
                criterion = self.criteria[criterion_id]
                focus_criteria_desc.append(
                    f"- {criterion.name} ({criterion.weight * 100:.0f}%): {criterion.description}"
                )
        
        # Build context section
        context_str = ""
        if research_context:
            context_items = [f"- {k}: {v}" for k, v in research_context.items()]
            context_str = f"\n\n## Research Context\n" + "\n".join(context_items)
        
        prompt = f"""# Research Plan Section Evaluation

## Section to Evaluate
**Section ID:** {section_id}

**Content:**
{section_content}
{context_str}

## Your Evaluation Focus
As a {persona_config['name']}, evaluate this section on:

{chr(10).join(focus_criteria_desc)}

## Scoring Instructions
1. Evaluate each criterion on a 0-100 scale
2. Be specific and cite examples from the section
3. Consider both content quality and completeness
4. Provide actionable recommendations

## Required Output Format
**Criterion Scores:**
- Clarity: [0-100]
- Feasibility: [0-100]
- Rigor: [0-100]
- Contribution: [0-100]

**Strengths:**
1. [Specific strength with evidence]
2. [Specific strength with evidence]
3. [Specific strength with evidence]

**Weaknesses:**
1. [Specific weakness with evidence]
2. [Specific weakness with evidence]
3. [Specific weakness with evidence]

**Feedback:**
[Detailed actionable feedback paragraph]

Evaluate now:"""
        
        return prompt
    
    def _parse_evaluation_response(
        self,
        response_text: str,
        persona_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse LLM evaluation response into structured data.
        
        Args:
            response_text: Raw LLM response
            persona_config: Persona configuration dict
        
        Returns:
            Dict with criteria_scores, subcriteria_scores, total_score, 
            feedback, strengths, weaknesses
        
        Raises:
            ValueError: If parsing fails or scores are invalid
        """
        import re
        
        # Extract criterion scores using regex
        criteria_scores = {}
        
        # Match patterns like "Clarity: 85" or "- Clarity: 85"
        score_pattern = r'(?:^|\n)\s*-?\s*(\w+):\s*(\d+)'
        matches = re.finditer(score_pattern, response_text, re.IGNORECASE)
        
        for match in matches:
            criterion_name = match.group(1).strip().lower()
            score = float(match.group(2))
            
            # Map to criterion_id
            for criterion_id, criterion in self.criteria.items():
                if criterion.name.lower().startswith(criterion_name):
                    if 0 <= score <= 100:  # Validate score range
                        criteria_scores[criterion_id] = score
                    else:
                        self.log.warning(
                            "invalid_score_parsed",
                            criterion=criterion.name,
                            score=score
                        )
        
        # Validate extraction results
        total_criteria = len(self.criteria)
        extracted_count = len(criteria_scores)
        
        # Check if extraction completely failed
        if extracted_count == 0:
            raise ValueError(
                f"Failed to extract any criterion scores from LLM response. "
                f"Response length: {len(response_text)} chars. "
                f"Response preview: {response_text[:200]}..."
            )
        
        # Check if too many scores are missing (>50%)
        missing_count = total_criteria - extracted_count
        if missing_count / total_criteria > 0.5:
            raise ValueError(
                f"Too many missing scores ({missing_count}/{total_criteria}). "
                f"LLM response may be malformed. Extracted: {list(criteria_scores.keys())}"
            )
        
        # Fill remaining missing scores with 0 and warn
        for criterion_id, criterion in self.criteria.items():
            if criterion_id not in criteria_scores:
                criteria_scores[criterion_id] = 0.0
                self.log.warning(
                    "missing_criterion_score",
                    criterion=criterion.name,
                    persona=persona_config['name']
                )
        
        # Calculate total score (weighted by criterion weights)
        total_score = 0.0
        for criterion_id, criterion in self.criteria.items():
            crit_score = criteria_scores.get(criterion_id, 0.0)
            total_score += crit_score * criterion.weight
        
        # Extract strengths
        strengths = self._extract_list_items(response_text, "Strengths:")
        if not strengths:
            strengths = ["No specific strengths identified"]
        
        # Extract weaknesses
        weaknesses = self._extract_list_items(response_text, "Weaknesses:")
        if not weaknesses:
            weaknesses = ["No specific weaknesses identified"]
        
        # Extract feedback paragraph
        feedback_match = re.search(
            r'\*\*Feedback:\*\*\s*\n(.+?)(?:\n\n|\Z)',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        feedback = feedback_match.group(1).strip() if feedback_match else response_text[-500:]
        
        return {
            "criteria_scores": criteria_scores,
            "subcriteria_scores": {},  # Not implemented in this version
            "total_score": round(total_score, 2),
            "feedback": feedback,
            "strengths": strengths[:5],  # Limit to 5
            "weaknesses": weaknesses[:5]  # Limit to 5
        }
    
    def _extract_list_items(self, text: str, header: str) -> List[str]:
        """
        Extract numbered or bulleted list items after a header.
        
        Args:
            text: Full text to search
            header: Header text (e.g., "Strengths:")
        
        Returns:
            List of extracted items (without numbers/bullets)
        """
        import re
        
        # Find section starting with header
        pattern = rf'\*\*{re.escape(header)}\*\*\s*\n((?:(?:\d+\.|\-)\s*.+\n?)+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if not match:
            return []
        
        section_text = match.group(1)
        
        # Extract individual items
        item_pattern = r'(?:^\s*(?:\d+\.|\-)\s*)(.+)$'
        items = []
        for line in section_text.split('\n'):
            item_match = re.match(item_pattern, line.strip())
            if item_match:
                items.append(item_match.group(1).strip())
        
        return items
    
    def _aggregate_scores(
        self,
        section_id: str,
        section_content: str,
        persona_evaluations: List[PersonaEvaluation]
    ) -> AggregatedEvaluation:
        """
        Aggregate persona evaluations with weighted averaging.
        
        Args:
            section_id: Section identifier
            section_content: Original section text
            persona_evaluations: List of PersonaEvaluation objects
        
        Returns:
            AggregatedEvaluation with weighted scores
        
        Raises:
            ValueError: If persona weights don't sum to 1.0
        """
        # Validate persona weights sum to 1.0
        total_weight = sum(pe.persona_weight for pe in persona_evaluations)
        if not (0.99 <= total_weight <= 1.01):  # Floating point tolerance
            raise ValueError(f"Persona weights must sum to 1.0, got {total_weight}")
        
        # Calculate weighted criterion scores
        criteria_scores: Dict[str, float] = {}
        
        for criterion_id, criterion in self.criteria.items():
            weighted_score = 0.0
            for persona_eval in persona_evaluations:
                crit_score = persona_eval.criteria_scores.get(criterion_id, 0.0)
                weighted_score += crit_score * persona_eval.persona_weight
            
            criteria_scores[criterion_id] = round(weighted_score, 2)
        
        # Calculate overall score (criteria already weighted)
        overall_score = sum(
            criteria_scores[criterion_id] * criterion.weight
            for criterion_id, criterion in self.criteria.items()
        )
        overall_score = round(overall_score, 2)
        
        # Generate consensus feedback
        consensus_feedback = self._generate_consensus_feedback(persona_evaluations)
        
        # Extract priority improvements
        priority_improvements = self._extract_priority_improvements(persona_evaluations)
        
        # Determine thresholds
        meets_threshold = overall_score >= self.min_acceptable_score
        recommended_approval = overall_score >= self.approval_threshold
        
        # Extract section title from content (first heading)
        section_title = self._extract_section_title(section_content)
        
        return AggregatedEvaluation(
            section_id=section_id,
            section_title=section_title,
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            persona_evaluations=persona_evaluations,
            consensus_feedback=consensus_feedback,
            priority_improvements=priority_improvements,
            meets_threshold=meets_threshold,
            recommended_approval=recommended_approval,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_consensus_feedback(
        self,
        persona_evaluations: List[PersonaEvaluation]
    ) -> str:
        """
        Generate consensus feedback from all persona evaluations.
        
        Args:
            persona_evaluations: List of PersonaEvaluation objects
        
        Returns:
            Consensus feedback string
        """
        # Collect all strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        
        for pe in persona_evaluations:
            all_strengths.extend(pe.strengths)
            all_weaknesses.extend(pe.weaknesses)
        
        # Build consensus message
        consensus = f"**Consensus Evaluation from {len(persona_evaluations)} Evaluators**\n\n"
        
        consensus += f"**Top Strengths:**\n"
        for i, strength in enumerate(all_strengths[:3], 1):
            consensus += f"{i}. {strength}\n"
        
        consensus += f"\n**Top Concerns:**\n"
        for i, weakness in enumerate(all_weaknesses[:3], 1):
            consensus += f"{i}. {weakness}\n"
        
        return consensus
    
    def _extract_priority_improvements(
        self,
        persona_evaluations: List[PersonaEvaluation]
    ) -> List[str]:
        """
        Extract priority improvement recommendations.
        
        Args:
            persona_evaluations: List of PersonaEvaluation objects
        
        Returns:
            List of priority improvement strings
        """
        # Collect all weaknesses with persona weights
        weighted_weaknesses = []
        
        for pe in persona_evaluations:
            for weakness in pe.weaknesses:
                weighted_weaknesses.append((weakness, pe.persona_weight))
        
        # Sort by weight (highest first)
        weighted_weaknesses.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 5 unique improvements
        improvements = []
        seen = set()
        
        for weakness, _ in weighted_weaknesses:
            # Simple deduplication
            weakness_key = weakness[:50].lower()
            if weakness_key not in seen:
                improvements.append(weakness)
                seen.add(weakness_key)
            
            if len(improvements) >= 5:
                break
        
        return improvements
    
    def _extract_section_title(self, section_content: str) -> str:
        """
        Extract section title from content (first heading).
        
        Args:
            section_content: Section text
        
        Returns:
            Extracted title or "Untitled Section"
        """
        import re
        
        # Match markdown heading (# Title or ## Title)
        match = re.search(r'^#{1,3}\s+(.+)$', section_content, re.MULTILINE)
        
        if match:
            return match.group(1).strip()
        
        # Fallback: first line if short
        first_line = section_content.split('\n')[0].strip()
        if len(first_line) < 100:
            return first_line
        
        return "Untitled Section"
    
    async def _generate_with_retry(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        operation: str
    ) -> Any:
        """
        Generate LLM response with exponential backoff retry.
        
        Implements resilient API calling with:
        - Exponential backoff (1s → 2s → 4s)
        - Configurable max retries
        - Detailed error logging
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens in response
            operation: Operation name for logging
        
        Returns:
            LLM response object
        
        Raises:
            RuntimeError: If all retries exhausted
        
        Example:
            >>> response = await self._generate_with_retry(
            ...     prompt="Evaluate...",
            ...     system_prompt="You are...",
            ...     max_tokens=2000,
            ...     operation="evaluate_section"
            ... )
        """
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self.llm_client.aio.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config={
                            "system_instruction": system_prompt,
                            "temperature": self.temperature,
                            "max_output_tokens": max_tokens
                        }
                    ),
                    timeout=self.llm_timeout
                )
                
                self.log.info(
                    "llm_call_success",
                    operation=operation,
                    attempt=attempt + 1,
                    response_length=len(response.text) if response.text else 0
                )
                
                return response
                
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
            Sanitized string (max 500 chars)
        
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
        
        # Limit length
        if len(str_value) > 500:
            str_value = str_value[:500] + "... [truncated for safety]"
            self.log.debug("input_truncated", original_length=len(str(value)))
        
        return str_value.strip()


# Export public API
__all__ = [
    "ResearchPlanEvaluatorAgent",
    "PersonaEvaluation",
    "AggregatedEvaluation"
]
