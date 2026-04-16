# 🎯 DECISION FRAMEWORK: Kdaj Uporabiti 3-Phase Metodologijo

**Datum:** 16. April 2026  
**Namen:** Optimizacija rigor vs efficiency pri razvoju komponent  
**Princip:** **Risk-Based Quality Assurance**

---

## 🧭 FILOZOFIJA

> **"Critic review tam, kjer je tveganje. Hitrost tam, kjer je stvar jasna."**

**Nikoli:**
- ❌ Slepo uporabljaj 3-phase za vse (waste of time)
- ❌ Skippaj kritik pri visoko rizičnih komponentah (quality disaster)

**Vedno:**
- ✅ Oceni **kompleksnost** in **tveganje** pred začetkom
- ✅ Prilagodi proces glede na **risk level**
- ✅ Testiraj **vedno** (100% non-negotiable)

---

## 📊 DECISION MATRIX

### Kompleksnost × Tveganje → Proces

```
┌─────────────────────────────────────────────────────────────┐
│                    KOMPLEKSNOST                             │
│              LOW         MEDIUM          HIGH               │
├──────────┬───────────┬────────────┬──────────────────────────┤
│          │           │            │                          │
│  HIGH    │ 2-PHASE   │  FULL      │   FULL + MICROSCOPE     │
│          │ Quick     │ 3-PHASE    │   3-PHASE               │
│  RISK    │ Review    │            │                          │
│          │           │            │   (Extra scrutiny)       │
├──────────┼───────────┼────────────┼──────────────────────────┤
│          │           │            │                          │
│  MEDIUM  │ 1-PHASE   │  2-PHASE   │   FULL 3-PHASE          │
│          │ Test only │ Quick      │                          │
│  RISK    │           │ Review     │                          │
│          │           │            │                          │
├──────────┼───────────┼────────────┼──────────────────────────┤
│          │           │            │                          │
│  LOW     │ 1-PHASE   │  1-PHASE   │   2-PHASE               │
│          │ Test only │ Test only  │   Quick Review          │
│  RISK    │           │            │                          │
│          │           │            │                          │
└──────────┴───────────┴────────────┴──────────────────────────┘
```

---

## 🔍 KOMPLEKSNOST KRITËRIJI

| Factor | LOW (1 pt) | MEDIUM (2 pts) | HIGH (3 pts) |
|--------|------------|----------------|--------------|
| **Lines of code** | <100 | 100-300 | 300+ |
| **Dependencies** | 0-2 | 3-5 | 6+ |
| **Logic complexity** | Linear | Branching | Nested/recursive |
| **External APIs** | None | 1 API | 2+ APIs |
| **Data transformations** | Simple | Moderate | Complex (multi-step) |
| **State management** | Stateless | Simple state | Complex state machine |

**Total Score:**
- **LOW:** 1-6 points
- **MEDIUM:** 7-12 points
- **HIGH:** 13-18 points

---

## ⚠️ TVEGANJE KRITERIJI

| Factor | LOW (1 pt) | MEDIUM (2 pts) | HIGH (3 pts) |
|--------|------------|----------------|--------------|
| **User impact** | Internal tool only | Dev team uses | End users affected |
| **Financial impact** | None | <€100 API costs | €100+ API costs |
| **Data sensitivity** | Public data | Internal data | Personal/sensitive |
| **Error consequences** | Easy to fix | Requires debugging | Critical failure |
| **Reversibility** | Instantly reversible | Reversible with effort | Hard to reverse |
| **Validation difficulty** | Easy to verify | Manual checking | Complex validation |

**Total Score:**
- **LOW:** 1-6 points
- **MEDIUM:** 7-12 points
- **HIGH:** 13-18 points

---

## 🚦 PROCESS DEFINITIONS

### 1-PHASE: Test Only ⚡ (Fastest)

**When to use:**
- Simple utility functions
- Data structure definitions
- Configuration files (already done)
- Straightforward CRUD operations

**Steps:**
1. ✅ Implement
2. ✅ Write unit tests
3. ✅ Run tests → all green
4. ❌ **SKIP** critic review
5. ❌ **SKIP** improvement cycle

**Time:** ~1-2 hours per component

