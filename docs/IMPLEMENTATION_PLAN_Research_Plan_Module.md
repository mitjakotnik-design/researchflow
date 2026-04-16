# 📋 IMPLEMENTACIJSKI NAČRT: Research Plan Creation Module

**Datum:** 16. April 2026  
**Verzija:** 1.0  
**Status:** Design Phase

---

## 🎯 CILJ MODULA

Dodati **Research Plan Creation** kot **prvi korak** v ResearchFlow workflow, ki omogoča:
1. **Interaktivno kreacijo** raziskovalnega načrta z uporabnikom
2. **Iterativno izboljševanje** vsake sekcije (write → evaluate → revise)
3. **Avtomatsko ocenjevanje** z Multi-Evaluator sistemom
4. **Saturation loop** dokler ne doseže **≥85/100**
5. **Generiranje kritik** če po max iteracijah ne doseže cilja

---

## 🏗️ ARHITEKTURA

### Trenutni Workflow
```
User → Article Generation → Output
```

### Nov Workflow
```
User Login → Research Plan Creation ✨ → Literature Search → Article Generation → Publication
              ↓ (interaktivno)
         [Iteracije do 85+]
              ↓ (če < 85)
         [Critique Report]
```

---

## 📐 KOMPONENTE ZA IMPLEMENTACIJO

### 1. **Agent Layer** (4 novi agenti)

#### 1.1 `ResearchPlanWriterAgent`
```python
# agents/research_plan_writer.py

class ResearchPlanWriterAgent(EnhancedBaseAgent):
    """
    Writes research plan sections based on user input and templates.
    
    Actions:
    - write_section: Generate specific plan section
    - revise_section: Improve based on critique
    - synthesize_plan: Combine sections into cohesive document
    """
```

**Capabilities:**
- Prompt engineering za vsako sekcijo posebej
- Integration user input (research interests, RQ, scope)
- Template-based generation (PRISMA-ScR, PCC framework)
- Revision based on multi-evaluator feedback

#### 1.2 `ResearchPlanEvaluatorAgent`
```python
# agents/research_plan_evaluator.py

class ResearchPlanEvaluatorAgent(EnhancedBaseAgent):
    """
    Evaluates research plan quality with specialized criteria.
    
    Evaluation dimensions:
    - Clarity (25%): RQ jasnost, cilji, struktura
    - Feasibility (25%): Izvedljivost, časovnica, viri
    - Rigor (30%): Metodološka natančnost, PRISMA-ScR
    - Contribution (20%): Pričakovani doprinos, relevantnost
    """
```

**Evaluation personas:**
1. **Methodology Expert** (40%) - PRISMA-ScR compliance, search strategy
2. **Research Supervisor** (30%) - Feasibility, timeline, clarity
3. **Domain Expert** (20%) - Theoretical frameworks, relevance
4. **Ethics Reviewer** (10%) - Ethics considerations, data management

#### 1.3 `ResearchPlanInterviewerAgent`
```python
# agents/research_plan_interviewer.py

class ResearchPlanInterviewerAgent(EnhancedBaseAgent):
    """
    Conducts interactive interview with user to gather requirements.
    
    Interview stages:
    1. Research topic & motivation
    2. Research questions (main + sub)
    3. Theoretical frameworks
    4. Methodology preferences
    5. Constraints (time, budget, resources)
    6. Expected outcomes
    """
```

**Interview flow:**
```
Stage 1: Topic Exploration
  Q1: What is your research topic?
  Q2: Why is this important now?
  Q3: What gaps have you identified?

Stage 2: Research Questions
  Q4: What is your main research question?
  Q5: Any sub-questions?
  Q6: What is your PCC framework? (Population/Concept/Context)

Stage 3: Methodology
  Q7: Why scoping review? (vs systematic, narrative)
  Q8: Databases to search?
  Q9: Time range?
  Q10: Language restrictions?

Stage 4: Resources
  Q11: Timeline (weeks)?
  Q12: Team size?
  Q13: Budget constraints?

Stage 5: Outputs
  Q14: Target journals?
  Q15: Expected contributions?
```

