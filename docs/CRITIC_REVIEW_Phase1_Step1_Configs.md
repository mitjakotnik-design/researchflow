# 🔬 KRITIČNA ANALIZA: Config Files (Korak 1.1)

**Datum:** 16. April 2026  
**Kritik:** ResearchFlow Code Critic  
**Namen:** Mikroskopski pregled config datotek

---

## 📊 PREGLED IZVEDENIH DATOTEK

### Datoteke Kreirane:
1. `config/research_plan_sections.py` ✅ (426 vrstic)
2. `config/research_plan_evaluation.py` ✅ (459 vrstic)

### Testiranje:
- ✅ Test 1: research_plan_sections.py izveden uspešno
- ✅ Test 2: research_plan_evaluation.py izveden uspešno
- ✅ Izhodni log: Brez napak

---

## ✅ POZITIVNI VIDIKI

### 1. **Struktura in Arhitektura** (9/10)
**Odlično:**
- ✅ Uporablja dataclasses (Python best practice)
- ✅ Jasna separacija concerns (sections vs evaluation)
- ✅ Type hints povsod (excellent for maintainability)
- ✅ Enum za personas in verdicts (type-safe)
- ✅ Dependency tracking med sekcijami

**Primer odličnosti:**
```python
@dataclass
class ResearchPlanSection:
    section_id: str
    name: str
    min_words: int
    max_words: int
    depends_on: List[str] = field(default_factory=list)
```
→ Clean, explicit, testable

### 2. **Dokumentacija** (10/10)
**Izvrstno:**
- ✅ Comprehensive docstrings
- ✅ Module-level documentation
- ✅ Inline comments za kompleksne dele
- ✅ Reference na source documents (CRITICAL_ANALYSIS)
- ✅ `__main__` blok z testnimi outputi

### 3. **Validacija &Helper Functions** (9/10)
**Zelo dobro:**
- ✅ `validate_word_count()` - simple but effective
- ✅ `check_required_elements()` - keyword-based check
- ✅ `validate_evaluation()` - ensures completeness
- ✅ `get_verdict()` - clear threshold logic
- ✅ Dependency validation funkcija

### 4. **Alignment z Zahtevami** (10/10)
**Perfektno:**
- ✅ **15 sekcij** - vse iz critical analysis
- ✅ **Option A criteria** - Clarity, Feasibility, Rigor, Contribution
- ✅ **4 personas** - Methodology Expert (40%), Supervisor (30%), Domain (20%), Ethics (10%)
- ✅ **Score thresholds** - 85+ approved, 75-84 minor revision
- ✅ Dependencies mapped correctly

---

## ⚠️ POMANJKLJIVOSTI & IZBOLJŠAVE

### 1. **Word Count Validation - Preveč Simplističen** (Severity: MEDIUM)

**Problem:**
```python
def validate_word_count(content: str, section_id: str) -> tuple[bool, str]:
    word_count = len(content.split())  # ← TOO SIMPLE
```

**Težava:**
- Šteje markdown syntax kot besede (`##`, `**`, `- `)
- Ne ignorira code blocks (ki naj ne štejejo)
- Ne ignorira references/citations

**Primer:**
```markdown
## Section Title  ← counts as 2 words
**Bold text** here  ← counts as 3 words instead of 2
```python  ← counts as 1 word
code here  ← counts as 2 words (should be excluded?)
```

**Predlagana rešitev:**
```python
import re

def validate_word_count(content: str, section_id: str) -> tuple[bool, str]:
    """Validate word count, excluding markdown syntax and code blocks."""
    spec = get_section_spec(section_id)
    
    # Remove code blocks
    content_clean = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # Remove inline code
    content_clean = re.sub(r'`[^`]+`', '', content_clean)
    
    # Remove markdown headers (#, ##, ###)
    content_clean = re.sub(r'^#+\s+', '', content_clean, flags=re.MULTILINE)
    
    # Remove markdown formatting (**, __, *, _)
    content_clean = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', content_clean)
    
    # Remove links [text](url)
    content_clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content_clean)
    
    # Count words
    words = content_clean.split()
    word_count = len([w for w in words if w.strip()])
    
    if word_count < spec.min_words:
        return False, f"Too short: {word_count} words (min: {spec.min_words})"
    elif word_count > spec.max_words:
        return False, f"Too long: {word_count} words (max: {spec.max_words})"
    else:
        return True, f"Word count OK: {word_count} words"