**Example:**
```python
# Simple helper function
def format_section_title(title: str) -> str:
    """Format section title with proper capitalization."""
    return title.title().strip()

# Test only - no critic needed
def test_format_section_title():
    assert format_section_title("hello world") == "Hello World"
    assert format_section_title("  test  ") == "Test"
```

---

### 2-PHASE: Quick Review ⚡⚡ (Fast)

**When to use:**
- Medium complexity components
- Non-critical business logic
- UI components
- API wrappers (simple)

**Steps:**
1. ✅ Implement
2. ✅ Write unit tests
3. ✅ Run tests → all green
4. ✅ **Quick review** (15-30 min)
   - Check obvious issues (typos, logic errors)
   - Verify test coverage adequate
   - No detailed scoring
5. ✅ **Quick fixes** if needed (< 1 hour)

**Time:** ~2-4 hours per component

**Quick Review Checklist:**
```markdown
- [ ] Code runs without errors
- [ ] Tests cover main paths
- [ ] No obvious bugs
- [ ] Naming conventions followed
- [ ] Documentation present
```

---

### FULL 3-PHASE: Implement → Critic → Improve 🔍 (Thorough)

**When to use:**
- Complex agents (LLM interaction)
- Multi-step workflows
- Scoring/evaluation logic
- Business-critical components

**Steps:**
1. ✅ Implement (skeleton + core logic)
2. ✅ Write comprehensive unit tests
3. ✅ Run tests → all green
4. ✅ **Full critic review** (1-2 hours)
   - Score: Architecture, Functionality, Robustness, Testing, Code Quality
   - Identify issues (HIGH/MEDIUM/LOW priority)
   - Generate detailed report
5. ✅ **Implement HIGH priority fixes** (2-4 hours)
6. ✅ Re-test → verify fixes
7. ✅ (Optional) Second critic review if score < 8.5

**Time:** ~8-12 hours per component

**Critic Review Template:**
```markdown
## Component: [Name]

### Score: X.X/10

### Issues Found:
- 🔴 HIGH: [Critical issue requiring fix]
- ⚠️ MEDIUM: [Important but not blocking]
- ℹ️ LOW: [Nice to have]

### Recommendation: 
- [ ] APPROVED (score ≥9.0)
- [ ] APPROVED with minor improvements (8.0-8.9)
- [ ] NEEDS FIXES (7.0-7.9)
- [ ] MAJOR REWORK (<7.0)
```

---

### MICROSCOPE 3-PHASE: Full + Extra Scrutiny 🔬 (Maximum Rigor)

**When to use:**
- Foundation components (used by everything)
- Security-critical code
- Financial calculations
- Data pipeline orchestration
- Meta-components (CriticAgent reviewing CriticAgent)

**Steps:**
1. ✅ Implement
2. ✅ Write comprehensive unit tests + integration tests
3. ✅ Run tests → all green
4. ✅ **Full critic review** (detailed)
5. ✅ **Implement ALL fixes** (HIGH + MEDIUM priority)
6. ✅ Re-test
7. ✅ **Microscope review** (line-by-line)
   - Check every edge case
   - Verify input validation
   - Look for subtle bugs
   - Performance analysis
8. ✅ Final fixes
9. ✅ **Validation:** Score must be ≥9.0

**Time:** ~16-24 hours per component

**Microscope Checklist:**
```markdown
- [ ] Every input validated
- [ ] Every error path tested
- [ ] No magic numbers
- [ ] No code duplication
- [ ] Performance acceptable
- [ ] Memory leaks checked
- [ ] Concurrency issues addressed
- [ ] Documentation complete
- [ ] Examples provided
```

---

## 🎯 AGENT-SPECIFIC GUIDELINES

### ResearchPlanWriterAgent

**Assessment:**
- **Complexity:** HIGH (3 pts)
  - LLM prompting (complex)
  - Multiple actions (write, revise, synthesize)
  - Context management
  - Template integration
  - ~400-500 lines
- **Risk:** HIGH (3 pts)
  - Generated content quality critical
  - API costs significant (Gemini API)
  - User directly sees output
  - Hard to validate automatically
  - Errors propagate to final document

**Total:** 
- Complexity: 13+ pts → **HIGH**
- Risk: 13+ pts → **HIGH**

