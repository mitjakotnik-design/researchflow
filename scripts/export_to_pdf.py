"""Export scoping review article to PDF with figures using fpdf2."""

from fpdf import FPDF
from pathlib import Path
import datetime
import re
import textwrap

# Paths
output_dir = Path("output")
figures_dir = output_dir / "figures"
article_path = output_dir / "article_scoping_review.md"


class ScopingReviewPDF(FPDF):
    """Custom PDF class for scoping review articles."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'Scoping Review: HR and AI Workplace Transformation', 0, 0, 'L')
            self.cell(0, 10, str(self.page_no()), 0, 0, 'R')
            self.ln(15)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        if self.page_no() == 1:
            self.cell(0, 10, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')
    
    def chapter_title(self, title, level=1):
        """Add a chapter/section title."""
        if level == 1:  # Main title
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(26, 26, 26)
            self.multi_cell(0, 10, title, align='C')
            self.ln(5)
        elif level == 2:  # Section
            self.set_font('Helvetica', 'B', 13)
            self.set_text_color(44, 62, 80)
            self.ln(5)
            self.multi_cell(0, 8, title)
            self.set_draw_color(189, 195, 199)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
        elif level == 3:  # Subsection
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(52, 73, 94)
            self.ln(3)
            self.multi_cell(0, 7, title)
            self.ln(2)
    
    def body_text(self, text):
        """Add body text paragraph."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        
        # Handle bold and italic in text
        text = self._clean_markdown(text)
        self.multi_cell(0, 5, text, align='J')
        self.ln(3)
    
    def reference_text(self, text):
        """Add reference entry with hanging indent."""
        self.set_font('Helvetica', '', 9)
        self.set_text_color(51, 51, 51)
        
        text = self._clean_markdown(text)
        # Use smaller line height for references
        self.multi_cell(0, 4, text, align='L')
        self.ln(2)
    
    def abstract_box(self, text):
        """Add styled abstract box."""
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(52, 152, 219)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(51, 51, 51)
        
        # Calculate box height
        text = self._clean_markdown(text)
        
        # Draw box
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.5)
        self.rect(12, y, 186, 3, 'F')  # Top border accent
        self.set_fill_color(248, 249, 250)
        
        self.set_x(15)
        self.multi_cell(180, 5, text, align='J')
        self.ln(5)
    
    def keywords_box(self, keywords):
        """Add keywords box."""
        self.set_fill_color(240, 240, 240)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(51, 51, 51)
        self.cell(25, 7, 'Keywords: ', 0, 0)
        self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 7, keywords)
        self.ln(5)
    
    def add_figure(self, image_path, caption, fig_num):
        """Add a figure with caption."""
        if not Path(image_path).exists():
            print(f"  Warning: Image not found: {image_path}")
            return
        
        # Check if we need a new page
        if self.get_y() > 200:
            self.add_page()
        
        self.ln(5)
        
        # Add image centered
        img_width = 180
        x = (210 - img_width) / 2
        self.image(str(image_path), x=x, w=img_width)
        
        # Add caption
        self.ln(3)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(85, 85, 85)
        self.multi_cell(0, 5, f'Figure {fig_num}. {caption}', align='C')
        self.ln(5)
    
    def _clean_markdown(self, text):
        """Remove markdown formatting and handle Unicode."""
        # Remove bold markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # Remove italic markers
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Remove code markers
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Replace Unicode characters with ASCII equivalents
        replacements = {
            '\u2014': '-',    # em dash
            '\u2013': '-',    # en dash
            '\u2018': "'",    # left single quote
            '\u2019': "'",    # right single quote
            '\u201c': '"',    # left double quote
            '\u201d': '"',    # right double quote
            '\u2026': '...',  # ellipsis
            '\u00a0': ' ',    # non-breaking space
            '\u2022': '*',    # bullet
            '\u2032': "'",    # prime
            '\u2033': '"',    # double prime
            '\u00b0': ' degrees',  # degree symbol
            '\u00d7': 'x',    # multiplication sign
            '\u00f7': '/',    # division sign
            '\u2212': '-',    # minus sign
            '\u00b1': '+/-',  # plus-minus
            '\u2248': '~',    # approximately
            '\u2264': '<=',   # less than or equal
            '\u2265': '>=',   # greater than or equal
            '\u00e9': 'e',    # e acute
            '\u00e8': 'e',    # e grave
            '\u00e0': 'a',    # a grave
            '\u00f6': 'o',    # o umlaut
            '\u00fc': 'u',    # u umlaut
            '\u00df': 'ss',   # eszett
        }
        
        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)
        
        # Remove any remaining non-ASCII characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text


