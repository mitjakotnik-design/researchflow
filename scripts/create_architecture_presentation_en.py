#!/usr/bin/env python3
"""
ResearchFlow - Technical Architecture Presentation (English)
User Journey first, then Architecture
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon
import numpy as np
from datetime import datetime

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

UNICODE_FONT = 'SegoeUI'
UNICODE_FONT_BOLD = 'SegoeUIBold'

pdfmetrics.registerFont(TTFont(UNICODE_FONT, 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont(UNICODE_FONT_BOLD, 'C:/Windows/Fonts/segoeuib.ttf'))

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "architecture_presentation_en"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {
    'primary': '#2563EB',
    'secondary': '#7C3AED',
    'accent': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'dark': '#1F2937',
    'light': '#F3F4F6',
    'white': '#FFFFFF',
    'blue_light': '#DBEAFE',
    'purple_light': '#EDE9FE',
    'green_light': '#D1FAE5',
    'orange_light': '#FEF3C7',
    'red_light': '#FEE2E2',
}


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_user_journey():
    """Create user journey diagram"""
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(8, 10.5, 'User Journey: From Research Question to Publication', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    steps_row1 = [
        ('1. Login', 'Create Project', COLORS['primary']),
        ('2. Research Plan', 'Define questions', COLORS['primary']),
        ('3. Search Strings', 'AI generates', COLORS['secondary']),
        ('4. Import Results', 'Upload .ris/.csv', COLORS['secondary']),
        ('5. Abstract Screen', 'AI categorizes', COLORS['accent']),
    ]
    
    steps_row2 = [
        ('6. Get Full Texts', 'Upload PDFs', COLORS['accent']),
        ('7. Analysis', 'Themes, gaps', COLORS['warning']),
        ('8. AI Writing', 'Section by section', COLORS['warning']),
        ('9. Visualizations', 'PRISMA, EGM', COLORS['danger']),
        ('10. Export', 'PDF/DOCX ready', COLORS['danger']),
    ]
    
    for i, (title, desc, color) in enumerate(steps_row1):
        x = 0.8 + i * 3
        y = 7.5
        
        box = FancyBboxPatch((x, y - 0.8), 2.6, 1.6, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        circle = Circle((x + 0.4, y + 0.5), 0.25, facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        ax.text(x + 0.4, y + 0.5, title.split('.')[0].replace(' ', ''), ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        ax.text(x + 1.3, y + 0.4, title.split('. ')[1], ha='center', va='center', 
                fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.3, y - 0.2, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
        
        if i < 4:
            ax.annotate('', xy=(x + 3.0, y), xytext=(x + 2.7, y),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    for i, (title, desc, color) in enumerate(steps_row2):
        x = 0.8 + i * 3
        y = 4.5
        
        box = FancyBboxPatch((x, y - 0.8), 2.6, 1.6, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        num = str(i + 6)
        circle = Circle((x + 0.4, y + 0.5), 0.25, facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        ax.text(x + 0.4, y + 0.5, num, ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        ax.text(x + 1.3, y + 0.4, title.split('. ')[1], ha='center', va='center', 
                fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.3, y - 0.2, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
        
        if i < 4:
            ax.annotate('', xy=(x + 3.0, y), xytext=(x + 2.7, y),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    ax.plot([15.0, 15.5], [7.5, 7.5], color=COLORS['dark'], lw=2)
    ax.plot([15.5, 15.5], [7.5, 4.5], color=COLORS['dark'], lw=2)
    ax.annotate('', xy=(15.0, 4.5), xytext=(15.5, 4.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    ax.plot([1, 15], [2, 2], color=COLORS['dark'], linewidth=2)
    timeline_points = [
        (2.5, 'Day 1-2', 'Setup'),
        (5.5, 'Day 3-5', 'Search'),
        (8.5, 'Week 2', 'Screen'),
        (11.5, 'Week 3-4', 'Analysis'),
        (14, 'Week 5-6', 'Export'),
    ]
    for x, time, phase in timeline_points:
        ax.plot(x, 2, 'o', markersize=10, color=COLORS['primary'])
        ax.text(x, 1.5, time, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        ax.text(x, 1.1, phase, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    ax.text(8, 0.5, 'Typical timeline: 4-6 weeks (vs. 6-12 months traditional)', 
            ha='center', va='center', fontsize=11, style='italic', color=COLORS['accent'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "user_journey.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_high_level_architecture():
    """Create high-level system architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7, 10.5, 'ResearchFlow - High-Level System Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # USER LAYER
    user_box = FancyBboxPatch((1, 8.8), 12, 1.4, boxstyle="round,pad=0.03",
                               facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(user_box)
    ax.text(1.3, 9.9, 'USER INTERFACE LAYER', ha='left', va='center', 
            fontsize=11, fontweight='bold', color=COLORS['primary'])
    
    user_components = ['Next.js 14\nFrontend', 'React\nComponents', 'Chatbot\nInterface', 'HITL\nDashboard']
    for i, comp in enumerate(user_components):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 8.95), 2.4, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 9.35, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # API GATEWAY
    api_box = FancyBboxPatch((1, 7.0), 12, 1.4, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(api_box)
    ax.text(1.3, 8.1, 'API GATEWAY (Cloud Run)', ha='left', va='center',
            fontsize=11, fontweight='bold', color=COLORS['secondary'])
    
    api_components = ['Authentication', 'Rate Limiting', 'Validation', 'Load Balancing']
    for i, comp in enumerate(api_components):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 7.15), 2.4, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 7.55, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # BACKEND SERVICES
    backend_box = FancyBboxPatch((1, 4.0), 12, 2.6, boxstyle="round,pad=0.03",
                                  facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(backend_box)
    ax.text(1.3, 6.3, 'BACKEND SERVICES (Python/FastAPI)', ha='left', va='center',
            fontsize=11, fontweight='bold', color=COLORS['accent'])
    
    services_row1 = ['Orchestration', 'RAG Service', 'Agent Cluster', 'HITL Manager']
    for i, comp in enumerate(services_row1):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 5.4), 2.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 5.75, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    services_row2 = ['Doc Processor', 'Search Generator', 'Article Gen', 'Export Service']
    for i, comp in enumerate(services_row2):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 4.3), 2.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 4.65, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # DATA LAYER
    data_box = FancyBboxPatch((1, 1.5), 12, 2.1, boxstyle="round,pad=0.03",
                               facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(data_box)
    ax.text(1.3, 3.3, 'DATA LAYER', ha='left', va='center',
            fontsize=11, fontweight='bold', color=COLORS['warning'])
    
    data_components = [('Firestore', 'Metadata'), ('ChromaDB', 'Vectors'), ('Cloud Storage', 'Files'), ('Redis', 'Cache')]
    for i, (name, desc) in enumerate(data_components):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 1.7), 2.4, 1.3, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 2.55, name, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.2, 2.1, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # SECURITY LAYER
    sec_box = FancyBboxPatch((1, 0.3), 12, 0.9, boxstyle="round,pad=0.03",
                              facecolor=COLORS['red_light'], edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(sec_box)
    ax.text(7, 0.75, 'SECURITY: TLS 1.3  |  Cloud Armor  |  PromptGuard  |  Audit Logs  |  Monitoring', 
            ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['danger'])
    
    # Arrows
    arrow_positions = [3.5, 7, 10.5]
    for xpos in arrow_positions:
        ax.annotate('', xy=(xpos, 8.8), xytext=(xpos, 8.4), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
        ax.annotate('', xy=(xpos, 7.0), xytext=(xpos, 6.6), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
        ax.annotate('', xy=(xpos, 4.0), xytext=(xpos, 3.6), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "high_level_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_multi_agent_architecture():
    """Create multi-agent system architecture diagram"""
    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7.5, 10.5, 'Multi-Agent System Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # ORCHESTRATOR
    orch_box = FancyBboxPatch((5.5, 8.5), 4, 1.5, boxstyle="round,pad=0.05",
                               facecolor=COLORS['primary'], edgecolor=COLORS['dark'], linewidth=2)
    ax.add_patch(orch_box)
    ax.text(7.5, 9.4, 'ORCHESTRATOR', ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    ax.text(7.5, 8.9, 'Workflow Coordination', ha='center', va='center', fontsize=10, color='white')
    
    agents_row1 = [
        (2, 5.5, 'Research Plan\nAgent', COLORS['secondary'], 'Parse questions\nDefine PICO/PCC'),
        (5.5, 5.5, 'Search String\nAgent', COLORS['accent'], 'Boolean queries\nMulti-database'),
        (9, 5.5, 'Screening\nAgent', COLORS['warning'], 'Abstract analysis\nInclude/Exclude'),
        (12.5, 5.5, 'Analysis\nAgent', COLORS['danger'], 'Gap detection\nTheme extraction'),
    ]
    
    for x, y, name, color, desc in agents_row1:
        box = FancyBboxPatch((x - 1.4, y - 1.2), 2.8, 2.4, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        header = FancyBboxPatch((x - 1.3, y + 0.6), 2.6, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x, y + 0.85, name, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.text(x, y - 0.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        ax.annotate('', xy=(x, y + 1.2), xytext=(7.5, 8.5),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2, 
                                  connectionstyle=f"arc3,rad={0.15 if x < 7.5 else -0.15 if x > 7.5 else 0}"))
    
    agents_row2 = [
        (3.5, 1.8, 'Article\nGenerator', COLORS['secondary'], 'Section writing\nCitation format'),
        (7.5, 1.8, 'Export\nAgent', COLORS['accent'], 'PDF/DOCX\nFigure embed'),
        (11.5, 1.8, 'Visualization\nAgent', COLORS['warning'], 'PRISMA diagrams\nEvidence maps'),
    ]
    
    for x, y, name, color, desc in agents_row2:
        box = FancyBboxPatch((x - 1.4, y - 1.2), 2.8, 2.4, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        header = FancyBboxPatch((x - 1.3, y + 0.6), 2.6, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x, y + 0.85, name, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.text(x, y - 0.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    for x in [3.5, 7.5, 11.5]:
        ax.plot([x, x], [3.0, 4.3], color=COLORS['dark'], linestyle=':', linewidth=1.5, alpha=0.6)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "multi_agent_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_memory_architecture():
    """Create 3-tier memory architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, '3-Tier Memory Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Working Memory
    wm_box = FancyBboxPatch((0.5, 6.3), 13, 2.7, boxstyle="round,pad=0.03",
                             facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=3)
    ax.add_patch(wm_box)
    ax.text(7, 8.7, 'WORKING MEMORY (Redis)', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['accent'])
    
    wm_items = [('Task Context', 'Agent state'), ('Conversation', 'User queries'), ('Temp Results', 'Partial data'), ('HITL Queue', 'Decisions')]
    for i, (title, desc) in enumerate(wm_items):
        x = 1.2 + i * 3.1
        box = FancyBboxPatch((x, 6.5), 2.7, 1.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.35, 7.8, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.35, 7.2, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Short-Term Memory
    stm_box = FancyBboxPatch((0.5, 3.2), 13, 2.7, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=3)
    ax.add_patch(stm_box)
    ax.text(7, 5.6, 'SHORT-TERM MEMORY (ChromaDB)', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    stm_items = [('Doc Chunks', '768-dim vectors'), ('Reasoning', 'Decision logs'), ('Screening', 'Inc/Exc/Unc'), ('Search Cache', 'Query results')]
    for i, (title, desc) in enumerate(stm_items):
        x = 1.2 + i * 3.1
        box = FancyBboxPatch((x, 3.4), 2.7, 1.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.35, 4.7, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.35, 4.1, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Long-Term Memory
    ltm_box = FancyBboxPatch((0.5, 0.3), 13, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=3)
    ax.add_patch(ltm_box)
    ax.text(7, 2.5, 'LONG-TERM MEMORY (Firestore + Cloud Storage)', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['primary'])
    
    ltm_items = [('Project State', 'Full history'), ('User Profiles', 'Preferences'), ('Doc Archive', 'PDFs, text'), ('Articles', 'Final outputs')]
    for i, (title, desc) in enumerate(ltm_items):
        x = 1.2 + i * 3.1
        box = FancyBboxPatch((x, 0.5), 2.7, 1.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.35, 1.6, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.35, 1.1, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Arrows
    for side_x in [0.7, 13.3]:
        ax.annotate('', xy=(side_x, 6.3), xytext=(side_x, 5.9), arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
        ax.annotate('', xy=(side_x, 3.2), xytext=(side_x, 2.8), arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "memory_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_rag_architecture():
    """Create RAG system architecture diagram"""
    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7.5, 10.5, 'RAG (Retrieval-Augmented Generation) Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # INGESTION
    ing_box = FancyBboxPatch((0.5, 3.5), 4, 6.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(ing_box)
    ax.text(2.5, 9.7, 'INGESTION', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['primary'])
    
    ing_steps = [('1. PDF Upload', 8.8), ('2. Text Extract', 7.8), ('3. Chunking', 6.8), ('4. Embedding', 5.8), ('5. Index Store', 4.8)]
    for step, y in ing_steps:
        box = FancyBboxPatch((0.8, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    for i in range(len(ing_steps) - 1):
        ax.annotate('', xy=(2.5, ing_steps[i+1][1] + 0.4), xytext=(2.5, ing_steps[i][1] - 0.4),
                   arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=1.5))
    
    ax.text(2.5, 4.0, 'PyMuPDF\n1024 tokens\n50 overlap', ha='center', va='center', fontsize=8, style='italic', color=COLORS['dark'])
    
    # VECTOR DATABASE
    vdb_box = FancyBboxPatch((5, 3.5), 5, 6.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(vdb_box)
    ax.text(7.5, 9.7, 'VECTOR DATABASE', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    chroma_box = FancyBboxPatch((5.8, 7.8), 3.4, 1.5, boxstyle="round,pad=0.03",
                                 facecolor=COLORS['secondary'], edgecolor='white', linewidth=2)
    ax.add_patch(chroma_box)
    ax.text(7.5, 8.7, 'ChromaDB', ha='center', va='center', fontsize=13, fontweight='bold', color='white')
    ax.text(7.5, 8.2, '768-dim embeddings', ha='center', va='center', fontsize=9, color='white')
    
    indices = [('Document Index', 6.8), ('Reasoning Index', 5.8), ('Metadata Index', 4.8)]
    for name, y in indices:
        box = FancyBboxPatch((5.5, y - 0.35), 4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(7.5, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # RETRIEVAL
    ret_box = FancyBboxPatch((10.5, 3.5), 4, 6.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ret_box)
    ax.text(12.5, 9.7, 'RETRIEVAL', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['accent'])
    
    ret_steps = [('1. Query Embed', 8.8), ('2. Hybrid Search', 7.8), ('3. Re-ranking', 6.8), ('4. Context Build', 5.8), ('5. LLM Generate', 4.8)]
    for step, y in ret_steps:
        box = FancyBboxPatch((10.8, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(12.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    for i in range(len(ret_steps) - 1):
        ax.annotate('', xy=(12.5, ret_steps[i+1][1] + 0.4), xytext=(12.5, ret_steps[i][1] - 0.4),
                   arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=1.5))
    
    ax.text(12.5, 4.0, 'BM25+Semantic\nTop-k: 10\nGemini 2.5', ha='center', va='center', fontsize=8, style='italic', color=COLORS['dark'])
    
    # Arrows
    ax.annotate('', xy=(5, 6.5), xytext=(4.5, 6.5), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(10.5, 6.5), xytext=(10, 6.5), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Output
    out_box = FancyBboxPatch((4, 0.5), 7, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(out_box)
    ax.text(7.5, 2.5, 'GENERATED OUTPUT', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['warning'])
    ax.text(7.5, 1.5, 'Grounded in sources  |  Inline citations  |  Reasoning traces', ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    ax.annotate('', xy=(7.5, 3.0), xytext=(12.5, 4.4),
               arrowprops=dict(arrowstyle='->', color=COLORS['warning'], lw=2, connectionstyle="arc3,rad=-0.2"))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "rag_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_workflow_pipeline():
    """Create 8-phase workflow pipeline"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(8, 9.5, '8-Phase Scoping Review Workflow', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    phases = [
        ('Phase 1', 'Research Plan', COLORS['primary'], 'Define questions\nSet PICO criteria', 'HITL #1'),
        ('Phase 2', 'Search Strings', COLORS['primary'], 'Boolean queries\nWoS/Scopus/PubMed', 'HITL #2'),
        ('Phase 3', 'Abstract Screen', COLORS['secondary'], 'AI categorization\nInc/Exc/Uncertain', 'HITL #3'),
        ('Phase 4', 'Full-text ID', COLORS['secondary'], 'DOI resolution\nPDF retrieval', ''),
    ]
    
    phases2 = [
        ('Phase 5', 'FT Ingestion', COLORS['accent'], 'PDF parsing\nVector embedding', 'HITL #4'),
        ('Phase 6', 'Gap Analysis', COLORS['accent'], 'Theme extraction\nPattern analysis', 'HITL #5'),
        ('Phase 7', 'Article Gen', COLORS['warning'], 'Section writing\nCitation format', 'HITL #6-7'),
        ('Phase 8', 'Export & Viz', COLORS['danger'], 'PDF/DOCX\nPRISMA diagram', 'HITL #8-10'),
    ]
    
    for i, (num, name, color, tasks, hitl) in enumerate(phases):
        x = 0.8 + i * 3.8
        y = 6.5
        box = FancyBboxPatch((x, y - 1), 3.3, 2.8, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        header = FancyBboxPatch((x + 0.1, y + 1.2), 3.1, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x + 1.65, y + 1.45, f'{num}: {name}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.text(x + 1.65, y + 0.3, tasks, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        if hitl:
            ax.text(x + 1.65, y - 0.7, hitl, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1, pad=0.2))
        if i < 3:
            ax.annotate('', xy=(x + 4.0, y + 0.5), xytext=(x + 3.4, y + 0.5),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    for i, (num, name, color, tasks, hitl) in enumerate(phases2):
        x = 0.8 + i * 3.8
        y = 2.5
        box = FancyBboxPatch((x, y - 1), 3.3, 2.8, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        header = FancyBboxPatch((x + 0.1, y + 1.2), 3.1, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x + 1.65, y + 1.45, f'{num}: {name}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.text(x + 1.65, y + 0.3, tasks, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        if hitl:
            ax.text(x + 1.65, y - 0.7, hitl, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1, pad=0.2))
        if i < 3:
            ax.annotate('', xy=(x + 4.0, y + 0.5), xytext=(x + 3.4, y + 0.5),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    ax.annotate('', xy=(15.0, 4.5), xytext=(15.0, 5.5), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.plot([14.5, 15.0], [5.5, 5.5], color=COLORS['dark'], lw=2)
    ax.plot([14.5, 15.0], [4.5, 4.5], color=COLORS['dark'], lw=2)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "workflow_pipeline.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_hitl_architecture():
    """Create HITL architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Human-in-the-Loop (HITL) Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # AI Processing
    ai_box = FancyBboxPatch((0.5, 3), 4, 5.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['secondary'], alpha=0.15, edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(2.5, 8.2, 'AI PROCESSING', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    ai_steps = ['Document Analysis', 'Decision Generation', 'Confidence Score', 'Reasoning Trace', 'Action Queue']
    for i, step in enumerate(ai_steps):
        y = 7.3 - i * 0.9
        box = FancyBboxPatch((0.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # HITL Decision
    hitl_box = FancyBboxPatch((5, 3.5), 4, 4.5, boxstyle="round,pad=0.05",
                               facecolor=COLORS['warning'], alpha=0.2, edgecolor=COLORS['warning'], linewidth=3)
    ax.add_patch(hitl_box)
    ax.text(7, 7.7, 'HITL DECISION', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['warning'])
    
    decisions = [('[OK] APPROVE', 6.8, COLORS['accent']), ('[X] REJECT', 5.9, COLORS['danger']), 
                 ('[EDIT] MODIFY', 5.0, COLORS['primary']), ('[...] DEFER', 4.1, '#6B7280')]
    for text, y, color in decisions:
        box = FancyBboxPatch((5.3, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor=color, alpha=0.25, edgecolor=color, linewidth=1)
        ax.add_patch(box)
        ax.text(7, y, text, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
    
    # Human Review
    human_box = FancyBboxPatch((9.5, 3), 4, 5.5, boxstyle="round,pad=0.03",
                                facecolor=COLORS['accent'], alpha=0.15, edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(human_box)
    ax.text(11.5, 8.2, 'HUMAN REVIEW', ha='center', va='center', fontsize=13, fontweight='bold', color=COLORS['accent'])
    
    human_steps = ['View Reasoning', 'Check Sources', 'Validate Decision', 'Add Comments', 'Submit Action']
    for i, step in enumerate(human_steps):
        y = 7.3 - i * 0.9
        box = FancyBboxPatch((9.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows
    ax.annotate('', xy=(5, 5.5), xytext=(4.5, 5.5), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(9.5, 5.5), xytext=(9, 5.5), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(2.5, 2.8), xytext=(7, 3.3),
               arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=2, connectionstyle="arc3,rad=0.3", linestyle='--'))
    ax.text(4.8, 2.4, 'Feedback Loop', ha='center', va='center', fontsize=9, style='italic', color=COLORS['danger'])
    
    ax.text(7, 1.8, '10 HITL Decision Points', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['dark'])
    hitl_left = ['#1 Research Plan', '#2 Search String', '#3 Screening', '#4 Full-text', '#5 Themes']
    hitl_right = ['#6 Article Structure', '#7 Citations', '#8 Language', '#9 Figures', '#10 Final']
    for i, (left, right) in enumerate(zip(hitl_left, hitl_right)):
        y = 1.4 - i * 0.28
        ax.text(2.5, y, left, ha='left', va='center', fontsize=8, color=COLORS['dark'])
        ax.text(8.5, y, right, ha='left', va='center', fontsize=8, color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "hitl_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_security_architecture():
    """Create security architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Security Architecture', ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    layers = [
        ('Cloud Armor WAF', 8.2, COLORS['danger'], 'DDoS Protection  |  Rate Limiting  |  Geo Blocking'),
        ('TLS 1.3 + mTLS', 6.8, COLORS['warning'], 'Encryption in Transit  |  Certificate Pinning  |  HSTS'),
        ('Authentication', 5.4, COLORS['accent'], 'Firebase Auth  |  MFA (TOTP)  |  OAuth 2.0'),
        ('Authorization', 4.0, COLORS['primary'], 'RBAC  |  JWT Tokens  |  API Keys'),
        ('Data Security', 2.6, COLORS['secondary'], 'AES-256 at Rest  |  Key Management  |  Audit Logs'),
    ]
    
    for name, y, color, items in layers:
        box = FancyBboxPatch((0.5, y - 0.5), 13, 1.2, boxstyle="round,pad=0.02",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(0.8, y + 0.1, name, ha='left', va='center', fontsize=11, fontweight='bold', color=color)
        ax.text(13.2, y + 0.1, items, ha='right', va='center', fontsize=9, color=COLORS['dark'])
    
    ai_sec_box = FancyBboxPatch((4, 0.8), 6, 1.2, boxstyle="round,pad=0.02",
                                 facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(ai_sec_box)
    ax.text(7, 1.6, 'AI SECURITY', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['secondary'])
    ax.text(7, 1.1, 'PromptGuard  |  Injection Filter  |  Output Sanitize', ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "security_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_deployment_architecture():
    """Create deployment architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Deployment Architecture (Google Cloud Platform)', ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    ax.text(7, 8.9, 'Region: europe-west1 (Belgium) - GDPR Compliant', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['primary'])
    
    # Cloud Run
    run_box = FancyBboxPatch((0.5, 5), 4, 3.3, boxstyle="round,pad=0.03",
                              facecolor=COLORS['secondary'], alpha=0.15, edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(run_box)
    ax.text(2.5, 8.0, 'Cloud Run Services', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['secondary'])
    for i, name in enumerate(['API Gateway', 'Backend Service', 'Worker Service']):
        y = 7.2 - i * 0.8
        box = FancyBboxPatch((0.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Data Services
    data_box = FancyBboxPatch((5, 5), 4, 3.3, boxstyle="round,pad=0.03",
                               facecolor=COLORS['warning'], alpha=0.15, edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(data_box)
    ax.text(7, 8.0, 'Data Services', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['warning'])
    for i, name in enumerate(['Firestore', 'Cloud Storage', 'Memorystore']):
        y = 7.2 - i * 0.8
        box = FancyBboxPatch((5.3, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(7, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # AI Services
    ai_box = FancyBboxPatch((9.5, 5), 4, 3.3, boxstyle="round,pad=0.03",
                             facecolor=COLORS['accent'], alpha=0.15, edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(11.5, 8.0, 'AI Services', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['accent'])
    for i, name in enumerate(['Vertex AI', 'ChromaDB', 'Embeddings']):
        y = 7.2 - i * 0.8
        box = FancyBboxPatch((9.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.5, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # DevOps, Monitoring, Security
    boxes_bottom = [
        (0.5, 'DevOps & CI/CD', COLORS['danger'], ['Cloud Build', 'Artifact Registry', 'Terraform']),
        (5, 'Observability', '#6B7280', ['Cloud Monitoring', 'Cloud Logging', 'Cloud Trace']),
        (9.5, 'Security', COLORS['primary'], ['Cloud Armor', 'Secret Manager', 'IAM']),
    ]
    for x, title, color, items in boxes_bottom:
        box = FancyBboxPatch((x, 1.5), 4, 3, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x + 2, 4.2, title, ha='center', va='center', fontsize=11, fontweight='bold', color=color)
        for i, name in enumerate(items):
            y = 3.5 - i * 0.7
            item_box = FancyBboxPatch((x + 0.3, y - 0.25), 3.4, 0.5, boxstyle="round,pad=0.02",
                                       facecolor='white', edgecolor=color, linewidth=1)
            ax.add_patch(item_box)
            ax.text(x + 2, y, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    ax.text(7, 0.8, 'Auto-scaling: 0-100 instances  |  SLA: 99.9%  |  Multi-zone deployment', 
            ha='center', va='center', fontsize=10, style='italic', color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "deployment_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_data_flow():
    """Create data flow diagram"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(8, 9.5, 'Data Flow Architecture', ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Sources
    source_box = FancyBboxPatch((0.5, 7), 4.5, 2, boxstyle="round,pad=0.03",
                                 facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(source_box)
    ax.text(2.75, 8.7, 'INPUT SOURCES', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['primary'])
    for i, name in enumerate(['PDF Docs', 'Research Plan', 'User Input']):
        x = 0.9 + i * 1.4
        box = FancyBboxPatch((x, 7.2), 1.2, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.6, 7.6, name, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Processing
    proc_box = FancyBboxPatch((5.5, 7), 5, 2, boxstyle="round,pad=0.03",
                               facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(proc_box)
    ax.text(8, 8.7, 'PROCESSING LAYER', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['secondary'])
    for i, name in enumerate(['Parse', 'Chunk', 'Embed', 'Index']):
        x = 5.8 + i * 1.15
        box = FancyBboxPatch((x, 7.2), 1.0, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.5, 7.6, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Output
    out_box = FancyBboxPatch((11, 7), 4.5, 2, boxstyle="round,pad=0.03",
                              facecolor=COLORS['danger'], alpha=0.2, edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(out_box)
    ax.text(13.25, 8.7, 'OUTPUT', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['danger'])
    for i, name in enumerate(['Article', 'PDF/DOCX', 'PRISMA']):
        x = 11.4 + i * 1.4
        box = FancyBboxPatch((x, 7.2), 1.2, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['danger'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.6, 7.6, name, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Storage
    storage_box = FancyBboxPatch((0.5, 3.5), 6, 2.5, boxstyle="round,pad=0.03",
                                  facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(storage_box)
    ax.text(3.5, 5.7, 'STORAGE LAYER', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['warning'])
    for i, (name, desc) in enumerate([('Firestore', 'Metadata'), ('ChromaDB', 'Vectors'), ('Cloud Storage', 'Files')]):
        x = 0.9 + i * 1.8
        box = FancyBboxPatch((x, 3.7), 1.6, 1.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.8, 4.7, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 0.8, 4.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # AI Generation
    ai_box = FancyBboxPatch((7, 3.5), 5.5, 2.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(9.75, 5.7, 'AI GENERATION', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['accent'])
    for i, (name, desc) in enumerate([('RAG Retrieval', ''), ('LLM Generate', 'Gemini 2.5'), ('Validate', '')]):
        x = 7.3 + i * 1.7
        box = FancyBboxPatch((x, 3.7), 1.5, 1.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.75, 4.7, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        if desc:
            ax.text(x + 0.75, 4.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # HITL
    hitl_box = FancyBboxPatch((13, 3.5), 2.5, 2.5, boxstyle="round,pad=0.03",
                               facecolor=COLORS['warning'], alpha=0.3, edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(hitl_box)
    ax.text(14.25, 5.7, 'HITL', ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['warning'])
    ax.text(14.25, 4.5, 'Human\nReview', ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows
    ax.annotate('', xy=(5.5, 8), xytext=(5.0, 8), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(11, 8), xytext=(10.5, 8), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(3.5, 6.0), xytext=(6.5, 7.0), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5, connectionstyle="arc3,rad=0.3"))
    ax.annotate('', xy=(7, 4.7), xytext=(6.5, 4.7), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    ax.annotate('', xy=(13, 4.7), xytext=(12.5, 4.7), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    ax.annotate('', xy=(14.25, 6.0), xytext=(14.25, 7.0), arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    ax.text(8, 2.5, 'Continuous Feedback Loop', ha='center', va='center', fontsize=12, fontweight='bold', color=COLORS['primary'])
    ax.annotate('', xy=(2, 2.8), xytext=(14, 2.8), arrowprops=dict(arrowstyle='<->', color=COLORS['primary'], lw=2))
    ax.text(8, 2.0, 'HITL Review & Validation at each phase', ha='center', va='center', fontsize=10, style='italic', color=COLORS['primary'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "data_flow.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


# ============================================================================
# PDF GENERATION
# ============================================================================

def create_architecture_pdf(images):
    """Create the English architecture PDF - User Journey first"""
    
    filepath = OUTPUT_DIR / "ResearchFlow_Architecture_EN.pdf"
    
    doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=28, alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['primary']), spaceAfter=20, fontName=UNICODE_FONT_BOLD)
    
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['dark']), spaceAfter=10, fontName=UNICODE_FONT)
    
    heading1_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=18, alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['primary']), spaceBefore=20, spaceAfter=12, fontName=UNICODE_FONT_BOLD)
    
    heading2_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=14, alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['secondary']), spaceBefore=15, spaceAfter=8, fontName=UNICODE_FONT_BOLD)
    
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY,
        textColor=colors.HexColor(COLORS['dark']), spaceAfter=8, leading=14, fontName=UNICODE_FONT)
    
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['dark']), spaceAfter=4, leftIndent=15, bulletIndent=5, fontName=UNICODE_FONT)
    
    story = []
    
    # ==================== PAGE 1: Title Page ====================
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("ResearchFlow", title_style))
    story.append(Paragraph("Technical Architecture Documentation", subtitle_style))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("AI-Powered Scoping Review Platform",
                          ParagraphStyle('Sub2', fontSize=14, alignment=TA_CENTER,
                                        textColor=colors.HexColor(COLORS['secondary']), fontName=UNICODE_FONT)))
    story.append(Spacer(1, 3*cm))
    
    toc_data = [
        ['Contents', 'Page'],
        ['1. User Experience', '2'],
        ['2. System Overview', '3'],
        ['3. High-Level Architecture', '4'],
        ['4. Multi-Agent System', '5'],
        ['5. Memory Architecture', '6'],
        ['6. RAG System', '7'],
        ['7. Workflow Pipeline', '8'],
        ['8. HITL Architecture', '9'],
        ['9. Data Flow', '10'],
        ['10. Security Architecture', '11'],
        ['11. Deployment Infrastructure', '12'],
    ]
    toc_table = Table(toc_data, colWidths=[12*cm, 3*cm])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), UNICODE_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), UNICODE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['light'])),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(f"Version 2.3 | April 2026",
                          ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, textColor=colors.gray, fontName=UNICODE_FONT)))
    story.append(PageBreak())
    
    # ==================== PAGE 2: User Experience (FIRST!) ====================
    story.append(Paragraph("1. User Experience", heading1_style))
    story.append(Paragraph(
        "The diagram below shows the complete user journey from login to final article export. "
        "A typical scoping review can be completed in 4-6 weeks instead of the traditional 6-12 months.",
        body_style
    ))
    if 'user_journey' in images:
        story.append(Image(images['user_journey'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("User Journey Steps:", heading2_style))
    journey_steps = [
        "<b>1. Login:</b> Authenticate via Google/Email, optional MFA",
        "<b>2. Create Project:</b> New scoping review project with name and description",
        "<b>3. Input Plan:</b> Define research questions, PICO, inclusion criteria",
        "<b>4. Generate Strings:</b> AI generates Boolean search strings, user validates",
        "<b>5. Import Results:</b> Upload .ris/.csv from WoS/Scopus/PubMed",
        "<b>6. Screening:</b> AI categorizes abstracts, user confirms/rejects",
        "<b>7. Full-text:</b> Upload PDFs, system parses and indexes",
        "<b>8. Analysis:</b> AI identifies themes and gaps, user validates",
        "<b>9. Writing:</b> AI writes article sections, user reviews/edits",
        "<b>10. Export:</b> Download PDF/DOCX with figures and references",
    ]
    for j in journey_steps:
        story.append(Paragraph(f"• {j}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 3: System Overview ====================
    story.append(Paragraph("2. System Overview", heading1_style))
    story.append(Paragraph(
        "ResearchFlow is an advanced platform for automated scoping review article writing, "
        "based on a multi-agent architecture with AI support. The system enables the complete workflow "
        "from defining the research question to a publication-ready article.",
        body_style
    ))
    
    story.append(Paragraph("2.1 Key Technologies", heading2_style))
    tech_data = [
        ['Component', 'Technology', 'Purpose'],
        ['Backend', 'Python 3.11+ / FastAPI', 'REST API, Async processing'],
        ['Frontend', 'Next.js 14 / React', 'Server-side rendering, UX'],
        ['LLM', 'Vertex AI Gemini 2.5', 'Text generation, reasoning'],
        ['Vector DB', 'ChromaDB', 'Semantic search, embeddings'],
        ['Database', 'Firestore', 'Document storage, real-time'],
        ['Cache', 'Memorystore Redis', 'Session, rate limiting'],
        ['Storage', 'Cloud Storage', 'PDFs, exports, assets'],
        ['Auth', 'Firebase Auth', 'OAuth, MFA, JWT'],
    ]
    tech_table = Table(tech_data, colWidths=[3.5*cm, 4.5*cm, 7*cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), UNICODE_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), UNICODE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['light'])),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tech_table)
    
    story.append(Paragraph("2.2 Architectural Principles", heading2_style))
    principles = [
        "<b>Cloud-Native:</b> Built for GCP with auto-scaling and managed services",
        "<b>Event-Driven:</b> Asynchronous processing with Pub/Sub for long-running tasks",
        "<b>Microservices:</b> Separate services for backend, workers, AI processing",
        "<b>HITL-First:</b> Human leads AI, 10 control points in workflow",
        "<b>Security-by-Design:</b> GDPR compliant, EU data residency, encryption",
    ]
    for p in principles:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 4: High-Level Architecture ====================
    story.append(Paragraph("3. High-Level System Architecture", heading1_style))
    story.append(Paragraph(
        "The diagram below shows the layered architecture from user interface to data layer, "
        "with integrated security and observability components.",
        body_style
    ))
    if 'high_level' in images:
        story.append(Image(images['high_level'], width=16*cm, height=12*cm))
    
    story.append(Paragraph("Key Components:", heading2_style))
    components = [
        "<b>User Interface Layer:</b> Next.js 14 frontend with chatbot interface, HITL dashboard",
        "<b>API Gateway:</b> Cloud Run with authentication, rate limiting, load balancing",
        "<b>Backend Services:</b> FastAPI microservices for orchestration, RAG, agents",
        "<b>Data Layer:</b> Firestore for metadata, ChromaDB for vectors, Cloud Storage for files",
        "<b>Security Layer:</b> TLS 1.3, Cloud Armor WAF, PromptGuard for AI security",
    ]
    for c in components:
        story.append(Paragraph(f"• {c}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 5: Multi-Agent Architecture ====================
    story.append(Paragraph("4. Multi-Agent System", heading1_style))
    story.append(Paragraph(
        "ResearchFlow uses a multi-agent architecture where specialized agents handle "
        "different phases of the scoping review process. A central orchestrator coordinates agent activities.",
        body_style
    ))
    if 'multi_agent' in images:
        story.append(Image(images['multi_agent'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Agents and Their Tasks:", heading2_style))
    agents_desc = [
        "<b>Research Plan Agent:</b> Parses research questions, defines PICO/PCC criteria",
        "<b>Search String Agent:</b> Generates Boolean search strings for WoS, Scopus, PubMed",
        "<b>Screening Agent:</b> Analyzes abstracts, categorizes Include/Exclude/Uncertain",
        "<b>Analysis Agent:</b> Identifies gaps, extracts themes, recognizes patterns",
        "<b>Article Generator:</b> Writes article sections with inline citations in academic style",
        "<b>Visualization Agent:</b> Generates PRISMA diagrams, Evidence Gap Maps",
    ]
    for a in agents_desc:
        story.append(Paragraph(f"• {a}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 6: Memory Architecture ====================
    story.append(Paragraph("5. Three-Tier Memory Architecture", heading1_style))
    story.append(Paragraph(
        "The system uses a three-tier memory architecture for optimal context and state management "
        "during processing. Each tier has a specific role and technology.",
        body_style
    ))
    if 'memory' in images:
        story.append(Image(images['memory'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Memory Tiers:", heading2_style))
    memory_desc = [
        "<b>Working Memory (Redis):</b> Current task context, conversation history, intermediate results, HITL queue. TTL: minutes to hours.",
        "<b>Short-Term Memory (ChromaDB):</b> Document vector embeddings, reasoning traces, screening decisions, search results. TTL: project duration.",
        "<b>Long-Term Memory (Firestore + Cloud Storage):</b> Complete project history, user profiles, document archive, generated articles. TTL: permanent.",
    ]
    for m in memory_desc:
        story.append(Paragraph(f"• {m}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 7: RAG Architecture ====================
    story.append(Paragraph("6. RAG (Retrieval-Augmented Generation) Architecture", heading1_style))
    story.append(Paragraph(
        "The RAG system enables grounding of LLM responses in source documents. "
        "It consists of an ingestion pipeline and a retrieval pipeline with hybrid search.",
        body_style
    ))
    if 'rag' in images:
        story.append(Image(images['rag'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Technical Details:", heading2_style))
    rag_details = [
        "<b>Ingestion:</b> PyMuPDF + markitdown for PDF parsing, chunking 1024 tokens with 50 overlap",
        "<b>Embedding:</b> text-embedding-004 model, 768-dimensional vectors",
        "<b>Indexing:</b> ChromaDB with HNSW algorithm for fast similarity search",
        "<b>Retrieval:</b> Hybrid search (BM25 + semantic), RRF fusion, top-k=10",
        "<b>Generation:</b> Gemini 2.5 Pro with grounded prompting and citation formatting",
    ]
    for r in rag_details:
        story.append(Paragraph(f"• {r}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 8: Workflow Pipeline ====================
    story.append(Paragraph("7. 8-Phase Workflow Pipeline", heading1_style))
    story.append(Paragraph(
        "The scoping review process is divided into 8 sequential phases, each with specific tasks "
        "and HITL control points. Each phase has clearly defined inputs and outputs.",
        body_style
    ))
    if 'workflow' in images:
        story.append(Image(images['workflow'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Phases and HITL Points:", heading2_style))
    workflow_desc = [
        "1. <b>Research Plan:</b> Define questions, PICO criteria - HITL #1 validation",
        "2. <b>Search Strings:</b> Boolean expression generation - HITL #2 syntax review",
        "3. <b>Abstract Screening:</b> AI categorization - HITL #3 decisions",
        "4. <b>Full-text ID:</b> DOI resolution, PDF retrieval",
        "5. <b>Full-text Ingestion:</b> Parsing, chunking - HITL #4 quality check",
        "6. <b>Gap Analysis:</b> Gap identification, themes - HITL #5 theme validation",
        "7. <b>Article Generation:</b> Section writing - HITL #6-7 content review",
        "8. <b>Export:</b> PDF/DOCX, visualizations - HITL #8-10 final review",
    ]
    for w in workflow_desc:
        story.append(Paragraph(f"• {w}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 9: HITL Architecture ====================
    story.append(Paragraph("8. Human-in-the-Loop (HITL) Architecture", heading1_style))
    story.append(Paragraph(
        "The HITL architecture ensures that humans lead the AI tool, not the other way around. "
        "10 control points enable complete oversight over every critical decision in the process.",
        body_style
    ))
    if 'hitl' in images:
        story.append(Image(images['hitl'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("HITL Principles:", heading2_style))
    hitl_principles = [
        "<b>Transparency:</b> Every AI decision has visible reasoning traces",
        "<b>Interactivity:</b> User can approve/reject/modify every decision",
        "<b>Feedback Loop:</b> Rejected decisions return to the agent with instructions",
        "<b>Audit Trail:</b> All decisions are logged for reproducibility",
        "<b>Batch Processing:</b> Ability to review multiple decisions at once",
    ]
    for h in hitl_principles:
        story.append(Paragraph(f"• {h}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 10: Data Flow ====================
    story.append(Paragraph("9. Data Flow", heading1_style))
    story.append(Paragraph(
        "Data flows through the system from input sources (PDF, research plan) through processing "
        "and storage to final outputs (article, visualizations).",
        body_style
    ))
    if 'data_flow' in images:
        story.append(Image(images['data_flow'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Data Flows:", heading2_style))
    data_flows = [
        "<b>Input:</b> PDF documents, research plan, user inputs - Processing Layer",
        "<b>Processing:</b> Parse - Chunk - Embed - Index cycle with validation",
        "<b>Storage:</b> Firestore (metadata), ChromaDB (vectors), Cloud Storage (files)",
        "<b>AI Generation:</b> RAG retrieval - LLM generate - Validate - Output",
        "<b>Output:</b> Article sections, citations, figures, PDF/DOCX, PRISMA diagram",
    ]
    for d in data_flows:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 11: Security Architecture ====================
    story.append(Paragraph("10. Security Architecture", heading1_style))
    story.append(Paragraph(
        "Security is built into all layers of the system - from network protection to AI-specific "
        "security against prompt injection attacks.",
        body_style
    ))
    if 'security' in images:
        story.append(Image(images['security'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Security Layers:", heading2_style))
    security_layers = [
        "<b>Perimeter:</b> Cloud Armor WAF, DDoS protection, geo-blocking",
        "<b>Transport:</b> TLS 1.3, mTLS for internal services, HSTS",
        "<b>Authentication:</b> Firebase Auth with MFA (TOTP), OAuth 2.0 (Google, Microsoft)",
        "<b>Authorization:</b> RBAC (Owner/Editor/Reviewer/Viewer), JWT tokens",
        "<b>Data:</b> AES-256 encryption at rest, Google-managed keys",
        "<b>AI Security:</b> EnhancedPromptGuard (regex + LLM-based injection detection)",
        "<b>Audit:</b> Complete logging to Firestore + BigQuery for compliance",
    ]
    for s in security_layers:
        story.append(Paragraph(f"• {s}", bullet_style))
    story.append(PageBreak())
    
    # ==================== PAGE 12: Deployment ====================
    story.append(Paragraph("11. Deployment Infrastructure", heading1_style))
    story.append(Paragraph(
        "ResearchFlow is deployed on Google Cloud Platform in the EU region (europe-west1) "
        "for GDPR compliance. It uses managed services with auto-scaling.",
        body_style
    ))
    if 'deployment' in images:
        story.append(Image(images['deployment'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Infrastructure Specifications:", heading2_style))
    infra_specs = [
        "<b>Region:</b> europe-west1 (Belgium) - GDPR compliant, low latency for EU",
        "<b>Compute:</b> Cloud Run with auto-scaling 0-100 instances",
        "<b>CI/CD:</b> Cloud Build with Terraform for infrastructure-as-code",
        "<b>Monitoring:</b> Cloud Monitoring, Logging, Trace for full observability",
        "<b>SLA:</b> Target 99.9% availability with multi-zone deployment",
    ]
    for i in infra_specs:
        story.append(Paragraph(f"• {i}", bullet_style))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Result: Publication-ready scoping review article with inline citations, "
        "PRISMA diagram and Evidence Gap Map in 4-6 weeks.",
        ParagraphStyle('Highlight', fontSize=11, alignment=TA_CENTER, 
                      textColor=colors.HexColor(COLORS['accent']), fontName=UNICODE_FONT_BOLD)
    ))
    
    doc.build(story)
    return str(filepath)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("ResearchFlow Architecture (English) - User Journey First")
    print("=" * 60)
    
    images = {}
    
    print("\n[1/10] Creating user journey (first chapter)...")
    images['user_journey'] = create_user_journey()
    print(f"       Done")
    
    print("\n[2/10] Creating high-level architecture...")
    images['high_level'] = create_high_level_architecture()
    print(f"       Done")
    
    print("\n[3/10] Creating multi-agent architecture...")
    images['multi_agent'] = create_multi_agent_architecture()
    print(f"       Done")
    
    print("\n[4/10] Creating memory architecture...")
    images['memory'] = create_memory_architecture()
    print(f"       Done")
    
    print("\n[5/10] Creating RAG architecture...")
    images['rag'] = create_rag_architecture()
    print(f"       Done")
    
    print("\n[6/10] Creating workflow pipeline...")
    images['workflow'] = create_workflow_pipeline()
    print(f"       Done")
    
    print("\n[7/10] Creating HITL architecture...")
    images['hitl'] = create_hitl_architecture()
    print(f"       Done")
    
    print("\n[8/10] Creating data flow diagram...")
    images['data_flow'] = create_data_flow()
    print(f"       Done")
    
    print("\n[9/10] Creating security architecture...")
    images['security'] = create_security_architecture()
    print(f"       Done")
    
    print("\n[10/10] Creating deployment architecture...")
    images['deployment'] = create_deployment_architecture()
    print(f"       Done")
    
    print("\n" + "=" * 60)
    print("Generating English PDF (A4, 12 pages)...")
    pdf_path = create_architecture_pdf(images)
    print(f"PDF saved to: {pdf_path}")
    print("=" * 60)
    
    return pdf_path


if __name__ == "__main__":
    main()
