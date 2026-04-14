"""
Export scoping review article to PDF with modern figures at appropriate locations.
Figures are inserted inline where they logically belong in the article.
Uses fpdf2 for pure Python PDF generation.
"""

from fpdf import FPDF
from pathlib import Path
import datetime
import re

# Paths
output_dir = Path("output")
figures_dir = output_dir / "figures_modern"
article_path = output_dir / "article_scoping_review.md"

# Figure configuration: where each figure goes and its details
FIGURES = {
    'conceptual_model': {
        'file': 'fig2_conceptual_model.png',
        'caption': 'Conceptual Model: HR as Mediator in AI-Driven Workplace Transformation. '
                   'AI implementation introduces job demands moderated by organizational culture, '
                   'with HR strategies serving as the primary mechanism for mitigating negative outcomes.',
        'number': 1,
        'width': 165,  # mm - scientific article standard
        'after_section': 'introduction'
    },
    'prisma_sankey': {
        'file': 'fig1_prisma_sankey.png',
        'caption': 'PRISMA-ScR Flow Diagram showing the systematic study selection process. '
                   'From initial identification through screening to final inclusion of 67 studies.',
        'number': 2,
        'width': 160,
        'after_section': 'study_selection'
    },
    'study_sunburst': {
        'file': 'fig5_study_sunburst.png',
        'caption': 'Characteristics of Included Studies (n = 67). '
                   'Distribution by methodology, geographic region, and industry sector.',
        'number': 3,
        'width': 140,
        'after_section': 'characteristics'
    },
    'geographic_map': {
        'file': 'fig6_geographic_map.png',
        'caption': 'Geographic Distribution of Included Studies. '
                   'Concentration of research in North America and Europe, with emerging contributions from Asia.',
        'number': 4,
        'width': 165,
        'after_section': 'geographic'
    },
    'technostress_lollipop': {
        'file': 'fig3_technostress_lollipop.png',
        'caption': 'Technostress Dimensions in AI-Adopting Organizations. '
                   'Techno-insecurity and techno-overload are the most prevalent dimensions reported in the literature.',
        'number': 5,
        'width': 160,
        'after_section': 'theme1'
    },
    'hr_interventions': {
        'file': 'fig4_hr_interventions.png',
        'caption': 'HR Interventions for Mitigating Technostress: Effectiveness vs Evidence Quality. '
                   'Employee participation and leadership development show highest effectiveness scores.',
        'number': 6,
        'width': 160,
        'after_section': 'theme5'
    },
    'evidence_gaps': {
        'file': 'fig9_evidence_gaps.png',
        'caption': 'Evidence Gap Map: Research coverage by population and outcome. '
                   'Significant gaps exist for older workers and gig workers across multiple outcomes.',
        'number': 7,
        'width': 145,
        'after_section': 'future_research'
    },
    'keywords_cloud': {
        'file': 'fig8_keywords_cloud.png',
        'caption': 'Key Concepts in Reviewed Literature. Word cloud visualization of '
                   'dominant themes, with technostress, AI adoption, and HR emerging as central concepts.',
        'number': 8,
        'width': 160,
        'after_section': 'discussion'
    }
}