```

**Prioriteta:** HIGH (bo vplival na vse evalvacije)

---

### 2. **Required Elements Check - Naivna Implementacija** (Severity: MEDIUM)

**Problem:**
```python
def check_required_elements(content: str, section_id: str) -> tuple[bool, List[str]]:
    content_lower = content.lower()
    for element in spec.required_elements:
        element_keywords = element.replace("_", " ").split()
        if not any(keyword in content_lower for keyword in element_keywords):
            missing.append(element)
```

**Težave:**
1. **False positives:** "research question" bo najden tudi v "research questions are..."
2. **False negatives:** "RQ" ali "research goal" ne bo zaznan kot "research_question"
3. **No semantic understanding:** Ne razume če je element prisoten ampak s sinonimi
4. **No structure awareness:** Ne ve ali je element v pravem delu dokumenta

**Primer napake:**
```markdown
## Methodology
We will NOT use qualitative methods...  ← "qualitative" found, but negated!
```

**Predlagana rešitev (faza 1 - basic improvement):**
```python
def check_required_elements(content: str, section_id: str) -> tuple[bool, List[str]]:
    """Check required elements with improved pattern matching."""
    spec = get_section_spec(section_id)
    missing = []
    
    # Define synonyms/variations for common elements
    ELEMENT_PATTERNS = {
        "main_research_question": [
            r"main\s+research\s+question",
            r"primary\s+research\s+question",
            r"overarching\s+question",
            r"RQ:",
            r"main\s+RQ"
        ],
        "sub_questions": [
            r"sub[- ]questions?",
            r"secondary\s+questions?",
            r"RQ\d+:",
            r"sub[- ]RQ"
        ],
        "pcc_framework": [
            r"PCC\s+framework",
            r"Population.*?Concept.*?Context",
            r"P\.C\.C\.",
            r"PCC\s+\("
        ],
        # Add more patterns for other elements...
    }
    
    content_lower = content.lower()
    
    for element in spec.required_elements:
        found = False
        
        # Try custom patterns first
        if element in ELEMENT_PATTERNS:
            for pattern in ELEMENT_PATTERNS[element]:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    found = True
                    break
        else:
            # Fallback to simple keyword check
            element_keywords = element.replace("_", " ").split()
            if any(keyword in content_lower for keyword in element_keywords):
                found = True
        
        if not found:
            missing.append(element)
    
    return len(missing) == 0, missing
```

**Dolgoročna rešitev (faza 2 - z NLP):**
- Uporabiti Gemini embedding za semantic similarity
- Check če section vsebuje semantično podoben content kot required element
- Threshold: cosine similarity > 0.7

**Prioriteta:** MEDIUM (lahko počaka do faze 2, basic version zadošča za MVP)

---

### 3. **Manjka Error Handling** (Severity: LOW-MEDIUM)

**Problem:**
Nobena funkcija nima try-except blokov. Če pride do napake (npr., invalid section_id), program crashne.

**Primeri ranljivosti:**
```python
def get_section_spec(section_id: str) -> ResearchPlanSection:
    if section_id not in RESEARCH_PLAN_SECTIONS:
        raise ValueError(f"Unknown section: {section_id}")  # ← OK, ampak...
    return RESEARCH_PLAN_SECTIONS[section_id]
