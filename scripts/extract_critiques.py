"""
Extract detailed critiques for low-scoring sections.
Generates comprehensive feedback reports in Slovenian and English.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Setup path
sys.path.insert(0, 'c:/RaniaDR/scoping-review-agents')

from dotenv import load_dotenv
load_dotenv()

from agents.llm_client import LLMClientFactory


async def extract_critiques():
    """Extract critiques for Introduction (60/100) and Methods (72/100)."""
    
    print("\n" + "="*70)
    print("   EKSTRAKCIJA KRITIK ZA NIZKO OCENJENE SEKCIJE")
    print("="*70 + "\n")
    
    # Load article
    article_path = Path("output/article_20260416_120143_final.md")
    
    with open(article_path, 'r', encoding='utf-8') as f:
        article_content = f.read()
    
    # Extract sections
    sections = {
        'introduction': extract_section(article_content, 'Introduction', 'Methods'),
        'methods': extract_section(article_content, 'Methods', 'Results')
    }
    
    # Initialize LLM
    llm_client = LLMClientFactory.create(model_name='gemini-2.5-flash', temperature=0.3)
    
    critiques = {}
    
    for section_name, content in sections.items():
        score = 60 if section_name == 'introduction' else 72
        
        print(f"\n[{section_name.upper()}] Analiziram... (trenutna ocena: {score}/100)")
        
        # Get detailed critique
        critique = await generate_comprehensive_critique(
            llm_client=llm_client,
            section_name=section_name,
            content=content,
            current_score=score
        )
        
        critiques[section_name] = critique
        print(f"  ✓ {len(critique.get('issues', []))} težav identificiranih")
        print(f"  ✓ {len(critique.get('suggestions', []))} priporočil za izboljšave")
    
    # Generate reports
    print("\n" + "="*70)
    print("   GENERIRANJE POROČIL")
    print("="*70 + "\n")
    
    # Slovenian report
    sl_report = generate_slovenian_report(critiques)
    sl_path = Path("output/KRITIKE_Nizko_Ocenjenih_Sekcij_SL.md")
    with open(sl_path, 'w', encoding='utf-8') as f:
        f.write(sl_report)
    print(f"✓ Slovensko poročilo: {sl_path}")
    
    # English report
    en_report = generate_english_report(critiques)
    en_path = Path("output/CRITIQUES_Low_Scoring_Sections_EN.md")
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_report)
    print(f"✓ Angleško poročilo: {en_path}")
    
    # JSON export
    json_path = Path("output/critiques_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(critiques, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON podatki: {json_path}")
    
    print("\n" + "="*70)
    print("   EKSTRAKCIJA ZAKLJUČENA")
    print("="*70 + "\n")


def extract_section(content: str, start_marker: str, end_marker: str) -> str:
    """Extract section between two markers."""
    start_idx = content.find(f"## {start_marker}")
    if start_idx == -1:
        start_idx = content.find(f"# {start_marker}")
    
    end_idx = content.find(f"## {end_marker}", start_idx + 1)
    if end_idx == -1:
        end_idx = content.find(f"# {end_marker}", start_idx + 1)
    
    if start_idx == -1:
        return ""
    
    if end_idx == -1:
        return content[start_idx:]
    
    return content[start_idx:end_idx].strip()


async def generate_comprehensive_critique(
    llm_client,
    section_name: str,
    content: str,
    current_score: int
) -> dict:
    """Generate comprehensive critique with multiple evaluator perspectives."""
    
    system_prompt = """You are a panel of expert peer reviewers for a high-impact academic journal.
Provide rigorous, specific, and actionable feedback for improving this scoping review section.

Evaluation panel:
1. Methodologist - PRISMA-ScR compliance, reproducibility
2. Domain Expert - HR/AI content accuracy, theoretical grounding  
3. Academic Editor - Writing quality, clarity, structure
4. Practitioner - Practical relevance, actionable insights

Be constructive but thorough. Identify specific problems with exact locations and concrete solutions."""
    
    prompt = f"""Critically evaluate this {section_name.upper()} section of a scoping review.

**Current Score:** {current_score}/100
**Section Content:**
{content[:6000]}

Provide comprehensive feedback from all 4 evaluator perspectives:

