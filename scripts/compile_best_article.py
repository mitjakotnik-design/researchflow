"""
Compile best-of-breed article from multiple iterations.
Selects the highest-scoring version of each section and creates final article.

Usage:
    python scripts/compile_best_article.py
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import shutil

# Directories
data_dir = Path("data")
checkpoints_dir = data_dir / "checkpoints"
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Best sections identified from analysis
BEST_SECTIONS = {
    'abstract': ('article_20260416_121158', 93, 5),
    'introduction': ('article_20260416_120143', 60, 2),
    'methods': ('article_20260416_120143', 72, 5),
    'results': ('article_20260416_131705', 87, 4),
    'discussion': ('article_20260416_120143', 83, 5),
    'conclusion': ('article_20260416_121954', 82, 5),
}


def load_section_from_checkpoint(article_id: str, section: str) -> Dict:
    """Load a specific section from checkpoint JSON."""
    checkpoint_path = checkpoints_dir / f"{article_id}_section_{section}.json"
    
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return None
    
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract the specific section from the 'sections' dict
    if 'sections' in data and section in data['sections']:
        section_data = data['sections'][section]
        # Add title from parent
        section_data['title'] = data.get('title', '')
        return section_data
    
    return None


def compile_best_article():
    """Compile article from best-scoring sections."""
    
    print("\n" + "="*70)
    print("   🏆 COMPILING BEST-OF-BREED ARTICLE")
    print("="*70 + "\n")
    
    # Load metadata
    print("📊 Loading section data:\n")
    sections_data = {}
    
    for section, (article_id, score, iterations) in BEST_SECTIONS.items():
        print(f"  {section.upper():15} → {article_id}  (score: {score}, iter: {iterations})")
        data = load_section_from_checkpoint(article_id, section)
        
        if data:
            sections_data[section] = data
        else:
            print(f"    ⚠️  Warning: Could not load {section}")
    
    if len(sections_data) != 6:
        print(f"\n❌ Only loaded {len(sections_data)}/6 sections. Aborting.")
        return None
    
    print("\n✅ All sections loaded successfully\n")
    
    # Compile article
    print("📝 Compiling final article...\n")
    
    article_content = []
    
    # Title (from any section, they should all be the same)
    title = sections_data['abstract'].get('title', 'Scoping Review Article')
    article_content.append(f"# {title}\n\n")
    
    # Date and metadata
    article_content.append(f"**Compiled:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    article_content.append(f"**Method:** Best-of-breed compilation\n")
    article_content.append(f"**Quality:** Optimized (highest scoring sections)\n\n")
    article_content.append("---\n\n")
    
    # Add each section
    section_order = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']
    
    total_words = 0
    
    for section in section_order:
        data = sections_data[section]
        article_id, score, iterations = BEST_SECTIONS[section]
        
        # Section header with metadata
        article_content.append(f"## {section.upper()}\n\n")
        article_content.append(f"<!-- Source: {article_id} | Score: {score}/100 | Iterations: {iterations} -->\n\n")
        
        # Section content
        content = data.get('content', '')
        word_count = data.get('word_count', 0)
        total_words += word_count
        
        if content:
            article_content.append(content)
            article_content.append("\n\n")
            print(f"    ✅ {section.title():15} {word_count:5} words")
        else:
            article_content.append("*[Section content not found]*\n\n")
            print(f"    ⚠️  {section.title():15} MISSING")
    
    # Compile statistics
    total_score = sum(score for _, score, _ in BEST_SECTIONS.values())
    avg_score = total_score / len(BEST_SECTIONS)
    
    article_content.append("---\n\n")
    article_content.append("## Compilation Statistics\n\n")
    article_content.append(f"- **Total sections:** {len(BEST_SECTIONS)}\n")
    article_content.append(f"- **Total words:** {total_words:,}\n")
    article_content.append(f"- **Average score:** {avg_score:.1f}/100\n")
    article_content.append(f"- **Total iterations:** {sum(iter for _, _, iter in BEST_SECTIONS.values())}\n")
    article_content.append(f"- **Compilation method:** Best-of-breed (highest score per section)\n\n")
    
    article_content.append("### Section Sources\n\n")
    article_content.append("| Section | Source Article | Score | Iterations |\n")
    article_content.append("|---------|----------------|-------|------------|\n")
    for section, (article_id, score, iterations) in BEST_SECTIONS.items():
        article_content.append(f"| {section.title()} | {article_id} | {score}/100 | {iterations} |\n")
    
    # Save compiled article
    output_path = output_dir / "article_best_of_breed.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(article_content))
    
    print(f"✅ Article compiled successfully!\n")
    print(f"📄 Output: {output_path}")
    print(f"📊 Average quality score: {avg_score:.1f}/100\n")
    
    # Create stats JSON
    stats = {
        "title": title,
        "compiled_at": datetime.now().isoformat(),
        "method": "best-of-breed",
        "total_sections": len(BEST_SECTIONS),
        "average_score": avg_score,
        "sections": {
            section: {
                "source": article_id,
                "score": score,
                "iterations": iterations
            }
            for section, (article_id, score, iterations) in BEST_SECTIONS.items()
        }
    }
    
    stats_path = output_dir / "article_best_of_breed_stats.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"📈 Stats saved: {stats_path}\n")
    
    return output_path, stats


def main():
    """Main execution."""
    result = compile_best_article()
    
    if result:
        article_path, stats = result
        
        print("="*70)
        print("   🎉 COMPILATION COMPLETE")
        print("="*70)
        print(f"\n📄 Article: {article_path}")
        print(f"📊 Average Score: {stats['average_score']:.1f}/100")
        print(f"🎯 Next steps:")
        print(f"   1. Review article: {article_path}")
        print(f"   2. Generate visualizations: python scripts/create_modern_visualizations.py")
        print(f"   3. Export to PDF: python scripts/export_article_with_figures.py")
        print()


if __name__ == "__main__":
    main()