def parse_markdown(md_text):
    """Parse markdown into structured sections."""
    sections = []
    current_section = {'type': 'text', 'content': '', 'level': 0}
    
    lines = md_text.split('\n')
    
    for line in lines:
        # Check for headers
        if line.startswith('# '):
            if current_section['content'].strip():
                sections.append(current_section)
            current_section = {'type': 'h1', 'content': line[2:].strip(), 'level': 1}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': '', 'level': 0}
        elif line.startswith('## '):
            if current_section['content'].strip():
                sections.append(current_section)
            current_section = {'type': 'h2', 'content': line[3:].strip(), 'level': 2}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': '', 'level': 0}
        elif line.startswith('### '):
            if current_section['content'].strip():
                sections.append(current_section)
            current_section = {'type': 'h3', 'content': line[4:].strip(), 'level': 3}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': '', 'level': 0}
        elif line.startswith('**Keywords'):
            if current_section['content'].strip():
                sections.append(current_section)
            # Extract keywords
            kw = re.sub(r'\*\*Keywords:\*\*\s*', '', line)
            current_section = {'type': 'keywords', 'content': kw.strip(), 'level': 0}
            sections.append(current_section)
            current_section = {'type': 'text', 'content': '', 'level': 0}
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            # List item
            current_section['content'] += '• ' + line.strip()[2:] + '\n'
        elif line.strip().startswith(tuple(f'{i}.' for i in range(1, 10))):
            # Numbered list
            current_section['content'] += line.strip() + '\n'
        else:
            current_section['content'] += line + '\n'
    
    if current_section['content'].strip():
        sections.append(current_section)
    
    return sections


def main():
    print("\n" + "=" * 60)
    print("EXPORTING TO PDF (fpdf2)")
    print("=" * 60 + "\n")
    
    # Check if article exists
    if not article_path.exists():
        print(f"❌ Article not found at: {article_path}")
        return
    
    # Check figures
    figures = list(figures_dir.glob("*.png"))
    print(f"Found {len(figures)} figures in {figures_dir}")
    
    # Read article
    with open(article_path, "r", encoding="utf-8") as f:
        article_md = f.read()
    
    # Parse markdown
    sections = parse_markdown(article_md)
    
    # Create PDF
    pdf = ScopingReviewPDF()
    pdf.add_page()
    
    # Track sections for figure insertion
    current_section = ""
    abstract_done = False
    in_references = False
    figures_to_insert = [
        {'after': 'Study Selection', 'file': 'figure1_prisma_flow.png', 
         'caption': 'PRISMA-ScR flow diagram showing the study selection process.', 'num': 1, 'done': False},
        {'after': 'Characteristics of Included', 'file': 'figure5_study_characteristics.png', 
         'caption': 'Characteristics of included studies: methodology, geographic distribution, and sector.', 'num': 2, 'done': False},
        {'after': 'Theme 1', 'file': 'figure3_technostress_dimensions.png', 
         'caption': 'Prevalence of technostress dimensions in AI-adopting organizations.', 'num': 3, 'done': False},
        {'after': 'Theme 5', 'file': 'figure4_hr_interventions.png', 
         'caption': 'Effectiveness and evidence quality of HR interventions for technostress mitigation.', 'num': 4, 'done': False},
        {'after': '4. Discussion', 'file': 'figure2_conceptual_model.png', 
         'caption': 'Conceptual model: HR as mediator in AI-driven workplace transformation.', 'num': 5, 'done': False},
    ]
    
    for section in sections:
        if section['type'] == 'h1':
            pdf.chapter_title(section['content'], level=1)
        
        elif section['type'] == 'h2':
            current_section = section['content']
            # Check if entering References section
            if 'References' in section['content']:
                in_references = True
                pdf.add_page()  # Start references on new page
            pdf.chapter_title(section['content'], level=2)
            
            # Check for figure insertion after h2
            for fig in figures_to_insert:
                if fig['after'] in section['content'] and not fig['done']:
                    pdf.add_figure(figures_dir / fig['file'], fig['caption'], fig['num'])
                    fig['done'] = True
        
        elif section['type'] == 'h3':
            current_section = section['content']
            pdf.chapter_title(section['content'], level=3)
            
        elif section['type'] == 'keywords':
            pdf.keywords_box(section['content'])
        
        elif section['type'] == 'text':
            content = section['content'].strip()
            if not content:
                continue
            
            # Split into paragraphs
            paragraphs = content.split('\n\n')
            
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if not para:
                    continue
                
                # Use different formatting for references
                if in_references:
                    # Each reference entry
                    for ref_line in para.split('\n'):
                        ref_line = ref_line.strip()
                        if ref_line and not ref_line.startswith('*'):
                            pdf.reference_text(ref_line)
                else:
                    pdf.body_text(para)
                    
                    # Insert figures after first paragraph of specific sections
                    if i == 0:
                        for fig in figures_to_insert:
                            if fig['after'] in current_section and not fig['done']:
                                pdf.add_figure(figures_dir / fig['file'], fig['caption'], fig['num'])
                                fig['done'] = True
    
    # Insert any remaining figures at the end
    pdf.ln(10)
    for fig in figures_to_insert:
        if not fig['done']:
            print(f"  Adding remaining figure: {fig['file']}")
            pdf.add_figure(figures_dir / fig['file'], fig['caption'], fig['num'])
            fig['done'] = True
    
    # Save PDF
    pdf_path = output_dir / "article_scoping_review.pdf"
    pdf.output(str(pdf_path))
    
    # Get file size
    pdf_size = pdf_path.stat().st_size / 1024
    
    print(f"\n✓ PDF exported: {pdf_path}")
    print(f"  Size: {pdf_size:.1f} KB")
    print(f"  Pages: ~{pdf.page_no()}")
    print(f"  Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