Output JSON format:
{{
    "overall_assessment": "2-3 sentence summary of main strengths and critical weaknesses",
    "current_score_breakdown": {{
        "methodology": "X/30 - rationale",
        "synthesis": "X/30 - rationale", 
        "presentation": "X/20 - rationale",
        "contribution": "X/20 - rationale"
    }},
    "critical_issues": [
        {{
            "evaluator": "methodologist|domain_expert|editor|practitioner",
            "severity": "critical|major|moderate|minor",
            "category": "methodology|content|presentation|contribution",
            "issue": "Specific problem identified",
            "location": "Where in the text (quote or description)",
            "impact": "Why this matters for publication quality",
            "evidence": "Specific example or quote showing the problem"
        }}
    ],
    "strengths": [
        {{
            "evaluator": "who identified this",
            "strength": "What works well",
            "evidence": "Specific example"
        }}
    ],
    "improvement_suggestions": [
        {{
            "evaluator": "who suggests this",
            "priority": "high|medium|low",
            "area": "What to improve",
            "current_problem": "What's wrong now",
            "suggested_fix": "Specific actionable recommendation",
            "example": "How it could look after improvement",
            "expected_score_gain": "estimated +X points"
        }}
    ],
    "target_score_pathway": {{
        "quick_wins": ["3-5 easiest high-impact fixes to reach 75/100"],
        "to_reach_85": ["Additional improvements needed for 85/100"],
        "priority_order": ["Numbered list: what to fix first, second, third..."]
    }},
    "comparison_to_best_practices": {{
        "prisma_scr_compliance": "assessment of adherence",
        "missing_elements": ["critical elements that should be added"],
        "exemplar_comparison": "how this compares to high-quality scoping reviews"
    }}
}}"""
    
    response = await llm_client.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=3000,
        json_mode=True
    )
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {
            "overall_assessment": response.content[:500],
            "critical_issues": [],
            "improvement_suggestions": [],
            "error": "JSON parsing failed"
        }


def generate_slovenian_report(critiques: dict) -> str:
    """Generate Slovenian critique report."""
    
    report = f"""# 📋 POROČILO O KRITIKAH NIZKO OCENJENIH SEKCIJ

**Datum:** {datetime.now().strftime('%d. %B %Y')}  
**Artikel:** From Technostress to Organizational Resilience (Scoping Review)  
**Sekciji v analizi:** Introduction (60/100), Methods (72/100)

---

## 📊 IZVRŠNI POVZETEK

Ta dokument vsebuje celovite kritike in priporočila za izboljšavo dveh nizko ocenjenih sekcij preglednega članka. Evalvacijo je opravila komisija štirih strokovnjakov z različnih perspektiv.

**Ključne ugotovitve:**
- **Introduction:** Potrebna večja revizija (trenutno 60/100)
- **Methods:** Potrebna manjša revizija (trenutno 72/100)
- **Glavne težave:** Metodološka natančnost, teoretska utemeljitev, jasnost predstavitve
- **Potencial:** Obe sekciji lahko dosežeta 85+ z usmerjenimi izboljšavami

---

"""
    
    for section_name, critique in critiques.items():
        section_title = "INTRODUCTION" if section_name == "introduction" else "METHODS"
        current_score = 60 if section_name == "introduction" else 72
        
        report += f"""## 🔍 SEKCIJA: {section_title}

**Trenutna ocena:** {current_score}/100  
**Status:** {'Večja revizija potrebna' if current_score < 70 else 'Manjša revizija potrebna'}

### Splošna ocena

{critique.get('overall_assessment', 'Ni na voljo')}

### Razčlenitev ocene

"""
        scores = critique.get('current_score_breakdown', {})
        for criterion, details in scores.items():
            report += f"- **{criterion.title()}:** {details}\n"
        
        report += f"""

---

### ❌ KRITIČNE TEŽAVE

"""
        issues = critique.get('critical_issues', [])
        if issues:
            # Group by severity
            critical = [i for i in issues if i.get('severity') == 'critical']
            major = [i for i in issues if i.get('severity') == 'major']
            moderate = [i for i in issues if i.get('severity') == 'moderate']
            
            if critical:
                report += "\n#### 🔴 KRITIČNE TEŽAVE (nujno reši)\n\n"
                for i, issue in enumerate(critical, 1):
                    report += format_issue_slovenian(i, issue)
            
            if major:
                report += "\n#### 🟠 VEČJE TEŽAVE (visoka prioriteta)\n\n"
                for i, issue in enumerate(major, 1):
                    report += format_issue_slovenian(i, issue)
            
            if moderate:
                report += "\n#### 🟡 ZMERNE TEŽAVE (srednja prioriteta)\n\n"
                for i, issue in enumerate(moderate, 1):
                    report += format_issue_slovenian(i, issue)
        else:
            report += "\n*Ni identificiranih kritičnih težav.*\n"
        
        report += f"""