**Decision:** ✅ **FULL 3-PHASE**

**Rationale:**
- LLM prompting is art + science (needs iteration)
- Template integration can be tricky
- Quality of generated text is critical
- Critic review will catch prompt issues before production

**Process:**
1. Implement WriterAgent skeleton + 3 core actions
2. Write 15-20 unit tests (mock LLM responses)
3. Run tests → all green
4. **Critic review** (score all dimensions)
5. Fix HIGH priority issues (prompts, error handling)
6. Re-test
7. ✅ Ready if score ≥8.5

**Time Budget:** ~10-12 hours

---

### ResearchPlanEvaluatorAgent

**Assessment:**
- **Complexity:** HIGH (3 pts)
  - Multi-persona evaluation
  - Scoring aggregation (weighted)
  - Consensus logic
  - Integration with 21 subcriteria
  - ~350-450 lines
- **Risk:** HIGH (3 pts)
  - Scoring accuracy critical (determines plan approval)
  - Mathematical errors = wrong decisions
  - Financial impact (reject good plan / approve bad plan)
  - Hard to debug scoring issues

**Total:**
- Complexity: 14 pts → **HIGH**
- Risk: 15 pts → **HIGH**

**Decision:** ✅ **FULL 3-PHASE**

**Rationale:**
- Math errors are subtle and dangerous
- Multi-persona consensus needs careful design
- Scoring bugs hard to catch without critique
- Critic will verify calculation logic

**Time Budget:** ~10-12 hours

---

### ResearchPlanInterviewerAgent

**Assessment:**
- **Complexity:** MEDIUM (2 pts)
  - Question generation (simpler LLM task)
  - Sequential Q&A flow
  - Context accumulation
  - ~200-250 lines
- **Risk:** MEDIUM (2 pts)
  - User experience affected but not critical
  - API costs moderate
  - Easy to iterate based on user feedback
  - Errors visible immediately (user notices)

**Total:**
- Complexity: 9 pts → **MEDIUM**
- Risk: 9 pts → **MEDIUM**

**Decision:** ✅ **2-PHASE (Quick Review)**

**Rationale:**
- Simpler than Writer/Evaluator
- User feedback will surface issues quickly
- Not mission-critical (nice UX enhancement)
- Quick review sufficient to catch obvious issues

**Time Budget:** ~4-6 hours

---

### ResearchPlanCriticAgent

**Assessment:**
- **Complexity:** HIGH (3 pts)
  - Complex evaluation logic
  - Report generation
  - Meta-critique (reviewing other agents)
  - Scoring multiple dimensions
  - ~300-400 lines
- **Risk:** HIGH (3 pts)
  - Meta-component (if broken, affects all reviews)
  - Quality gate for entire system
  - Circular dependency risk (who reviews the reviewer?)
  - Financial impact (bad critiques waste developer time)

**Total:**
- Complexity: 14 pts → **HIGH**
- Risk: 16 pts → **HIGH**

**Decision:** ✅ **MICROSCOPE 3-PHASE** 🔬

**Rationale:**
- **Meta-component risk:** If CriticAgent is broken, entire quality system fails
- Needs extra scrutiny (microscope review)
- Must be bulletproof before use
- Self-review paradox requires external validation

**Special Process:**
1. Implement CriticAgent
2. Write comprehensive tests
3. **Full critic review** (by human or earlier critic version)
4. Fix ALL issues (HIGH + MEDIUM)
5. **Microscope review** (line-by-line)
6. **Validation:** Test on known good/bad code samples
7. ✅ Score must be ≥9.0

**Time Budget:** ~16-20 hours

---

## 📋 DECISION CHECKLIST

### Before Starting Any Component:

**Step 1: Assess Complexity** (1-18 pts)
```
[ ] Lines of code estimate: ___
[ ] Dependencies count: ___
[ ] Logic complexity: Linear / Branching / Nested
[ ] External APIs: ___
[ ] Data transformations: Simple / Moderate / Complex
[ ] State management: Stateless / Simple / Complex

Total Complexity: ___ pts (LOW/MEDIUM/HIGH)
```