```

Kaj če:
- `section_id = None`?
- `section_id = ""`?
- `section_id = 123` (not string)?

**Predlagana rešitev:**
```python
def get_section_spec(section_id: str) -> ResearchPlanSection:
    """Get section specification by ID with validation."""
    if not isinstance(section_id, str):
        raise TypeError(f"section_id must be str, got {type(section_id).__name__}")
    
    if not section_id or not section_id.strip():
        raise ValueError("section_id cannot be empty")
    
    section_id = section_id.strip().lower()
    
    if section_id not in RESEARCH_PLAN_SECTIONS:
        valid_ids = ", ".join(RESEARCH_PLAN_SECTIONS.keys())
        raise ValueError(
            f"Unknown section: '{section_id}'. "
            f"Valid sections: {valid_ids}"
        )
    
    return RESEARCH_PLAN_SECTIONS[section_id]
```

**Prioriteta:** MEDIUM (pomembno za robustnost)

---

### 4. **Subcriteria Scores - Manjka Validacija** (Severity: MEDIUM)

**Problem:**
V `research_plan_evaluation.py` ni validacije da:
- Subscore ≤ max_score za subkriterij
- Sum(subscores) = criterion max_score

**Primer možne napake:**
```python
evaluation = {
    "clarity": {
        "research_questions": 10,  # MAX IS 8! ← Should error
        "objectives": 6,
        "structure": 6,
        "language": 5
    }
}
# Total = 27, but max_score for clarity = 25!
```

**Predlagana rešitev:**
```python
def validate_evaluation(evaluation: Dict) -> tuple[bool, List[str]]:
    """Validate evaluation scores with range checking."""
    errors = []
    
    for criterion_id, criterion_scores in evaluation.items():
        if criterion_id not in EVALUATION_CRITERIA:
            errors.append(f"Unknown criterion: {criterion_id}")
            continue
        
        criterion = EVALUATION_CRITERIA[criterion_id]
        criterion_total = 0
        
        for subcriterion_id, score in criterion_scores.items():
            if subcriterion_id not in criterion.subcriteria:
                errors.append(
                    f"Unknown subcriterion: {criterion_id}.{subcriterion_id}"
                )
                continue
            
            # Validate score range
            max_score = criterion.subcriteria[subcriterion_id].max_score
            if not isinstance(score, (int, float)):
                errors.append(
                    f"{criterion_id}.{subcriterion_id}: "
                    f"Score must be numeric, got {type(score).__name__}"
                )
            elif score < 0:
                errors.append(
                    f"{criterion_id}.{subcriterion_id}: "
                    f"Score cannot be negative ({score})"
                )
            elif score > max_score:
                errors.append(
                    f"{criterion_id}.{subcriterion_id}: "
                    f"Score {score} exceeds max {max_score}"
                )
            
            criterion_total += score
        
        # Check criterion total
        if abs(criterion_total - criterion.max_score) > 0.01:  # Allow rounding
            errors.append(
                f"{criterion_id}: Total {criterion_total} != "
                f"max score {criterion.max_score}"
            )
    
    return len(errors) == 0, errors
```

**Prioriteta:** HIGH (preveni invalid evaluations)

---

### 5. **Manjka Logging** (Severity: LOW)

**Problem:**
Ni structured logging. Težko debug-ati v produkciji.

**Predlagana izboljšava:**
```python
import structlog

logger = structlog.get_logger()

def validate_word_count(content: str, section_id: str) -> tuple[bool, str]:
    """Validate word count against section requirements."""
    spec = get_section_spec(section_id)
    word_count = len(content.split())
    
    logger.info(
        "word_count_validation",
        section_id=section_id,
        word_count=word_count,
        min_required=spec.min_words,
        max_allowed=spec.max_words
    )
    
    if word_count < spec.min_words:
        logger.warning(
            "word_count_too_low",
            section_id=section_id,
            word_count=word_count,
            deficit=spec.min_words - word_count
        )
        return False, f"Too short: {word_count} words (min: {spec.min_words})"
    # ...