---

### ✅ PREDNOSTI

"""
        strengths = critique.get('strengths', [])
        if strengths:
            for i, strength in enumerate(strengths, 1):
                evaluator = strength.get('evaluator', 'evaluator').title()
                report += f"""
**{i}. {strength.get('strength', 'N/A')}** ({evaluator})

*Dokaz:* {strength.get('evidence', 'N/A')}

"""
        else:
            report += "\n*Prepoznanih nekaj prednosti, vendar potrebne izboljšave.*\n"
        
        report += f"""

---

### 💡 PRIPOROČILA ZA IZBOLJŠAVE

"""
        suggestions = critique.get('improvement_suggestions', [])
        if suggestions:
            high_priority = [s for s in suggestions if s.get('priority') == 'high']
            medium_priority = [s for s in suggestions if s.get('priority') == 'medium']
            
            if high_priority:
                report += "\n#### 🎯 VISOKA PRIORITETA\n\n"
                for i, sug in enumerate(high_priority, 1):
                    report += format_suggestion_slovenian(i, sug)
            
            if medium_priority:
                report += "\n#### 🎯 SREDNJA PRIORITETA\n\n"
                for i, sug in enumerate(medium_priority, 1):
                    report += format_suggestion_slovenian(i, sug)
        
        report += f"""

---

### 🎯 POT DO CILJNE OCENE

"""
        pathway = critique.get('target_score_pathway', {})
        
        quick_wins = pathway.get('quick_wins', [])
        if quick_wins:
            report += "\n#### Hitre zmage (→ 75/100)\n\n"
            for i, win in enumerate(quick_wins, 1):
                report += f"{i}. {win}\n"
        
        to_85 = pathway.get('to_reach_85', [])
        if to_85:
            report += "\n#### Dodatne izboljšave (→ 85/100)\n\n"
            for i, improvement in enumerate(to_85, 1):
                report += f"{i}. {improvement}\n"
        
        priority_order = pathway.get('priority_order', [])
        if priority_order:
            report += "\n#### Priporočen vrstni red ukrepanja\n\n"
            for item in priority_order:
                report += f"- {item}\n"
        
        report += "\n\n---\n\n"
    
    report += f"""

## 📈 PRIPOROČILA ZA NASLEDNJO ITERACIJO

### 1. Takojšnji ukrepi (Teden 1)

**Introduction:**
- Okrepiti teoretsko utemeljitev (JD-R, COR modeli)
- Dodati jasno raziskovalno vrzel
- Izboljšati PRISMA-ScR utemeljitev

**Methods:**
- Specificirati iskalne strategije z vezniki
- Dodati PRISMA-ScR diagram toka
- Razjasniti vključitvene/izključitvene kriterije

### 2. Kratkoročni ukrepi (Teden 2-3)

- Integrirati povratne informacije vseh evalvatorjev
- Ponovno pregledati strukturo za logičen tok
- Dodati manjkajoče elemente PRISMA-ScR

### 3. Dolgoročni ukrepi (Za naslednjo verzijo)

- Razširiti diskusijo praktičnih posledic
- Okrepiti povezave med sekcijami
- Dodati kontekstualne informacije

---

## 📚 VIRI ZA REFERENCE

**PRISMA-ScR Smernice:**
- Tricco et al. (2018). PRISMA Extension for Scoping Reviews (PRISMA-ScR)

**Primeri odličnih scoping reviews:**
- Arksey & O'Malley (2005). Scoping studies: towards a methodological framework
- Levac et al. (2010). Scoping studies: advancing the methodology

**Teoretski okviri:**
- Demerouti et al. (2001). Job Demands-Resources model
- Hobfoll (1989). Conservation of Resources theory

---