#### 1.4 `ResearchPlanCriticAgent`
```python
# agents/research_plan_critic.py

class ResearchPlanCriticAgent(EnhancedBaseAgent):
    """
    Provides detailed critiques for low-scoring sections.
    
    Critique structure:
    - Overall assessment
    - Critical issues (severity + location + fix)
    - Strengths
    - Improvement suggestions (priority + expected gain)
    - Pathway to target score
    """
```

---

### 2. **Configuration Layer**

#### 2.1 `ResearchPlanSections`
```python
# config/research_plan_sections.py

RESEARCH_PLAN_SECTIONS = {
    "metadata": {
        "name": "Title & Metadata",
        "min_words": 50,
        "max_words": 200,
        "target_score": 85,
        "fields": ["title", "author", "institution", "date", "version"]
    },
    "research_question": {
        "name": "Research Question",
        "min_words": 300,
        "max_words": 600,
        "target_score": 85,
        "components": ["main_rq", "sub_questions", "pcc_framework", "justification"]
    },
    "theoretical_framework": {
        "name": "Theoretical Framework",
        "min_words": 400,
        "max_words": 800,
        "target_score": 85,
        "required_elements": ["theories", "models", "conceptual_framework", "literature_review"]
    },
    "methodology": {
        "name": "Methodology",
        "min_words": 500,
        "max_words": 1000,
        "target_score": 85,
        "subsections": ["design", "prisma_scr_rationale", "search_strategy", "eligibility_criteria"]
    },
    "search_strategy": {
        "name": "Search Strategy",
        "min_words": 400,
        "max_words": 800,
        "target_score": 85,
        "required": ["databases", "search_strings", "boolean_operators", "date_range"]
    },
    "eligibility_criteria": {
        "name": "Eligibility Criteria",
        "min_words": 300,
        "max_words": 600,
        "target_score": 85,
        "required": ["inclusion", "exclusion", "rationale"]
    },
    "data_extraction": {
        "name": "Data Extraction & Charting",
        "min_words": 300,
        "max_words": 600,
        "target_score": 85,
        "elements": ["data_items", "charting_form", "pilot_testing"]
    },
    "quality_assessment": {
        "name": "Quality Assessment",
        "min_words": 200,
        "max_words": 400,
        "target_score": 85,
        "elements": ["criteria", "tools", "independent_review"]
    },
    "identified_gaps": {
        "name": "Identified Gaps",
        "min_words": 400,
        "max_words": 800,
        "target_score": 85,
        "categories": ["theoretical", "empirical", "methodological", "practical"]
    },
    "timeline": {
        "name": "Timeline & Milestones",
        "min_words": 200,
        "max_words": 400,
        "target_score": 85,
        "required": ["phases", "duration", "deliverables"]
    },
    "expected_contributions": {
        "name": "Expected Contributions",
        "min_words": 300,
        "max_words": 600,
        "target_score": 85,
        "dimensions": ["theoretical", "methodological", "practical", "policy"]
    },
    "resources": {
        "name": "Resources & Budget",
        "min_words": 200,
        "max_words": 400,
        "target_score": 85,
        "elements": ["team", "budget", "tools", "access"]
    },
    "ethics": {
        "name": "Ethical Considerations",
        "min_words": 200,
        "max_words": 400,
        "target_score": 85,
        "required": ["approval", "data_management", "conflicts"]
    },
    "dissemination": {
        "name": "Dissemination Strategy",
        "min_words": 200,
        "max_words": 400,
        "target_score": 85,
        "channels": ["academic", "practitioner", "policy", "open_science"]
    },
    "references": {
        "name": "Key References",
        "min_words": 100,
        "max_words": 300,
        "target_score": 85,
        "types": ["theoretical", "methodological", "exemplar_reviews"]
    }
}
```