**Step 2: Assess Risk** (1-18 pts)
```
[ ] User impact: Internal / Dev team / End users
[ ] Financial impact: None / <€100 / €100+
[ ] Data sensitivity: Public / Internal / Sensitive
[ ] Error consequences: Easy fix / Debugging / Critical
[ ] Reversibility: Instant / Effortful / Hard
[ ] Validation difficulty: Easy / Manual / Complex

Total Risk: ___ pts (LOW/MEDIUM/HIGH)
```

**Step 3: Select Process**
```
Complexity: ________ 
Risk: ________

Process: [ ] 1-Phase [ ] 2-Phase [ ] Full 3-Phase [ ] Microscope

Time Budget: _____ hours
```

**Step 4: Execute**
```
[ ] Step 1: Implement
[ ] Step 2: Test
[ ] Step 3: (If applicable) Critic Review
[ ] Step 4: (If applicable) Improve
[ ] Step 5: (If applicable) Re-test
[ ] Step 6: (If applicable) Microscope Review
```

---

## 🎯 PRAGMATIC HEURISTICS

### "When in Doubt" Rules:

1. **API-heavy component?** → Full 3-Phase
   - LLM calls are expensive and hard to validate
   - Prompts need iteration

2. **Math/calculations?** → Full 3-Phase
   - Math bugs are subtle
   - Unit tests catch obvious errors, critic catches logic errors

3. **User-facing?** → At least 2-Phase
   - UX issues need human review
   - Tests don't catch all usability problems

4. **Pure data structure?** → 1-Phase
   - Dataclasses, configs, simple types
   - Tests are sufficient

5. **Foundation component?** → Microscope 3-Phase
   - Everything depends on it
   - Must be rock-solid

6. **Meta-component?** → Microscope 3-Phase
   - Circular dependency risk
   - Extra scrutiny necessary

7. **Prototype/experiment?** → 1-Phase initially
   - Fast iteration
   - Add rigor when promoting to production

### Time vs Quality Trade-offs:

```
┌────────────────────────────────────────────────┐
│  Time-Constrained Project                     │
│  ────────────────────────                     │
│  • Use 1-Phase for utilities                  │
│  • Use 2-Phase for most components            │
│  • Reserve Full 3-Phase for 2-3 critical      │
│                                                │
│  Quality-Critical Project (ResearchFlow)      │
│  ────────────────────────────────────         │
│  • Use 2-Phase minimum                        │
│  • Full 3-Phase for agents                    │
│  • Microscope for foundation                  │
└────────────────────────────────────────────────┘
```

---

## ✅ RESEARCHFLOW AGENT PLAN

### Phase 1: Core Infrastructure

| Component | Complexity | Risk | Process | Time | Status |
|-----------|------------|------|---------|------|--------|
| research_plan_sections.py | MEDIUM | HIGH | Full 3-Phase | 12h | ✅ 9.4/10 |
| research_plan_evaluation.py | MEDIUM | HIGH | Full 3-Phase | 12h | ✅ 9.4/10 |
| **WriterAgent** | **HIGH** | **HIGH** | **Full 3-Phase** | **10-12h** | ⏳ **NEXT** |
| **EvaluatorAgent** | **HIGH** | **HIGH** | **Full 3-Phase** | **10-12h** | ⏳ Pending |

### Phase 2: Orchestration

| Component | Complexity | Risk | Process | Time | Status |
|-----------|------------|------|---------|------|--------|
| ResearchPlanOrchestrator | HIGH | HIGH | Full 3-Phase | 12h | ⏳ Pending |
| SaturationLoop | MEDIUM | MEDIUM | 2-Phase | 4h | ⏳ Pending |

### Phase 3: User Interface

| Component | Complexity | Risk | Process | Time | Status |
|-----------|------------|------|---------|------|--------|
| InterviewerAgent | MEDIUM | MEDIUM | 2-Phase | 4-6h | ⏳ Pending |
| CLI Interface | LOW | LOW | 1-Phase | 2h | ⏳ Pending |

### Phase 4: Critique System

| Component | Complexity | Risk | Process | Time | Status |
|-----------|------------|------|---------|------|--------|
| **CriticAgent** | **HIGH** | **HIGH** | **Microscope** | **16-20h** | ⏳ Pending |
| Report Generator | MEDIUM | LOW | 2-Phase | 4h | ⏳ Pending |