```

**Prioriteta:** LOW (nice to have, ne kritično za MVP)

---

### 6. **Missing Unit Tests** (Severity: HIGH)

**Problem:**
Ni unit testov! Samo `__main__` block ki printa output.

**Potrebno:**
```python
# tests/config/test_research_plan_sections.py

import pytest
from config.research_plan_sections import (
    get_section_spec,
    validate_word_count,
    check_required_elements,
    validate_section_order,
    SECTION_ORDER
)

class TestSectionSpecs:
    """Tests for section specifications."""
    
    def test_all_sections_have_required_fields(self):
        """All sections must have name, min/max words, etc."""
        for section_id in SECTION_ORDER:
            spec = get_section_spec(section_id)
            assert spec.section_id == section_id
            assert spec.name
            assert spec.min_words > 0
            assert spec.max_words > spec.min_words
            assert spec.target_score >= 75
    
    def test_get_section_spec_invalid_id(self):
        """Should raise ValueError for unknown section."""
        with pytest.raises(ValueError, match="Unknown section"):
            get_section_spec("nonexistent_section")
    
    def test_validate_word_count_within_range(self):
        """Content within word count range should pass."""
        content = " ".join(["word"] * 150)  # 150 words
        valid, msg = validate_word_count(content, "metadata")
        assert valid
        assert "OK" in msg
    
    def test_validate_word_count_too_short(self):
        """Content below min words should fail."""
        content = "Short content"  # 2 words
        valid, msg = validate_word_count(content, "metadata")
        assert not valid
        assert "Too short" in msg
    
    def test_validate_word_count_too_long(self):
        """Content above max words should fail."""
        content = " ".join(["word"] * 1000)  # 1000 words
        valid, msg = validate_word_count(content, "metadata")
        assert not valid
        assert "Too long" in msg
    
    def test_section_dependencies(self):
        """Dependency validation should work correctly."""
        # Can do metadata first (no dependencies)
        assert validate_section_order([], "metadata")
        
        # Cannot do methodology before research_question
        assert not validate_section_order([], "methodology")
        
        # Can do methodology after dependencies met
        assert validate_section_order(
            ["research_question", "theoretical_framework"],
            "methodology"
        )

# tests/config/test_research_plan_evaluation.py

import pytest
from config.research_plan_evaluation import (
    get_verdict,
    calculate_weighted_score,
    validate_evaluation,
    QualityVerdict,
    EVALUATION_CRITERIA
)