#### 2.2 `ResearchPlanEvaluationCriteria`
```python
# config/research_plan_evaluation.py

EVALUATION_CRITERIA = {
    "clarity": {
        "weight": 0.25,
        "max_score": 25,
        "subcriteria": {
            "research_questions": 8,  # Clear, focused, answerable
            "objectives": 6,           # Specific, measurable
            "structure": 6,            # Logical flow
            "language": 5              # Academic, precise
        }
    },
    "feasibility": {
        "weight": 0.25,
        "max_score": 25,
        "subcriteria": {
            "timeline": 8,             # Realistic schedule
            "resources": 7,            # Adequate team/budget
            "scope": 5,                # Manageable scope
            "risks": 5                 # Risk mitigation
        }
    },
    "rigor": {
        "weight": 0.30,
        "max_score": 30,
        "subcriteria": {
            "methodology": 10,         # PRISMA-ScR alignment
            "search_strategy": 8,      # Comprehensive, reproducible
            "eligibility": 6,          # Clear criteria
            "quality_assessment": 6    # Appropriate tools
        }
    },
    "contribution": {
        "weight": 0.20,
        "max_score": 20,
        "subcriteria": {
            "novelty": 7,              # Original contribution
            "significance": 7,         # Impact potential
            "implications": 6          # Practical utility
        }
    }
}
```

---

### 3. **Orchestration Layer**

#### 3.1 `ResearchPlanOrchestrator`
```python
# orchestration/research_plan_orchestrator.py

class ResearchPlanOrchestrator:
    """
    Orchestrates research plan creation workflow.
    
    Workflow stages:
    1. User Interview (gather requirements)
    2. Section Generation (iterative, per section)
    3. Evaluation Loop (multi-evaluator)
    4. Revision Loop (if score < 85)
    5. Critique Generation (if max iterations reached)
    6. Final Assembly (combine sections)
    7. Export (MD + PDF)
    """
    
    async def create_research_plan(self, user_id: str):
        # Stage 1: Interview
        requirements = await self.interview_user()
        
        # Stage 2-5: Process each section
        plan_sections = {}
        critique_reports = {}
        
        for section_id, section_spec in RESEARCH_PLAN_SECTIONS.items():
            result = await self.process_section(
                section_id=section_id,
                requirements=requirements,
                target_score=section_spec["target_score"]
            )
            
            if result.final_score >= section_spec["target_score"]:
                plan_sections[section_id] = result.content
            else:
                # Generate critique report
                critique = await self.generate_critique_report(
                    section_id=section_id,
                    content=result.content,
                    score=result.final_score,
                    iteration_history=result.iterations
                )
                critique_reports[section_id] = critique
        
        # Stage 6: Assembly
        final_plan = self.assemble_plan(plan_sections)
        
        # Stage 7: Export
        self.export_plan(final_plan, critique_reports)
        
        return final_plan, critique_reports
    
    async def process_section(self, section_id, requirements, target_score):
        """Process single section with saturation loop."""
        
        section_result = SectionResult(section_id=section_id)
        iteration = 0
        previous_feedback = []
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Write/Revise
            if iteration == 1:
                content = await self.writer.write_section(
                    section_id=section_id,
                    requirements=requirements
                )
            else:
                content = await self.writer.revise_section(
                    section_id=section_id,
                    current_content=content,
                    feedback=previous_feedback
                )
            
            # Evaluate
            evaluation = await self.evaluator.evaluate(
                section_id=section_id,
                content=content,
                iteration=iteration
            )
            
            section_result.add_iteration(
                content=content,
                score=evaluation["overall_score"],
                evaluation=evaluation
            )
            
            # Check if target reached
            if evaluation["overall_score"] >= target_score:
                section_result.finalize(success=True)
                return section_result
            
            # Prepare feedback for next iteration
            previous_feedback = evaluation.get("improvement_suggestions", [])
            
            # Early stop if no improvement
            if iteration > 1 and not self._has_improvement(section_result):
                break
        
        # Max iterations reached
        section_result.finalize(success=False)
        return section_result
```

