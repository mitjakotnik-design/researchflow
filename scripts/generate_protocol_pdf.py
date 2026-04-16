"""
Generate PDF from Research Protocol markdown file.
Clean, professional academic formatting using WeasyPrint.
"""

from pathlib import Path
import datetime
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


# Academic CSS stylesheet
ACADEMIC_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm 2cm 2cm;
    
    @top-center {
        content: "Research Protocol: AI, HR & Psychosocial Risks";
        font-family: 'Georgia', serif;
        font-size: 9pt;
        color: #666;
    }
    
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Georgia', serif;
        font-size: 9pt;
        color: #999;
    }
}

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #212529;
    text-align: justify;
}

h1 {
    color: #212529;
    font-size: 24pt;
    font-weight: bold;
    margin-top: 0.8cm;
    margin-bottom: 0.5cm;
    page-break-after: avoid;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.3cm;
}

h2 {
    color: #2c3e50;
    font-size: 16pt;
    font-weight: bold;
    margin-top: 0.6cm;
    margin-bottom: 0.4cm;
    page-break-after: avoid;
}

h3 {
    color: #34495e;
    font-size: 13pt;
    font-weight: bold;
    margin-top: 0.4cm;
    margin-bottom: 0.3cm;
    page-break-after: avoid;
}

h4 {
    color: #4a5568;
    font-size: 11pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 0.3cm;
    margin-bottom: 0.2cm;
}

p {
    margin-bottom: 0.4cm;
    orphans: 3;
    widows: 3;
}

ul, ol {
    margin-left: 0.8cm;
    margin-bottom: 0.4cm;
}

li {
    margin-bottom: 0.2cm;
}

code {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    background-color: #f8f9fa;
    padding: 0.1cm 0.2cm;
    border-radius: 3px;
    font-size: 9pt;
}

pre {
    background-color: #f8f9fa;
    border-left: 3px solid #3498db;
    padding: 0.4cm;
    margin: 0.4cm 0;
    overflow-x: auto;
    page-break-inside: avoid;
}

pre code {
    background: none;
    padding: 0;
    font-size: 9pt;
    line-height: 1.4;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5cm 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th {
    background-color: #3498db;
    color: white;
    padding: 0.3cm;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 0.25cm;
    border-bottom: 1px solid #dee2e6;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

strong {
    font-weight: bold;
    color: #2c3e50;
}

em {
    font-style: italic;
}

blockquote {
    border-left: 4px solid #3498db;
    padding-left: 0.5cm;
    margin: 0.5cm 0;
    color: #555;
    font-style: italic;
}

.title-page {
    text-align: center;
    padding-top: 4cm;
    page-break-after: always;
}

.title-page h1 {
    font-size: 28pt;
    margin-bottom: 1cm;
    border: none;
}

.status-box {
    background-color: #e3f2fd;
    border: 2px solid #3498db;
    border-radius: 5px;
    padding: 0.5cm;
    margin: 1cm auto;
    width: 12cm;
    text-align: center;
}

.status-box h3 {
    color: #3498db;
    margin: 0.2cm 0;
    font-size: 12pt;
}

.status-box p {
    margin: 0.1cm 0;
    font-size: 10pt;
    color: #555;
}

hr {
    border: none;
    border-top: 1px solid #dee2e6;
    margin: 0.5cm 0;
}
"""


def markdown_to_pdf(md_path, output_path):
    """Convert markdown file to professional PDF."""
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'extra',  # Tables, fenced code, etc.
        'codehilite',  # Code highlighting
        'toc',  # Table of contents
        'nl2br',  # Newline to <br>
    ])
    
    html_body = md.convert(md_content)
    
    # Create complete HTML document
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Research Protocol</title>
</head>
<body>
    <div class="title-page">
        <h1>Psychosocial Risks and Organizational Culture Implications of Artificial Intelligence Implementation in Organizations through Human Resources</h1>
        <h2 style="color: #666; font-weight: normal;">Scoping Review Protocol</h2>
        <p style="margin-top: 2cm; font-size: 12pt; color: #888;">
            <strong>Version 1.0 - English</strong><br>
            April 2026
        </p>
        <div class="status-box">
            <h3>STATUS: READY FOR PROSPERO REGISTRATION</h3>
            <p><strong>Projected Timeline:</strong> 21 weeks</p>
            <p><strong>Target Impact Factor:</strong> 5.0+</p>
        </div>
        <p style="margin-top: 3cm; font-size: 9pt; color: #999;">
            Generated: {datetime.datetime.now().strftime("%B %d, %Y")}
        </p>
    </div>
    
    <div class="content">
        {html_body}
    </div>
</body>
</html>
"""
    
    # Configure fonts
    font_config = FontConfiguration()
    
    # Generate PDF
    html_doc = HTML(string=html)
    css = CSS(string=ACADEMIC_CSS, font_config=font_config)
    
    html_doc.write_pdf(
        output_path,
        stylesheets=[css],
        font_config=font_config
    )
    
    print(f"\n✅ PDF generated successfully!")
    print(f"📄 Output: {output_path}")
    print(f"📊 File size: {Path(output_path).stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    # Paths
    md_file = Path("c:/RaniaDR/Znanstvena podlaga/RESEARCH_PROTOCOL_Review_EN.md")
    pdf_file = Path("c:/RaniaDR/Znanstvena podlaga/RESEARCH_PROTOCOL_Review_EN.pdf")
    
    print("\n" + "="*70)
    print("   GENERATING RESEARCH PROTOCOL PDF")
    print("="*70 + "\n")
    
    markdown_to_pdf(md_file, pdf_file)
    
    print("\n" + "="*70)
    print("   GENERATION COMPLETE")
    print("="*70 + "\n")