class TestEvaluationCriteria:
    """Tests for evaluation criteria."""
    
    def test_total_score_is_100(self):
        """Sum of all criterion max scores should be 100."""
        total = sum(c.max_score for c in EVALUATION_CRITERIA.values())
        assert total == 100
    
    def test_weights_sum_to_1(self):
        """Weights should sum to 1.0."""
        total_weight = sum(c.weight for c in EVALUATION_CRITERIA.values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_get_verdict_thresholds(self):
        """Verdict determination should match thresholds."""
        assert get_verdict(95) == QualityVerdict.EXCELLENT
        assert get_verdict(85) == QualityVerdict.APPROVED
        assert get_verdict(75) == QualityVerdict.MINOR_REVISION
        assert get_verdict(65) == QualityVerdict.MAJOR_REVISION
        assert get_verdict(50) == QualityVerdict.SUBSTANTIAL_REWORK
    
    def test_calculate_weighted_score(self):
        """Weighted score calculation should be correct."""
        scores = {
            "clarity": 25,
            "feasibility": 25,
            "rigor": 30,
            "contribution": 20
        }
        total = calculate_weighted_score(scores)
        assert total == 100
    
    def test_validate_evaluation_complete(self):
        """Complete evaluation should pass validation."""
        evaluation = {
            "clarity": {
                "research_questions": 8,
                "objectives": 6,
                "structure": 6,
                "language": 5
            },
            "feasibility": {
                "timeline": 7,
                "resources_budget": 7,
                "team_qualifications": 6,
                "scope": 3,
                "risk_mitigation": 2
            },
            "rigor": {
                "methodology": 9,
                "search_strategy": 8,
                "eligibility_criteria": 5,
                "quality_assessment": 5,
                "ethics_data_mgmt": 3
            },
            "contribution": {
                "novelty": 7,
                "significance": 6,
                "implications_impact": 5,
                "dissemination": 2
            }
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid
        assert len(errors) == 0
    
    def test_validate_evaluation_missing_criterion(self):
        """Missing criterion should fail validation."""
        evaluation = {
            "clarity": {"research_questions": 8}
            # Missing feasibility, rigor, contribution
        }
        valid, errors = validate_evaluation(evaluation)
        assert not valid
        assert len(errors) > 0
```

**Prioriteta:** **CRITICAL** (brez testov = ne production-ready)

---

### 7. **Code Documentation - Manjkajo Primeri Uporabe** (Severity: LOW)

**Problem:**
Docstringi nimajo Examples sekcij.

**Izboljšava:**
```python
def validate_word_count(content: str, section_id: str) -> tuple[bool, str]:
    """
    Validate word count against section requirements.
    
    Args:
        content: Text content to validate
        section_id: ID of the section (e.g., "metadata", "research_question")
    
    Returns:
        Tuple of (valid: bool, message: str)
    
    Raises:
        ValueError: If section_id is unknown
    
    Examples:
        >>> content = "This is a sample research plan section with sufficient words."
        >>> valid, msg = validate_word_count(content, "metadata")
        >>> print(valid)
        True
        
        >>> short_content = "Too short"
        >>> valid, msg = validate_word_count(short_content, "research_question")
        >>> print(valid)
        False
    """
    # ...
```

**Prioriteta:** LOW (nice to have)

---

## 📊 SKUPNA OCENA: 8.2/10

### Razčlenitev:
| Kategorija | Ocena | Utež | Točke |
|------------|-------|------|-------|
| Arhitektura & Design | 9/10 | 25% | 2.25 |
| Dokumentacija | 10/10 | 15% | 1.50 |
| Funkcionalnost | 9/10 | 25% | 2.25 |
| Robustnost (error handling) | 6/10 | 15% | 0.90 |
| Testiranje | 3/10 | 15% | 0.45 |
| Code Quality | 9/10 | 5% | 0.45 |
| **SKUPAJ** | | **100%** | **8.2** |

### Interpretacija:
- **8-9 = Excellent** ← Mi smo tukaj!
- 7-8 = Very Good
- 6-7 = Good
- 5-6 = Acceptable
- <5 = Needs Major Rework

---

## 🎯 PRIORITETNA LISTA IZBOLJŠAV

### HIGH Priority (implementirati TAKOJ):
1. ✅ **Unit Tests** - 12 testov (sections + evaluation)
2. ⚠️ **Validation Enhancement** - Score range checking
3. ⚠️ **Word Count Fix** - Exclude markdown syntax

### MEDIUM Priority (implementirati v Phase 2):
4. ⚠️ **Required Elements** - Pattern matching improvements
5. ⚠️ **Error Handling** - Robustna input validation
6. ℹ️ **Logging** - Structured logs

### LOW Priority (lahko počaka):
7. ℹ️ **Documentation Examples** - Docstring examples
8. ℹ️ **Type Checking** - Add mypy support

---

## ✅ POTRDITEV ZA NADALJEVANJE

**Status:** ☑️ **POGOJNO ODOBRENO**

**Pred Phase 1.2 (Agents):**
1. ⚠️ Implementirati HIGH priority fixes (tests, validation, word count)
2. ✅ Run pytest → vse testi morajo biti zeleni
3. ✅ Code review izboljšav

**Po tem lahko nadaljujemo z:**
- Phase 1.2: ResearchPlanWriterAgent
- Phase 1.3: ResearchPlanEvaluatorAgent

---

**Kritik zaključil analizo: ⏰ {timestamp}**
**Naslednji korak: Implementacija izboljšav**