#### 3.2 `ResearchPlanSaturationLoop`
```python
# orchestration/research_plan_saturation_loop.py

class ResearchPlanSaturationLoop(SaturationLoop):
    """
    Specialized saturation loop for research plan sections.
    
    Differences from article saturation loop:
    - Different evaluation criteria
    - Interactive user feedback option
    - Section dependencies (e.g., RQ → Methodology)
    """
    
    async def run(self, section_spec, user_requirements):
        # Similar to article saturation loop but:
        # 1. Uses ResearchPlanEvaluator
        # 2. Considers user requirements explicitly
        # 3. May pause for user confirmation
        pass
```

---

### 4. **Scripts Layer**

#### 4.1 Main Generation Script
```python
# scripts/generate_research_plan.py

"""
Interactive Research Plan Generator

Usage:
    python scripts/generate_research_plan.py
    
Features:
- Interactive interview with user
- Iterative section generation
- Automatic evaluation and revision
- Critique report generation for low-scoring sections
"""

async def main():
    print("\n" + "="*70)
    print("   RESEARCHFLOW: RESEARCH PLAN CREATION")
    print("="*70 + "\n")
    
    # Initialize
    orchestrator = ResearchPlanOrchestrator()
    
    # User interview
    print("[STAGE 1] User Interview")
    requirements = await orchestrator.interview_user()
    
    # Generate plan
    print("\n[STAGE 2] Plan Generation")
    plan, critiques = await orchestrator.create_research_plan(
        requirements=requirements
    )
    
    # Report
    print("\n[STAGE 3] Results")
    print(f"  Sections completed: {len(plan.sections)}")
    print(f"  Sections needing revision: {len(critiques)}")
    
    if critiques:
        print("\n[STAGE 4] Critique Reports Generated")
        for section_id in critiques.keys():
            print(f"  - {section_id}: See CRITIQUES_Plan_{section_id}.md")
    
    print("\n✅ Research Plan Creation Complete!")
    print(f"📄 Output: output/research_plan_{plan.id}.md")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 4.2 Critique Extraction Script
```python
# scripts/extract_plan_critiques.py

"""
Extract detailed critiques for low-scoring research plan sections.
Mirrors extract_critiques.py functionality.
"""

async def extract_plan_critiques(section_id, content, score, iterations):
    """Generate comprehensive critique report."""
    
    critique = await generate_comprehensive_critique(
        llm_client=llm_client,
        section_name=section_id,
        content=content,
        current_score=score,
        plan_context=True  # Special flag for plan context
    )
    
    # Generate SL & EN reports
    sl_report = generate_slovenian_plan_report(critique)
    en_report = generate_english_plan_report(critique)
    
    # Export
    save_report(sl_report, f"CRITIQUES_Plan_{section_id}_SL.md")
    save_report(en_report, f"CRITIQUES_Plan_{section_id}_EN.md")
```

---

## 📊 EVALVACIJSKI SISTEM

### Evaluation Flow
```
Section Content
    ↓
Multi-Persona Evaluation
├── Methodology Expert (40%) → Rigor focus
├── Research Supervisor (30%) → Feasibility focus  
├── Domain Expert (20%)       → Contribution focus
└── Ethics Reviewer (10%)     → Ethics focus
    ↓
Weighted Consensus Score
    ↓
[Score ≥ 85?]
    ├── YES → Approve section
    └── NO  → Generate feedback → Revision loop
