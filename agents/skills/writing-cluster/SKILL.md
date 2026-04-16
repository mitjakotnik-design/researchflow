---
name: "writing-cluster"
description: |
  Writing cluster za scoping review: pisanje sekcij, sinteza literature,
  akademsko urejanje, terminologija, citiranje, vizualizacije.
  Trigger: pisanje, write, sekcija, section, sinteza, synthesis, uredi,
  edit, terminologija, citiranje, citation, graf, diagram, PRISMA.
argument-hint: "Katero sekcijo ali nalogo pisanja potrebuješ?"
user-invocable: true
applyTo: "agents/**"
tools:
  - read_file
  - create_file
  - replace_string_in_file
  - semantic_search
model: gemini-2.5-pro
---

# Writing Cluster

Entry point za vse agente za pisanje v ResearchFlow sistemu.

## Pregled

Writing cluster vsebuje 6 specializiranih agentov za fazo pisanja:

| Agent | Python razred | Namen |
|-------|---------------|-------|
| **Writer** | `WriterAgent` | Pisanje sekcij članka |
| **Synthesizer** | `SynthesizerAgent` | Narativna sinteza literature |
| **Academic Editor** | `AcademicEditorAgent` | Akademsko urejanje |
| **Terminology Guardian** | `TerminologyGuardianAgent` | Konsistentna terminologija |
| **Citation Manager** | `CitationManagerAgent` | Citiranje in reference |
| **Visualizer** | `VisualizerAgent` | Grafi, diagrami, EGM |

## Routing

| Uporabnikova potreba | Agent | Akcija | Naloži |
|---------------------|-------|--------|--------|
| "Napiši sekcijo X" | writer | `write_section` | [writer/SKILL.md](writer/SKILL.md) |
| "Sintetiziraj ugotovitve" | synthesizer | `synthesize` | [synthesizer/SKILL.md](synthesizer/SKILL.md) |
| "Uredi tekst" | academic_editor | `edit` | [academic-editor/SKILL.md](academic-editor/SKILL.md) |
| "Preveri terminologijo" | terminology_guardian | `check` | [terminology-guardian/SKILL.md](terminology-guardian/SKILL.md) |
| "Formatiraj citate" | citation_manager | `format` | [citation-manager/SKILL.md](citation-manager/SKILL.md) |
| "Generiraj diagram" | visualizer | `generate` | [visualizer/SKILL.md](visualizer/SKILL.md) |

## Sekcije članka

PRISMA-ScR struktura:

| Sekcija | Writer | Min besed | Max besed |
|---------|--------|-----------|-----------|
| Title | ✓ | - | 20 |
| Abstract | ✓ | 250 | 300 |
| Introduction | ✓ | 800 | 1200 |
| Methods | ✓ | 1500 | 2500 |
| Results | ✓ + Synthesizer | 2000 | 4000 |
| Discussion | ✓ | 1500 | 2500 |
| Conclusion | ✓ | 300 | 500 |
| References | Citation Manager | - | - |

## Workflow

```
1. [Researcher] → research context
       ↓
2. [Writer] → initial draft
       ↓
3. [Synthesizer] → enhance Results with narrative synthesis
       ↓
4. [Academic Editor] → language, flow, coherence
       ↓
5. [Terminology Guardian] → consistent terminology
       ↓
6. [Citation Manager] → format references
       ↓
7. [Visualizer] → PRISMA diagram, EGM, charts
```

## Saturation Loop

Writing podpira iterativno izboljševanje:

```python
while not quality_threshold_met:
    draft = await writer.execute(action="write_section", ...)
    
    # Quality checks (parallel)
    evaluations = await asyncio.gather(
        evaluator.execute(action="evaluate", text=draft),
        fact_checker.execute(action="check", text=draft),
        consistency_checker.execute(action="check", text=draft)
    )
    
    if all_pass(evaluations):
        break
    
    feedback = compile_feedback(evaluations)
    draft = await writer.execute(action="revise_section", feedback=feedback)
```

## Quality Gates

| Gate | Minimum | Blokira če |
|------|---------|-----------|
| Word count | 90% of min | <80% |
| Readability (Flesch) | 30-50 | <20 ali >60 |
| Citation density | 2-3/paragraph | <1/paragraph |
| Terminology consistency | 100% | <90% |

## Error Handling

| Error | Handling |
|-------|----------|
| Word count too low | Request expansion |
| Missing citations | Flag, request researcher |
| Tone inconsistency | Auto-correct, verify |
| Terminology mismatch | Apply glossary corrections |

## Konfiguracija

```python
WRITING_AGENTS = {
    "writer": {
        "model": "gemini-2.5-pro",
        "temperature": 0.4,      # Kreativnost z doslednostjo
        "max_tokens": 16384
    },
    "academic_editor": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2       # Nizka za konzervativno urejanje
    }
}
```

## Integracija z obstoječimi skills

| Generični skill | Uporaba |
|-----------------|---------|
| `.github/skills/review-article/` | PRISMA-ScR struktura |
| `.github/skills/academic-citation/` | APA 7, Vancouver formati |
| `.github/skills/scientific-writing-workflow/` | Faze pisanja |

---

**Verzija:** 2.0.0 | **Zadnja posodobitev:** 2026-04-16