### Phase 5: Integration & Polish

| Component | Complexity | Risk | Process | Time | Status |
|-----------|------------|------|---------|------|--------|
| End-to-end tests | HIGH | HIGH | Full 3-Phase | 8h | ⏳ Pending |
| Documentation | LOW | LOW | 1-Phase | 4h | ⏳ Pending |

**Total Time:**
- Full 3-Phase: 62-68 hours (6 components)
- 2-Phase: 12-14 hours (3 components)
- 1-Phase: 6 hours (2 components)
- **Grand Total: 80-88 hours** (~10-11 work days)

---

## 🚀 IMMEDIATE ACTION: WriterAgent

**Decision:** ✅ **FULL 3-PHASE**

**Justification:**
- Complexity: HIGH (LLM prompting, template integration)
- Risk: HIGH (output quality critical, API costs)
- Foundation for all section generation
- Prompts are complex and need iteration

**Time Budget:** 10-12 hours

**Breakdown:**
1. **Implement** (4-5 hours)
   - Agent skeleton
   - 3 core actions (write, revise, synthesize)
   - Prompt templates
   - Context management
   
2. **Test** (2-3 hours)
   - 15-20 unit tests
   - Mock LLM responses
   - Edge cases
   
3. **Critic Review** (1-2 hours)
   - Score: Architecture, Functionality, Robustness, Testing, Code Quality
   - Identify issues
   - Generate report
   
4. **Improve** (2-3 hours)
   - Fix HIGH priority issues
   - Refine prompts
   - Enhance error handling
   
5. **Re-test** (30 min)
   - Verify fixes
   - All tests green

**Target Score:** ≥8.5/10

---

## 📚 LESSONS LEARNED

### What Worked (Config Phase):

✅ **Full 3-Phase was worth it:**
- Caught 7 issues before production
- Improved from 8.2 → 9.3 → 9.4
- High confidence in foundation

✅ **Microscope review caught typos:**
- 2 cosmetic issues fixed
- Documentation enhanced

✅ **53 unit tests = safety net:**
- Instant verification of changes
- No regression fears

### What to Avoid:

❌ **Over-engineering simple components:**
- Don't use Full 3-Phase for utilities
- Tests are sufficient for data structures

❌ **Skipping tests:**
- NEVER acceptable (even for 1-Phase)
- Tests are non-negotiable baseline

❌ **Blind adherence to process:**
- Adapt based on complexity/risk
- Don't cargo cult the methodology

---

## 🎓 SUMMARY: Golden Rules

1. **Always Test** ✅
   - 100% non-negotiable
   - Every component, every time

2. **Risk-Based Quality** ✅
   - HIGH risk → Full 3-Phase or Microscope
   - LOW risk → 1-Phase (tests only)

3. **Time Budget Honestly** ✅
   - Full 3-Phase = 10-12 hours
   - Don't compress artificially

4. **Learn and Adapt** ✅
   - Track actual time vs estimates
   - Refine decision criteria

5. **Foundation = Microscope** ✅
   - Config files, meta-components
   - Extra scrutiny pays off

6. **Prototype Fast, Promote Carefully** ✅
   - 1-Phase for experiments
   - Upgrade to 3-Phase when moving to production

7. **Meta-Components Need Meta-Review** ✅
   - CriticAgent gets Microscope
   - No circular dependency shortcuts

---

## 🎯 READY TO PROCEED?

**Current Status:** Phase 1.2 - ResearchPlanWriterAgent

**Decision:** ✅ **FULL 3-PHASE**

**Estimated Time:** 10-12 hours

**Next Steps:**
1. Začni z implementacijo WriterAgent (skeleton + actions)
2. Napiši 15-20 unit testov
3. Zaženi teste → all green
4. Critic review → score, identify issues
5. Fix HIGH priority issues
6. Re-test → verify
7. ✅ Ready for Phase 1.3 (EvaluatorAgent)

**Ali nadaljujem z WriterAgent implementacijo?**

---

**Document Version:** 1.0  
**Last Updated:** 16. April 2026  
**Status:** ✅ Ready for use