```

### Evaluation Prompts (Example)

```python
EVALUATION_PROMPT_TEMPLATE = """
You are a {persona} evaluating a research plan {section_name} section.

**Your focus:** {persona_focus}

**Evaluation criteria:**
- Clarity: {clarity_criteria}
- Feasibility: {feasibility_criteria}
- Rigor: {rigor_criteria}
- Contribution: {contribution_criteria}

**Section content:**
{content}

**Task:** Score each criterion (0-100) and provide specific, actionable feedback.

Output JSON:
{{
    "scores": {{
        "clarity": 0-25,
        "feasibility": 0-25,
        "rigor": 0-30,
        "contribution": 0-20
    }},
    "strengths": ["strength 1", "strength 2"],
    "critical_issues": [
        {{
            "issue": "specific problem",
            "severity": "critical|major|moderate|minor",
            "location": "where in text",
            "fix": "how to address"
        }}
    ],
    "improvement_suggestions": [
        {{
            "area": "what to improve",
            "priority": "high|medium|low",
            "current_problem": "issue description",
            "suggested_fix": "actionable recommendation",
            "expected_gain": "+X points"
        }}
    ]
}}
"""
```

---

## 🔄 ITERACIJSKI PROCES

### Single Section Lifecycle

```
┌─────────────────────────────────────────┐
│  1. Write Section (Initial Draft)      │
│     - Based on user requirements        │
│     - Use templates & examples          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  2. Evaluate Section                    │
│     - Multi-persona scoring             │
│     - Generate feedback                 │
└──────────────┬──────────────────────────┘
               ↓
          [Score ≥ 85?]
               ├── YES → ✅ Approve
               └── NO → ↓
┌─────────────────────────────────────────┐
│  3. Generate Critique                   │
│     - Identify specific issues          │
│     - Prioritize improvements           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  4. Revise Section                      │
│     - Address feedback                  │
│     - Improve weak areas                │
└──────────────┬──────────────────────────┘
               ↓
          [Iteration < Max?]
               ├── YES → Back to step 2
               └── NO → ↓
┌─────────────────────────────────────────┐
│  5. Generate Final Critique Report      │
│     - Comprehensive feedback            │
│     - Pathway to target score           │
│     - Recommendations for user          │
└─────────────────────────────────────────┘
```

---

## 📁 FILE STRUCTURE

```
scoping-review-agents/
├── agents/
│   ├── research_plan_writer.py         ✨ NEW
│   ├── research_plan_evaluator.py      ✨ NEW
│   ├── research_plan_interviewer.py    ✨ NEW
│   └── research_plan_critic.py         ✨ NEW
│
├── config/
│   ├── research_plan_sections.py       ✨ NEW
│   └── research_plan_evaluation.py     ✨ NEW
│
├── orchestration/
│   ├── research_plan_orchestrator.py   ✨ NEW
│   └── research_plan_saturation_loop.py ✨ NEW
│
├── scripts/
│   ├── generate_research_plan.py       ✨ NEW
│   └── extract_plan_critiques.py       ✨ NEW
│
├── templates/
│   └── research_plan/                  ✨ NEW
│       ├── metadata_template.md
│       ├── research_question_template.md
│       ├── methodology_template.md
│       └── ...
│
└── output/
    └── research_plans/                 ✨ NEW
        ├── plan_20260416_001.md
        ├── plan_20260416_001_critiques/
        │   ├── CRITIQUES_RQ_SL.md
        │   ├── CRITIQUES_RQ_EN.md
        │   └── ...
        └── ...
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create agent base classes
  - [ ] `ResearchPlanWriterAgent`
  - [ ] `ResearchPlanEvaluatorAgent`
- [ ] Define section configurations
  - [ ] `research_plan_sections.py`
  - [ ] `research_plan_evaluation.py`
- [ ] Setup test framework
  - [ ] Unit tests for agents
  - [ ] Mock evaluation tests

### Phase 2: Orchestration (Week 2)
- [ ] Build orchestrator
  - [ ] `ResearchPlanOrchestrator`
  - [ ] `ResearchPlanSaturationLoop`
- [ ] Implement section processing
  - [ ] Write → Evaluate → Revise loop
  - [ ] Score tracking
  - [ ] Early stopping logic
- [ ] Integration tests
  - [ ] Full section lifecycle
  - [ ] Multi-section coordination

### Phase 3: User Interface (Week 3)
- [ ] Interactive interview agent
  - [ ] `ResearchPlanInterviewerAgent`
  - [ ] Question flow
  - [ ] Input validation
