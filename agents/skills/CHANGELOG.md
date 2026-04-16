# Changelog

All notable changes to ResearchFlow Agent Skills.

## [2.1.0] - 2026-04-16

### Added - Python Integration
- **skill_loader.py**: Core module for loading SKILL.md from Python
  - `SkillLoader` class with caching
  - `get_skill()` convenience function
  - `get_system_prompt()` for agent configuration
  - `list_all_skills()` for discovery
  - Section parsing from markdown body
- **templates/__init__.py**: Template loading package
  - `load_template()` function
  - `list_templates()` for discovery
- **schemas/__init__.py**: JSON Schema validation
  - `validate_data_charting()` function
  - `create_empty_data_charting()` helper
- **scripts/__init__.py**: Python tools integration
  - `calculate_kappa()` quick IRR function
  - `generate_prisma_diagram()` quick generator
- **requirements.txt**: Dependencies for skill tools
- **demo_integration.py**: Full integration demo

### Updated
- **agents/__init__.py**: Added skill_loader exports
- All `__init__.py` files now have proper `__all__` exports
- Added logging to skill_loader

## [2.0.0] - 2026-04-16

### Added
- **3 Cluster entry points**: research-cluster, writing-cluster, quality-cluster
- **17 Agent skills** with full documentation
- **Central configuration** (config.yaml) for all thresholds and model settings
- **Domain-specific content** for AI in HR scoping review
- **Error handling** sections for all agents
- **Quality gates** with specific thresholds
- **Inter-agent communication** protocols
- **Rate limiting** and circuit breaker documentation
- **PRISMA-ScR checklist** integration (22 items)
- **Evidence Gap Map** framework with pre-defined axes
- **Model preferences** in YAML frontmatter
- **Tools restriction** in YAML frontmatter

### Research Cluster
- researcher: RAG queries, synthesis, theme identification
- literature-scout: Boolean search strings for WoS/Scopus/PubMed/PsycINFO
- data-extractor: Structured charting with domain-specific template
- meta-analyst: Descriptive statistics, pattern detection
- gap-identifier: EGM generation, research agenda

### Writing Cluster
- writer: PRISMA-ScR section writing with word count enforcement
- synthesizer: Thematic, framework, realist synthesis methods
- academic-editor: Tone, coherence, readability improvements
- terminology-guardian: Domain glossary, consistency checking
- citation-manager: APA 7, Vancouver formatting, DOI verification
- visualizer: PRISMA diagram, EGM heatmap, publication figures

### Quality Cluster
- multi-evaluator: 5-dimension evaluation (accuracy, coherence, completeness, style, citations)
- fact-checker: Claim verification against RAG and sources
- consistency-checker: Cross-section consistency validation
- bias-auditor: Selection, reporting, language bias detection
- critic: Constructive feedback synthesis with prioritization
- methodology-validator: PRISMA-ScR compliance checking

### Changed
- Upgraded from v1.0 with significant enhancements
- Added `applyTo` pattern matching for all agent skills
- Added `tools` and `model` fields to cluster entry points

### Technical
- Total: 20 SKILL.md files (~105 KB)
- YAML validation: 100% pass
- Python validation script included

## [1.0.0] - 2026-04-16

### Added
- Initial v1 skills (basic structure)
- Research cluster only
- Basic routing and workflow

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to skill interfaces
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, documentation updates