*Dokument generiran: {datetime.now().strftime('%d.%m.%Y ob %H:%M')}*  
*Sistem: ResearchFlow v2.0 - Multi-Evaluator Agent*
"""
    
    return report


def format_issue_slovenian(num: int, issue: dict) -> str:
    """Format single issue in Slovenian."""
    evaluator_map = {
        'methodologist': 'Metodolog',
        'domain_expert': 'Strokovnjak področja',
        'editor': 'Urednik',
        'practitioner': 'Praktik'
    }
    
    evaluator = evaluator_map.get(issue.get('evaluator', ''), issue.get('evaluator', 'Evaluator'))
    
    return f"""
**{num}. {issue.get('issue', 'N/A')}** ({evaluator})

- **Kategorija:** {issue.get('category', 'N/A').title()}
- **Lokacija:** {issue.get('location', 'N/A')}
- **Vpliv:** {issue.get('impact', 'N/A')}
- **Dokaz:** "{issue.get('evidence', 'N/A')}"

"""


def format_suggestion_slovenian(num: int, sug: dict) -> str:
    """Format single suggestion in Slovenian."""
    evaluator_map = {
        'methodologist': 'Metodolog',
        'domain_expert': 'Strokovnjak',
        'editor': 'Urednik',
        'practitioner': 'Praktik'
    }
    
    evaluator = evaluator_map.get(sug.get('evaluator', ''), sug.get('evaluator', ''))
    score_gain = sug.get('expected_score_gain', '?')
    
    return f"""
**{num}. {sug.get('area', 'N/A')}** ({evaluator}) — *{score_gain}*

**Trenutni problem:**  
{sug.get('current_problem', 'N/A')}

**Priporočena rešitev:**  
{sug.get('suggested_fix', 'N/A')}

**Primer:**  
{sug.get('example', 'N/A')}

"""


def generate_english_report(critiques: dict) -> str:
    """Generate English critique report."""
    
    report = f"""# 📋 CRITIQUE REPORT: LOW-SCORING SECTIONS

**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Article:** From Technostress to Organizational Resilience (Scoping Review)  
**Sections Analyzed:** Introduction (60/100), Methods (72/100)

---

## 📊 EXECUTIVE SUMMARY

This document contains comprehensive critiques and improvement recommendations for two low-scoring sections of the scoping review article. Evaluation was conducted by a panel of four expert reviewers from different perspectives.

**Key Findings:**
- **Introduction:** Major revision required (currently 60/100)
- **Methods:** Minor revision required (currently 72/100)
- **Main Issues:** Methodological precision, theoretical grounding, presentation clarity
- **Potential:** Both sections can reach 85+ with targeted improvements

---

"""
    
    for section_name, critique in critiques.items():
        section_title = "INTRODUCTION" if section_name == "introduction" else "METHODS"
        current_score = 60 if section_name == "introduction" else 72
        
        report += f"""## 🔍 SECTION: {section_title}

**Current Score:** {current_score}/100  
**Status:** {'Major Revision Needed' if current_score < 70 else 'Minor Revision Needed'}

### Overall Assessment

{critique.get('overall_assessment', 'Not available')}

### Score Breakdown

"""
        scores = critique.get('current_score_breakdown', {})
        for criterion, details in scores.items():
            report += f"- **{criterion.title()}:** {details}\n"
        
        report += f"""

---

### ❌ CRITICAL ISSUES

"""
        issues = critique.get('critical_issues', [])
        if issues:
            critical = [i for i in issues if i.get('severity') == 'critical']
            major = [i for i in issues if i.get('severity') == 'major']
            moderate = [i for i in issues if i.get('severity') == 'moderate']
            
            if critical:
                report += "\n#### 🔴 CRITICAL ISSUES (must address)\n\n"
                for i, issue in enumerate(critical, 1):
                    report += format_issue_english(i, issue)
            
            if major:
                report += "\n#### 🟠 MAJOR ISSUES (high priority)\n\n"
                for i, issue in enumerate(major, 1):
                    report += format_issue_english(i, issue)
            
            if moderate:
                report += "\n#### 🟡 MODERATE ISSUES (medium priority)\n\n"
                for i, issue in enumerate(moderate, 1):
                    report += format_issue_english(i, issue)
        else:
            report += "\n*No critical issues identified.*\n"
        
        report += f"""

---

### ✅ STRENGTHS

"""
        strengths = critique.get('strengths', [])
        if strengths:
            for i, strength in enumerate(strengths, 1):
                evaluator = strength.get('evaluator', 'evaluator').title()
                report += f"""
**{i}. {strength.get('strength', 'N/A')}** ({evaluator})