- [ ] Main generation script
  - [ ] `generate_research_plan.py`
  - [ ] CLI interface
  - [ ] Progress reporting
- [ ] User testing
  - [ ] Usability evaluation
  - [ ] Feedback collection

### Phase 4: Critique System (Week 4)
- [ ] Critique generation
  - [ ] `ResearchPlanCriticAgent`
  - [ ] Multi-language reports (SL/EN)
- [ ] Critique extraction script
  - [ ] `extract_plan_critiques.py`
  - [ ] Report templates
- [ ] Quality assurance
  - [ ] Critique accuracy testing
  - [ ] Report clarity review

### Phase 5: Integration & Polish (Week 5)
- [ ] Integrate with main workflow
  - [ ] User login → Research Plan → Article
  - [ ] State management
  - [ ] Checkpoint/resume functionality
- [ ] Documentation
  - [ ] User guide
  - [ ] API documentation
  - [ ] Example workflows
- [ ] Deployment
  - [ ] Production configuration
  - [ ] Monitoring setup
  - [ ] Performance optimization

---

## 📝 EXAMPLE OUTPUT

### Research Plan Structure
```markdown
# Research Plan: AI in HRM Scoping Review

## Metadata
- **Title:** Psychosocial Risks of AI Implementation in HR
- **Author:** Dr. Jane Doe
- **Institution:** University of Example
- **Version:** 2.0
- **Date:** 2026-04-16
- **Status:** Ready for PROSPERO Registration

## 1. Research Question ⭐ 92/100
**Main RQ:** How does AI implementation through HR functions affect...

[Generated content with high score]

## 2. Theoretical Framework ⭐ 88/100
**Theories:**
- Job Demands-Resources (JD-R) Model
- Conservation of Resources (COR) Theory
...

## 3. Methodology ⚠️ 73/100
[Generated content - needs revision]

**Critique Report Available:**
- See: CRITIQUES_Plan_Methodology_SL.md
- Priority fixes: Search strategy specificity, PRISMA-ScR alignment
- Expected improvements: +12 points to reach 85

...
```

### Critique Report Example
```markdown
# 📋 KRITIKE: Research Plan - Methodology Section

**Trenutna ocena:** 73/100
**Potrebna revizija:** Manjša

## Kritične težave

### 1. Nepopolna iskalna strategija (Metodolog) 🔴
**Problem:** Boolean operatorji niso specificiran...
**Rešitev:** Dodati exact search strings z AND/OR/NOT...
**Pričakovan dobiček:** +5 točk

...
```

---

## 🎯 SUCCESS METRICS

### Quality Metrics
- **Target:** ≥85/100 for all sections
- **Acceptable:** ≥75/100 with documented critique
- **Unacceptable:** <75/100 (requires revision before proceeding)

### Performance Metrics
- **Generation time:** <30 minutes per section
- **Iteration efficiency:** Average 2-3 iterations to reach 85+
- **User satisfaction:** ≥4.5/5 stars

### System Metrics
- **API success rate:** ≥99%
- **Evaluation consistency:** Inter-rater kappa ≥0.8
- **Critique usefulness:** User rating ≥4.0/5

---

## 🔧 CONFIGURATION EXAMPLES

### User Requirements Schema
```python
@dataclass
class ResearchPlanRequirements:
    # Basic info
    research_topic: str
    motivation: str
    
    # Research questions
    main_rq: str
    sub_questions: list[str]
    pcc_framework: PCCFramework
    
    # Methodology
    review_type: str  # "scoping", "systematic", "narrative"
    databases: list[str]
    date_range: tuple[int, int]
    language_restrictions: list[str]
    
    # Resources
    timeline_weeks: int
    team_size: int
    budget: Optional[float]
    
    # Outputs
    target_journals: list[str]
    expected_contributions: list[str]
```