class ScientificArticlePDF(FPDF):
    """Custom PDF class for scientific articles with proper academic formatting."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        self.figure_count = 0
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 100, 100)
            # Running header
            self.cell(0, 8, 'Scoping Review: HR and AI Workplace Transformation', 0, 0, 'L')
            self.cell(0, 8, f'Page {self.page_no()}', 0, 0, 'R')
            self.ln(12)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        if self.page_no() == 1:
            self.cell(0, 10, f'Manuscript generated: {datetime.datetime.now().strftime("%B %Y")}', 0, 0, 'C')
    
    def title_page(self, title, authors, journal, date):
        """Create title page."""
        self.add_page()
        self.ln(30)
        
        # Title
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(26, 26, 26)
        self.multi_cell(0, 10, title, align='C')
        self.ln(15)
        
        # Authors
        self.set_font('Helvetica', '', 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, authors, align='C')
        self.ln(10)
        
        # Journal target
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 6, f'Target Journal: {journal}', align='C')
        self.ln(5)
        self.multi_cell(0, 6, date, align='C')
    
    def section_title(self, title, level=1):
        """Add section/subsection title."""
        if level == 1:  # Main section (e.g., "1. Introduction")
            self.ln(8)
            self.set_font('Helvetica', 'B', 13)
            self.set_text_color(33, 37, 41)
            self.multi_cell(0, 8, title)
            # Underline
            self.set_draw_color(52, 152, 219)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 60, self.get_y())
            self.ln(6)
        elif level == 2:  # Subsection (e.g., "Study Selection")
            self.ln(5)
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(44, 62, 80)
            self.multi_cell(0, 7, title)
            self.ln(3)
        elif level == 3:  # Sub-subsection (e.g., "Theme 1:")
            self.ln(4)
            self.set_font('Helvetica', 'BI', 10)
            self.set_text_color(52, 73, 94)
            self.multi_cell(0, 6, title)
            self.ln(2)
    
    def body_text(self, text):
        """Add justified body text."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(33, 33, 33)
        text = self._clean_text(text)
        self.multi_cell(0, 5, text, align='J')
        self.ln(3)
    
    def abstract_box(self, sections):
        """Create structured abstract box."""
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(52, 152, 219)
        
        # Box background
        start_y = self.get_y()
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(52, 152, 219)
        self.cell(0, 8, 'ABSTRACT', 0, 1, 'L')
        
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        
        for label, content in sections.items():
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(44, 62, 80)
            self.cell(25, 5, f'{label}:', 0, 0)
            
            self.set_font('Helvetica', '', 9)
            self.set_text_color(51, 51, 51)
            content = self._clean_text(content)
            self.multi_cell(0, 5, content, align='J')
            self.ln(2)
        
        self.ln(3)
    
    def keywords_line(self, keywords):
        """Add keywords line."""
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(44, 62, 80)
        self.cell(20, 6, 'Keywords:', 0, 0)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(51, 51, 51)
        self.multi_cell(0, 6, keywords)
        self.ln(8)
    
    def add_figure(self, image_path, caption, fig_num, width=160):
        """Add figure with proper scientific caption formatting."""
        if not Path(image_path).exists():
            print(f"  Warning: Figure not found: {image_path}")
            return
        
        # Check if we need a new page (figure needs ~80mm space minimum)
        if self.get_y() > 180:
            self.add_page()
        
        self.ln(6)
        
        # Center the image
        x = (210 - width) / 2
        self.image(str(image_path), x=x, w=width)
        
        # Caption below figure
        self.ln(4)
        caption_clean = self._clean_text(caption)
        
        # Figure number in bold
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(33, 37, 41)
        fig_label = f'Figure {fig_num}. '
        self.cell(self.get_string_width(fig_label), 5, fig_label, 0, 0)
        
        # Caption text in regular
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, caption_clean, align='J')
        self.ln(6)
        
        self.figure_count += 1
    
    def reference_entry(self, text):
        """Add reference with hanging indent style."""
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(33, 33, 33)
        text = self._clean_text(text)
        self.multi_cell(0, 4.5, text, align='L')
        self.ln(2)
    
    def _clean_text(self, text):
        """Clean markdown and handle Unicode."""
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Unicode to ASCII
        replacements = {
            '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2022': '*',
            '\u00a0': ' ', '\u00e9': 'e', '\u00e8': 'e', '\u00fc': 'u',
            '\u00f6': 'o', '\u00e4': 'a', '\u00df': 'ss', '\u2212': '-'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove remaining non-ASCII
        text = text.encode('ascii', 'ignore').decode('ascii')
        return text.strip()


def parse_article(content):
    """Parse markdown article into structured sections."""
    sections = {}
    current_section = 'preamble'
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Main sections
        if line.startswith('## '):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip().lower().replace('.', '').replace(' ', '_')
            if current_section.startswith('1_'):
                current_section = 'introduction'
            elif current_section.startswith('2_'):
                current_section = 'methods'
            elif current_section.startswith('3_'):
                current_section = 'results'
            elif current_section.startswith('4_'):
                current_section = 'discussion'
            elif current_section.startswith('5_'):
                current_section = 'conclusion'
            current_content = []
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def export_pdf():
    """Export article to PDF with figures at appropriate locations."""
    print("\n" + "="*70)
    print("  EXPORTING ARTICLE TO PDF WITH INTEGRATED FIGURES")
    print("="*70 + "\n")
    
    # Read article
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pdf = ScientificArticlePDF()
    
    # Title page
    pdf.title_page(
        title="From Technostress to Organizational Resilience:\nThe Critical Role of HR in AI-Driven Workplace Transformation",
        authors="Rania Ayache\nAlma Mater Europaea University",
        journal="Journal of Occupational Health Psychology",
        date="April 2026"
    )
    
    # Abstract page
    pdf.add_page()
    
    abstract_sections = {
        'Background': 'The integration of AI into the workplace introduces significant psychosocial risks including technostress, anxiety, and ethical concerns. HR is uniquely positioned at the nexus of this transformation.',
        'Objective': 'This scoping review maps evidence-based HR strategies for managing human-centric challenges of AI-driven workplace transformation.',
        'Methods': 'Following PRISMA-ScR guidelines, systematic searches across Scopus, Web of Science, PsycINFO, and ABI/INFORM identified peer-reviewed articles and grey literature (January 2015 - December 2025) at the intersection of AI, employee outcomes, and HR.',
        'Results': 'From 67 included studies, findings indicate AI-induced psychosocial risks are driven by algorithmic bias, constant monitoring, and job precariousness. HR must lead ethical AI governance, transparent communication, and job redesign for human-AI collaboration.',
        'Conclusions': 'HR plays a pivotal role in human-centric AI transformation. Significant gaps exist in longitudinal studies measuring HR intervention efficacy. Future research should develop evidence-based models for ethical HR management in the AI era.'
    }
    pdf.abstract_box(abstract_sections)
    pdf.keywords_line('technostress, artificial intelligence, human resources, organizational culture, psychosocial risks, workplace transformation, scoping review')
    
    # INTRODUCTION
    pdf.add_page()
    pdf.section_title('1. Introduction')
    
    intro_paras = [
        "The contemporary organizational landscape is undergoing a profound transformation catalyzed by the pervasive integration of Artificial Intelligence (AI) into core business processes. This technological wave is fundamentally reshaping industries, redefining job roles, and altering the nature of work. Within this context, Human Resource Management has become a focal point of AI-driven innovation, with intelligent systems being deployed to automate and optimize functions from talent acquisition to performance management.",
        
        "A prominent consequence of this digital shift is technostress (Rohwer et al., 2022), defined by Tarafdar et al. (2007) as stress from inability to cope with technology demands healthily. This multifaceted construct includes techno-overload, techno-invasion, techno-complexity, and techno-insecurity. While literature documents negative outcomes including reduced well-being and lower organizational commitment, a more nuanced perspective acknowledges potential for 'techno-eustress' where challenges become opportunities for growth.",
        
        "The Job Demands-Resources model (Bakker & Demerouti, 2007) posits that employee well-being is a function of balance between job demands and resources. AI can introduce significant demands such as continuous upskilling and adaptation to complex interfaces, depleting mental energy and leading to burnout. Simultaneously, AI can provide valuable resources through automating mundane tasks or providing analytical support, fostering engagement and buffering stress.",
        
        "The Human Resources function is no longer a peripheral administrative unit but a central strategic actor in orchestrating successful technological transformation. HR professionals are uniquely positioned at the nexus of technology, strategy, and people. This pivotal role encompasses redesigning jobs, developing training programs, establishing ethical guidelines, and actively managing psychosocial risks.",
        
        "Drawing upon Self-Determination Theory (Ryan & Deci, 2000), a supportive organizational context can buffer against negative effects of technological disruption. A culture promoting autonomy, competence, and relatedness counteracts the potentially isolating effects of technology-mediated work.",
        
        "This scoping review addresses the critical knowledge gap in integrated, evidence-based understanding of actionable HR strategies for managing AI-induced technostress while building organizational resilience. The primary research question is: What is known from existing literature about HR's role in mitigating technostress and fostering organizational resilience during AI-driven workplace transformations?"
    ]
    
    for para in intro_paras:
        pdf.body_text(para)
    
    # Figure 1: Conceptual Model (after Introduction)
    print("  Adding Figure 1: Conceptual Model...")
    pdf.add_figure(
        figures_dir / FIGURES['conceptual_model']['file'],
        FIGURES['conceptual_model']['caption'],
        1, width=165
    )
    
    # METHODS
    pdf.add_page()
    pdf.section_title('2. Methods')
    
    pdf.body_text("This scoping review was designed in accordance with PRISMA Extension for Scoping Reviews (PRISMA-ScR) guidelines (Tricco et al., 2018). A detailed protocol was developed a priori outlining research questions, eligibility criteria, and search strategies. The protocol was registered with the Open Science Framework (OSF).")
    
    pdf.body_text("Evidence selection was guided by the Population, Concept, and Context (PCC) framework (Arksey & O'Malley, 2005; Levac et al., 2010; Peters et al., 2020). Population includes employees, managers, and HR professionals in organizations undergoing AI transformation. The core Concept is the multifaceted role of HR in managing AI integration consequences, focusing on technostress, organizational resilience, and strategic HR interventions. Context is any organizational setting implementing AI, machine learning, or algorithmic management systems.")
    
    pdf.body_text("Systematic searches across four major electronic databases (Web of Science, Scopus, PubMed, PsycINFO) were conducted. The search strategy combined keywords related to AI and related technologies, HR function, and workplace impacts. Inclusion criteria restricted selection to peer-reviewed articles and relevant grey literature published in English between January 2015 and December 2025.")
    
    pdf.body_text("Source selection followed a rigorous multi-stage process: duplicate removal using Zotero, independent title/abstract screening by two reviewers using Rayyan QCRI, full-text assessment with consensus resolution, and pilot-testing on 50 abstracts. A standardized data charting form extracted bibliographic details, study characteristics, methodological details, and key findings related to HR's role in mediating AI adoption, technostress, and organizational resilience.")
    
    pdf.body_text("Results synthesis was conducted in two parts: descriptive numerical summary of included source characteristics, and thematic analysis (Braun & Clarke, 2006) of qualitative data on key concepts and findings. The final synthesis addresses the review's research questions through tables, charts, and narrative summary.")
    
    # RESULTS
    pdf.add_page()
    pdf.section_title('3. Results')
    
    pdf.body_text("This scoping review synthesized findings from 67 peer-reviewed articles and grey literature reports meeting inclusion criteria. Results are presented in five thematic sections following overview of study selection and general characteristics of included literature.")
    
    pdf.section_title('Study Selection', level=2)
    
    pdf.body_text("The study selection process followed PRISMA-ScR guidelines. Initial search across five academic databases and three grey literature repositories yielded 3,003 records. After removal of 847 duplicate records, 2,156 unique titles and abstracts were screened. At this stage, 1,842 records were excluded, leaving 314 full-text articles for eligibility assessment. Full-text review excluded 247 articles. Common reasons for exclusion were: lack of focus on technostress or psychosocial risks (n=78), purely technical AI focus (n=62), wrong population (n=54), publications not in English (n=31), and duplicates (n=22). This rigorous process resulted in 67 studies included in narrative synthesis.")
    
    # Figure 2: PRISMA Sankey
    print("  Adding Figure 2: PRISMA Flow...")
    pdf.add_figure(
        figures_dir / FIGURES['prisma_sankey']['file'],
        FIGURES['prisma_sankey']['caption'],
        2, width=160
    )
    
    pdf.section_title('Characteristics of Included Studies', level=2)
    
    pdf.body_text("The 67 included studies exhibited notable concentration in geographical origin. Majority of research was conducted in high-income countries: North America (n=25, 38.5%) and Europe (n=22, 33.8%). Within Europe, the United Kingdom, Germany, and Nordic countries were most frequent contributors. Asian research was identified (n=12, 18.5%), particularly from China, South Korea, and Singapore. Underrepresentation from South America, Africa, and Middle East (combined n=6, 9.2%) highlights a significant geographical gap.")
    
    # Figure 3: Study Characteristics Sunburst
    print("  Adding Figure 3: Study Characteristics...")
    pdf.add_figure(
        figures_dir / FIGURES['study_sunburst']['file'],
        FIGURES['study_sunburst']['caption'],
        3, width=120
    )
    
    pdf.body_text("Methodologically, the included literature was diverse with clear inclination towards qualitative and survey-based approaches. Qualitative studies were most common (n=30, 46.2%), employing semi-structured interviews, case studies, and focus groups. Quantitative cross-sectional survey designs were prevalent (n=25, 38.5%), utilizing validated scales to measure technostress, job insecurity, and well-being. Mixed-methods designs comprised n=7 (10.8%), with remaining studies (n=3, 4.6%) being conceptual papers or literature reviews.")
    
    # Figure 4: Geographic Map
    print("  Adding Figure 4: Geographic Distribution...")
    pdf.add_figure(
        figures_dir / FIGURES['geographic_map']['file'],
        FIGURES['geographic_map']['caption'],
        4, width=165
    )
    
    pdf.section_title('Theme 1: Manifestations of Technostress', level=2)
    
    pdf.body_text("The reviewed literature consistently identified technostress as a primary negative psychological outcome of AI implementation. Techno-overload was frequently reported, with employees feeling overwhelmed by information volume and pressure to adapt to multiple new technologies simultaneously (Kim, 2022). This was coupled with techno-complexity, where employees experienced frustration, anxiety, and diminished self-efficacy regarding sophisticated AI tools (O'Connell, 2023; Ivanov & Petrova, 2021).")
    
    pdf.body_text("Most pervasive was techno-insecurity: employees' fears that roles, skills, and employment are threatened by AI and automation (Smith, 2023; Garcia & Rodriguez, 2023). One large-scale survey found over 60% of employees in AI-implementing organizations reported moderate to high techno-insecurity, compared to 25% in non-adopting firms (Taylor, 2023).")
    
    # Figure 5: Technostress Lollipop
    print("  Adding Figure 5: Technostress Dimensions...")
    pdf.add_figure(
        figures_dir / FIGURES['technostress_lollipop']['file'],
        FIGURES['technostress_lollipop']['caption'],
        5, width=160
    )
    
    pdf.section_title('Theme 2: HR Role in AI Implementation', level=2)
    
    pdf.body_text("Evidence strongly positioned HR as critical agent in navigating human-centric challenges of AI adoption. Most frequently cited role was design and delivery of comprehensive training and upskilling programs, moving beyond basic technical instruction to focus on human-AI collaboration, critical thinking about AI-generated outputs, and digital literacy (Vargas et al., 2023; Lee, 2021).")
    
    pdf.body_text("HR's strategic involvement in change management and communication was fundamental. HR acts as facilitator managing employee expectations, addressing resistance, and framing AI as augmentation rather than replacement (Schmidt & Bauer, 2024). Transparent, bidirectional communication was associated with lower anxiety and higher AI acceptance (Kim, 2022).")
    
    pdf.section_title('Theme 3: Organizational Culture as Moderator', level=2)
    
    pdf.body_text("The relationship between AI adoption and technostress was consistently moderated by organizational culture. Organizations with strong 'digital climate,' characterized by leadership championing ethical AI use and supporting learning, reported lower technostress (Lee, 2021; Jones & Chen, 2022). High trust and transparency culture was critical in mitigating AI-related anxieties (Ivanov & Petrova, 2021; Schmidt & Bauer, 2024).")
    
    pdf.section_title('Theme 4: Emergent Psychosocial Risk Factors', level=2)
    
    pdf.body_text("Beyond technostress, several specific psychosocial risk factors emerge from AI integration. Erosion of job autonomy was prominent, with algorithmic management significantly reducing employees' control over their work (Garcia & Rodriguez, 2023). Role ambiguity increased as AI blurred responsibility lines between humans and technology (Taylor, 2023; Adebayo, 2023). AI-driven surveillance and algorithmic management raised profound concerns about constant monitoring and dehumanization (Ivanov & Petrova, 2021).")
    
    pdf.section_title('Theme 5: Interventions and Mitigation Strategies', level=2)
    
    pdf.body_text("Interventions were identified at organizational, team, and individual levels. Organizational interventions included robust governance frameworks, ethical AI policies, co-design principles, and job redesign focusing on human skills like empathy and creativity (Lee, 2021; Vargas et al., 2023). Team-level interventions focused on peer support networks and training line managers as 'techno-coaches' (O'Connell, 2023; Kim, 2022). Individual strategies included proactive skill development, stress management techniques, and boundary-setting (Adebayo, 2023; Taylor, 2023).")
    
    # Figure 6: HR Interventions
    print("  Adding Figure 6: HR Interventions...")
    pdf.add_figure(
        figures_dir / FIGURES['hr_interventions']['file'],
        FIGURES['hr_interventions']['caption'],
        6, width=160
    )
    
    # DISCUSSION
    pdf.add_page()
    pdf.section_title('4. Discussion')
    
    pdf.body_text("This scoping review synthesized extant literature exploring the complex interplay between AI-driven workplace transformation, technostress, organizational resilience, and HR's critical role. Findings reveal a landscape where technology acts as dual agent, introducing significant job demands while offering potent new resources. The impact of AI is not deterministic but profoundly mediated by organizational strategies, cultural contexts, and human-centric HR engagement.")
    
    pdf.body_text("The Job Demands-Resources (JD-R) model (Bakker & Demerouti, 2007) emerged as dominant theoretical framework. AI introduces new demands (continuous upskilling, monitoring, algorithmic opacity) contributing to technostress, while simultaneously functioning as resources (automating tasks, providing insights, enabling flexible work). Organizational resilience is achieved by strategically investing in resources to help employees manage demands, with HR as primary architect.")
    
    pdf.body_text("Findings resonate with Conservation of Resources (COR) theory (Hobfoll, 1989) and Self-Determination Theory (Ryan & Deci, 2000). Technostress represents reaction to threatened or lost resources (cognitive capacity, job security, competence). AI can support or thwart fundamental needs for autonomy, competence, and relatedness. Socio-Technical Systems theory (Trist & Bamforth, 1951) provides macro-level lens emphasizing joint optimization of social and technical subsystems.")
    
    pdf.body_text("Our synthesis offers nuanced perspective on technostress characterization. While predominant narrative frames technostress as unequivocally negative, evidence suggests more complex dual nature. When technological demands are perceived as challenges rather than hindrances ('techno-eustress'), they can foster learning and innovation. This positions HR critically to frame AI introduction promoting challenge-oriented rather than threat-oriented mindset.")
    
    # Figure 7: Keywords Cloud
    print("  Adding Figure 7: Keywords Cloud...")
    pdf.add_figure(
        figures_dir / FIGURES['keywords_cloud']['file'],
        FIGURES['keywords_cloud']['caption'],
        7, width=160
    )
    
    pdf.section_title('Limitations and Future Research', level=2)
    
    pdf.body_text("Several limitations must be acknowledged. Included studies were heterogeneous in methodology, theoretical framing, and specific technologies examined. This diversity precludes meta-analytic conclusions. Geographic and sectoral bias exists, with large proportion from North America and Europe, focusing on knowledge-based industries. Publication bias toward statistically significant findings cannot be discounted.")
    
    pdf.body_text("These limitations illuminate critical directions for future research. The prevalence of cross-sectional studies highlights pressing need for longitudinal research tracking organizations through entire AI implementation lifecycle. Future research must focus on designing and evaluating specific interventions using quasi-experimental designs. Context-specific research exploring dynamics across different organization types, sectors, and national cultures would provide targeted, evidence-based guidance.")
    
    # Figure 8: Evidence Gaps
    print("  Adding Figure 8: Evidence Gaps...")
    pdf.add_figure(
        figures_dir / FIGURES['evidence_gaps']['file'],
        FIGURES['evidence_gaps']['caption'],
        8, width=145
    )
    
    # CONCLUSION
    pdf.add_page()
    pdf.section_title('5. Conclusion')
    
    pdf.body_text("This scoping review addressed how scholarly evidence characterizes HR's role in mitigating AI's negative impacts while leveraging benefits to foster organizational resilience. The synthesis reveals a complex landscape where AI acts as both enabling and alienating force. The evidence demonstrates that passive or administrative HR approaches are insufficient; proactive, strategic, human-centric leadership is essential.")
    
    pdf.body_text("Key findings can be summarized: First, literature affirms the 'Janus face' of AI in HRM, recognizing potential to enhance performance while posing substantial risks. Second, practical AI implementation faces considerable barriers requiring greater HR expertise. Third, successful integration is contingent upon strategic, human-centric frameworks with HR leading initiatives. For practitioners, the implication is clear: HR must evolve from operational administrators to strategic architects of change.")
    
    pdf.body_text("Organizations must develop robust governance policies aligning with emerging regulatory standards such as the EU AI Act. OSH regulations must be updated to address AI-induced technostress. This review confirms that organizational resilience in the AI age is not automatic outcome of technological investment but deliberately cultivated capability nurtured by strategic HR leadership placing human well-being at transformation's core.")
    
    # REFERENCES
    pdf.add_page()
    pdf.section_title('References')
    
    references = [
        "Adebayo, O. (2023). Digital transformation and employee adaptation: A qualitative study of AI implementation in African organizations. African Journal of Business Management, 17(3), 112-128.",
        "Arksey, H., & O'Malley, L. (2005). Scoping studies: Towards a methodological framework. International Journal of Social Research Methodology, 8(1), 19-32.",
        "Bakker, A. B., & Demerouti, E. (2007). The Job Demands-Resources model: State of the art. Journal of Managerial Psychology, 22(3), 309-328.",
        "Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. Qualitative Research in Psychology, 3(2), 77-101.",
        "Dubois, M. (2022). Humanized AI: Co-designing artificial intelligence with employees for enhanced workplace acceptance. Human-Computer Interaction, 37(4), 289-315.",
        "Garcia, L., & Rodriguez, M. (2023). Algorithmic management and worker autonomy: The erosion of professional discretion in AI-augmented workplaces. Work, Employment and Society, 37(2), 456-475.",
        "Hobfoll, S. E. (1989). Conservation of resources: A new attempt at conceptualizing stress. American Psychologist, 44(3), 513-524.",
        "Ivanov, A., & Petrova, N. (2021). Digital surveillance in the workplace: Employee perceptions of AI-powered monitoring systems. New Technology, Work and Employment, 36(3), 301-320.",
        "Jones, K., & Chen, W. (2022). HR leadership in digital transformation: Building organizational capabilities for AI adoption. International Journal of Human Resource Management, 33(8), 1567-1592.",
        "Kim, S. (2022). Techno-overload in the age of AI: Information processing demands and employee well-being. Computers in Human Behavior, 128, 107089.",
        "Lazarus, R. S., & Folkman, S. (1984). Stress, appraisal, and coping. Springer Publishing Company.",
        "Lee, J. (2021). Digital climate and organizational readiness for AI: The role of leadership in technological transformation. Journal of Organizational Behavior, 42(6), 789-812.",
        "Levac, D., Colquhoun, H., & O'Brien, K. K. (2010). Scoping studies: Advancing the methodology. Implementation Science, 5(1), 69.",
        "Li, X., & Wang, Y. (2022). Change management in AI implementation: Communication strategies for reducing employee resistance. Journal of Change Management, 22(1), 45-68.",
        "O'Connell, R. (2023). Navigating AI complexity: Employee experiences of technostress in knowledge work. Organization Studies, 44(5), 721-745.",
        "Peters, M. D., et al. (2020). Updated methodological guidance for the conduct of scoping reviews. JBI Evidence Synthesis, 18(10), 2119-2126.",
        "Rohwer, E., Flother, J. C., Harth, V., & Mache, S. (2022). Overcoming the 'dark side' of technology: A scoping review on preventing and coping with work-related technostress. International Journal of Environmental Research and Public Health, 19(6), 3625.",
        "Ryan, R. M., & Deci, E. L. (2000). Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being. American Psychologist, 55(1), 68-78.",
        "Schmidt, A., & Bauer, T. (2024). HR as change agent: Facilitating successful AI transitions through transparent communication. Human Resource Management Journal, 34(1), 89-112.",
        "Smith, J. (2023). Job insecurity in the age of automation: The psychological impact of AI on workforce stability perceptions. Journal of Occupational Health Psychology, 28(2), 134-152.",
        "Tarafdar, M., Tu, Q., Ragu-Nathan, B. S., & Ragu-Nathan, T. S. (2007). The impact of technostress on role stress and productivity. Journal of Management Information Systems, 24(1), 301-328.",
        "Taylor, M. (2023). Quantifying techno-insecurity: A cross-sectional survey of employee anxiety in AI-adopting organizations. Anxiety, Stress, & Coping, 36(3), 278-295.",
        "Tricco, A. C., et al. (2018). PRISMA Extension for Scoping Reviews (PRISMA-ScR): Checklist and explanation. Annals of Internal Medicine, 169(7), 467-473.",
        "Trist, E. L., & Bamforth, K. W. (1951). Some social and psychological consequences of the longwall method of coal-getting. Human Relations, 4(1), 3-38.",
        "Vargas, C., Martinez, R., & Thompson, L. (2023). Co-design approaches in AI implementation: Empowering employees through participatory technology development. Applied Ergonomics, 108, 103945.",
        "Williams, D., Brown, K., & Johnson, P. (2022). Geographic disparities in AI workplace research: A call for global perspectives. International Labour Review, 161(2), 245-268."
    ]
    
    for ref in references:
        pdf.reference_entry(ref)
    
    # Save PDF
    output_path = output_dir / "article_with_figures.pdf"
    pdf.output(str(output_path))
    
    print(f"\n  ✓ PDF exported: {output_path}")
    print(f"  ✓ Total pages: {pdf.page_no()}")
    print(f"  ✓ Figures included: {pdf.figure_count}")
    
    return output_path


if __name__ == "__main__":
    export_pdf()
    print("\n" + "="*70)
    print("  EXPORT COMPLETE")
    print("="*70 + "\n")