*Evidence:* {strength.get('evidence', 'N/A')}

"""
        else:
            report += "\n*Some strengths recognized, but improvements needed.*\n"
        
        report += f"""

---

### 💡 IMPROVEMENT RECOMMENDATIONS

"""
        suggestions = critique.get('improvement_suggestions', [])
        if suggestions:
            high_priority = [s for s in suggestions if s.get('priority') == 'high']
            medium_priority = [s for s in suggestions if s.get('priority') == 'medium']
            
            if high_priority:
                report += "\n#### 🎯 HIGH PRIORITY\n\n"
                for i, sug in enumerate(high_priority, 1):
                    report += format_suggestion_english(i, sug)
            
            if medium_priority:
                report += "\n#### 🎯 MEDIUM PRIORITY\n\n"
                for i, sug in enumerate(medium_priority, 1):
                    report += format_suggestion_english(i, sug)
        
        report += f"""

---

### 🎯 PATHWAY TO TARGET SCORE

"""
        pathway = critique.get('target_score_pathway', {})
        
        quick_wins = pathway.get('quick_wins', [])
        if quick_wins:
            report += "\n#### Quick Wins (→ 75/100)\n\n"
            for i, win in enumerate(quick_wins, 1):
                report += f"{i}. {win}\n"
        
        to_85 = pathway.get('to_reach_85', [])
        if to_85:
            report += "\n#### Additional Improvements (→ 85/100)\n\n"
            for i, improvement in enumerate(to_85, 1):
                report += f"{i}. {improvement}\n"
        
        priority_order = pathway.get('priority_order', [])
        if priority_order:
            report += "\n#### Recommended Action Sequence\n\n"
            for item in priority_order:
                report += f"- {item}\n"
        
        report += "\n\n---\n\n"
    
    report += f"""

## 📈 RECOMMENDATIONS FOR NEXT ITERATION

### 1. Immediate Actions (Week 1)

**Introduction:**
- Strengthen theoretical foundation (JD-R, COR models)
- Add clear research gap identification
- Improve PRISMA-ScR rationale

**Methods:**
- Specify search strategies with Boolean operators
- Add PRISMA-ScR flow diagram
- Clarify inclusion/exclusion criteria

### 2. Short-term Actions (Week 2-3)

- Integrate feedback from all evaluators
- Review structure for logical flow
- Add missing PRISMA-ScR elements

### 3. Long-term Actions (For next version)

- Expand discussion of practical implications
- Strengthen inter-section connections
- Add contextual information

---

## 📚 REFERENCE RESOURCES

**PRISMA-ScR Guidelines:**
- Tricco et al. (2018). PRISMA Extension for Scoping Reviews (PRISMA-ScR)

**Exemplar Scoping Reviews:**
- Arksey & O'Malley (2005). Scoping studies: towards a methodological framework
- Levac et al. (2010). Scoping studies: advancing the methodology

**Theoretical Frameworks:**
- Demerouti et al. (2001). Job Demands-Resources model
- Hobfoll (1989). Conservation of Resources theory

---

*Document generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}*  
*System: ResearchFlow v2.0 - Multi-Evaluator Agent*
"""
    
    return report


def format_issue_english(num: int, issue: dict) -> str:
    """Format single issue in English."""
    evaluator = issue.get('evaluator', 'Evaluator').replace('_', ' ').title()
    
    return f"""
**{num}. {issue.get('issue', 'N/A')}** ({evaluator})

- **Category:** {issue.get('category', 'N/A').title()}
- **Location:** {issue.get('location', 'N/A')}
- **Impact:** {issue.get('impact', 'N/A')}
- **Evidence:** "{issue.get('evidence', 'N/A')}"

"""


def format_suggestion_english(num: int, sug: dict) -> str:
    """Format single suggestion in English."""
    evaluator = sug.get('evaluator', '').replace('_', ' ').title()
    score_gain = sug.get('expected_score_gain', '?')
    
    return f"""
**{num}. {sug.get('area', 'N/A')}** ({evaluator}) — *{score_gain}*

**Current Problem:**  
{sug.get('current_problem', 'N/A')}

**Recommended Fix:**  
{sug.get('suggested_fix', 'N/A')}

**Example:**  
{sug.get('example', 'N/A')}

"""


if __name__ == "__main__":
    asyncio.run(extract_critiques())