### Saturation Config for Research Plans
```python
RESEARCH_PLAN_SATURATION_CONFIG = SaturationConfig(
    target_score=85,           # Higher than articles (85 vs 75)
    minimum_acceptable=75,     # Still acceptable with critique
    max_iterations=5,          # Fewer iterations (5 vs 7)
    early_stop_if_no_improvement=2,
    min_improvement_delta=2.0,
    allow_user_intervention=True  # ✨ NEW: User can provide input
)
```

---

## 🤝 USER INTERACTION POINTS

### 1. Initial Interview (Required)
- User answers 15-20 questions
- Duration: 15-30 minutes
- Can save & resume

### 2. Section Review (Optional)
- After each section completes
- User can preview & provide feedback
- System incorporates feedback in next section

### 3. Low-Score Intervention (Automatic)
- If section scores <75 after max iterations
- System pauses & shows critique report
- User can:
  - a) Accept with documented limitations
  - b) Provide additional input for revision
  - c) Manually edit & resubmit for evaluation

### 4. Final Approval (Required)
- Review complete plan
- Approve to proceed to literature search
- Export options: MD, PDF, DOCX

---

## 📚 DEPENDENCIES

### Existing Dependencies (Reuse)
- ✅ `LLMClientFactory` (Gemini models)
- ✅ `Multi-Evaluator` pattern
- ✅ `SaturationLoop` architecture
- ✅ `StateManager`
- ✅ Template system

### New Dependencies
- 🆕 Interactive CLI library (e.g., `questionary`)
- 🆕 PDF generation (already have: `fpdf2`, `weasyprint`)
- 🆕 DOCX export (e.g., `python-docx`)

---

## ⚠️ RISKS & MITIGATION

### Risk 1: User Abandonment
**Risk:** User stops mid-interview  
**Mitigation:** 
- Save progress after each question
- Allow resume from checkpoint
- Keep questions concise (<50 words)

### Risk 2: Low Scores Despite Iterations
**Risk:** Section can't reach 85+ in max iterations  
**Mitigation:**
- Generate comprehensive critique report
- Allow user to accept with documented limitations
- Provide manual editing option

### Risk 3: Integration Complexity
**Risk:** Research Plan → Article workflow breaks  
**Mitigation:**
- Versioned APIs between modules
- Comprehensive integration tests
- Rollback mechanism

### Risk 4: Evaluation Inconsistency
**Risk:** Evaluator scores vary too much  
**Mitigation:**
- Use multiple personas with weighted consensus
- Track evaluation variance
- Calibrate against human expert ratings

---

## 🎓 NEXT STEPS

### Immediate (Today)
1. ✅ Review & approve this implementation plan
2. 🔲 Setup git branch: `feature/research-plan-module`
3. 🔲 Create skeleton files & directory structure

### This Week
4. 🔲 Implement Phase 1: Core Infrastructure
5. 🔲 Write unit tests for agents
6. 🔲 Begin Phase 2: Orchestration

### Next Sprint (2 weeks)
7. 🔲 Complete Phases 3-4
8. 🔲 Internal testing
9. 🔲 User pilot study

---

## 📊 APPENDIX: Template Examples

### A. Research Question Template
```markdown
## Research Question

### Main Research Question
{main_rq}

### Sub-Questions
1. {sub_question_1}
2. {sub_question_2}
...

### PCC Framework
- **Population:** {population}
- **Concept:** {concept}
- **Context:** {context}

### Rationale
{justification_for_rq}
```

### B. Search Strategy Template
```markdown
## Search Strategy

### Databases
- Web of Science
- Scopus
- PubMed
...

### Search String (Example: Web of Science)
```
TS=(("artificial intelligence" OR "machine learning" OR AI OR ML) 
AND ("human resource*" OR HRM OR "personnel management") 
AND (risk* OR stress OR wellbeing OR "work environment"))
```

### Date Range
{start_year} - {end_year}

### Language
{languages}
```

---

**Document End**

*For questions or clarifications, contact the ResearchFlow development team.*
