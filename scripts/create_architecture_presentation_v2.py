#!/usr/bin/env python3
"""
ResearchFlow - Technical Architecture Presentation
Detailed architecture documentation with visualizations
Minimum 10 A4 pages - FIXED VERSION with proper Unicode support
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
from matplotlib.patches import ConnectionPatch, Arc
import matplotlib.patheffects as path_effects
import numpy as np
from datetime import datetime

# Configure matplotlib to use DejaVu Sans (has full Unicode support)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem, FrameBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Unicode fonts for Slovenian characters (š, ž, č, etc.)
UNICODE_FONT = 'SegoeUI'
UNICODE_FONT_BOLD = 'SegoeUIBold'

pdfmetrics.registerFont(TTFont(UNICODE_FONT, 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont(UNICODE_FONT_BOLD, 'C:/Windows/Fonts/segoeuib.ttf'))
print(f"Registered fonts: {UNICODE_FONT}, {UNICODE_FONT_BOLD}")

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "architecture_presentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color palette
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

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))


# ============================================================================
# VISUALIZATION FUNCTIONS - OPTIMIZED LAYOUTS
# ============================================================================

def create_high_level_architecture():
    """Create high-level system architecture diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    # Title
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
    
    # Row 1: Core Services
    services_row1 = ['Orchestration', 'RAG Service', 'Agent Cluster', 'HITL Manager']
    for i, comp in enumerate(services_row1):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 5.4), 2.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 5.75, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Row 2: Specialized Services  
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
    
    data_components = [
        ('Firestore', 'Metadata'),
        ('ChromaDB', 'Vectors'),
        ('Cloud Storage', 'Files'),
        ('Redis', 'Cache')
    ]
    for i, (name, desc) in enumerate(data_components):
        x = 1.8 + i * 2.9
        box = FancyBboxPatch((x, 1.7), 2.4, 1.3, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.2, 2.55, name, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.2, 2.1, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # SECURITY LAYER (bottom)
    sec_box = FancyBboxPatch((1, 0.3), 12, 0.9, boxstyle="round,pad=0.03",
                              facecolor=COLORS['red_light'], edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(sec_box)
    ax.text(7, 0.75, 'SECURITY: TLS 1.3  |  Cloud Armor  |  PromptGuard  |  Audit Logs  |  Monitoring', 
            ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['danger'])
    
    # Vertical arrows between layers (centered, non-overlapping)
    arrow_positions = [3.5, 7, 10.5]
    for xpos in arrow_positions:
        # User to API
        ax.annotate('', xy=(xpos, 8.8), xytext=(xpos, 8.4),
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
        # API to Backend
        ax.annotate('', xy=(xpos, 7.0), xytext=(xpos, 6.6),
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
        # Backend to Data
        ax.annotate('', xy=(xpos, 4.0), xytext=(xpos, 3.6),
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "high_level_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_multi_agent_architecture():
    """Create multi-agent system architecture diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7.5, 10.5, 'Multi-Agent System Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # ORCHESTRATOR (center top)
    orch_box = FancyBboxPatch((5.5, 8.5), 4, 1.5, boxstyle="round,pad=0.05",
                               facecolor=COLORS['primary'], edgecolor=COLORS['dark'], linewidth=2)
    ax.add_patch(orch_box)
    ax.text(7.5, 9.4, 'ORCHESTRATOR', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    ax.text(7.5, 8.9, 'Workflow Coordination', ha='center', va='center', 
            fontsize=10, color='white')
    
    # First row agents - evenly spaced
    agents_row1 = [
        (2, 5.5, 'Research Plan\nAgent', COLORS['secondary'], 
         'Parse questions\nDefine PICO/PCC'),
        (5.5, 5.5, 'Search String\nAgent', COLORS['accent'],
         'Boolean queries\nMulti-database'),
        (9, 5.5, 'Screening\nAgent', COLORS['warning'],
         'Abstract analysis\nInclude/Exclude'),
        (12.5, 5.5, 'Analysis\nAgent', COLORS['danger'],
         'Gap detection\nTheme extraction'),
    ]
    
    for x, y, name, color, desc in agents_row1:
        # Agent box
        box = FancyBboxPatch((x - 1.4, y - 1.2), 2.8, 2.4, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Agent header
        header = FancyBboxPatch((x - 1.3, y + 0.6), 2.6, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x, y + 0.85, name, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        
        # Agent description
        ax.text(x, y - 0.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        
        # Arrow from orchestrator - curved nicely
        ax.annotate('', xy=(x, y + 1.2), xytext=(7.5, 8.5),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2, 
                                  connectionstyle=f"arc3,rad={0.15 if x < 7.5 else -0.15 if x > 7.5 else 0}"))
    
    # Second row of agents
    agents_row2 = [
        (3.5, 1.8, 'Article\nGenerator', COLORS['secondary'],
         'Section writing\nCitation format'),
        (7.5, 1.8, 'Export\nAgent', COLORS['accent'],
         'PDF/DOCX\nFigure embed'),
        (11.5, 1.8, 'Visualization\nAgent', COLORS['warning'],
         'PRISMA diagrams\nEvidence maps'),
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
    
    # Connection lines between rows (vertical dashed)
    for x in [3.5, 7.5, 11.5]:
        ax.plot([x, x], [3.0, 4.3], color=COLORS['dark'], linestyle=':', linewidth=1.5, alpha=0.6)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "multi_agent_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_memory_architecture():
    """Create 3-tier memory architecture diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, '3-Tier Memory Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Working Memory (top)
    wm_box = FancyBboxPatch((0.5, 6.3), 13, 2.7, boxstyle="round,pad=0.03",
                             facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=3)
    ax.add_patch(wm_box)
    ax.text(7, 8.7, 'WORKING MEMORY (Redis)', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['accent'])
    
    wm_items = [
        ('Task Context', 'Agent state'),
        ('Conversation', 'User queries'),
        ('Temp Results', 'Partial data'),
        ('HITL Queue', 'Decisions'),
    ]
    for i, (title, desc) in enumerate(wm_items):
        x = 1.2 + i * 3.1
        box = FancyBboxPatch((x, 6.5), 2.7, 1.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.35, 7.8, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.35, 7.2, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Short-Term Memory (middle)
    stm_box = FancyBboxPatch((0.5, 3.2), 13, 2.7, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=3)
    ax.add_patch(stm_box)
    ax.text(7, 5.6, 'SHORT-TERM MEMORY (ChromaDB)', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    stm_items = [
        ('Doc Chunks', '768-dim vectors'),
        ('Reasoning', 'Decision logs'),
        ('Screening', 'Inc/Exc/Unc'),
        ('Search Cache', 'Query results'),
    ]
    for i, (title, desc) in enumerate(stm_items):
        x = 1.2 + i * 3.1
        box = FancyBboxPatch((x, 3.4), 2.7, 1.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.35, 4.7, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.35, 4.1, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Long-Term Memory (bottom)
    ltm_box = FancyBboxPatch((0.5, 0.3), 13, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=3)
    ax.add_patch(ltm_box)
    ax.text(7, 2.5, 'LONG-TERM MEMORY (Firestore + Cloud Storage)', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['primary'])
    
    ltm_items = [
        ('Project State', 'Full history'),
        ('User Profiles', 'Preferences'),
        ('Doc Archive', 'PDFs, text'),
        ('Articles', 'Final outputs'),
    ]
    for i, (title, desc) in enumerate(ltm_items):
        x = 1.2 + i * 3.1
        box = FancyBboxPatch((x, 0.5), 2.7, 1.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.35, 1.6, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.35, 1.1, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Arrows between tiers (on the sides, not overlapping)
    # Left side arrows
    ax.annotate('', xy=(0.7, 6.3), xytext=(0.7, 5.9), 
                arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(0.7, 3.2), xytext=(0.7, 2.8), 
                arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    
    # Right side arrows
    ax.annotate('', xy=(13.3, 6.3), xytext=(13.3, 5.9), 
                arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(13.3, 3.2), xytext=(13.3, 2.8), 
                arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    
    # Labels
    ax.text(0.3, 6.1, 'Promote', ha='center', va='center', fontsize=8, rotation=90, color=COLORS['dark'])
    ax.text(0.3, 3.0, 'Persist', ha='center', va='center', fontsize=8, rotation=90, color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "memory_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_rag_architecture():
    """Create RAG system architecture diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7.5, 10.5, 'RAG (Retrieval-Augmented Generation) Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # INGESTION PIPELINE (left side)
    ing_box = FancyBboxPatch((0.5, 3.5), 4, 6.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(ing_box)
    ax.text(2.5, 9.7, 'INGESTION', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['primary'])
    
    ing_steps = [
        ('1. PDF Upload', 8.8),
        ('2. Text Extract', 7.8),
        ('3. Chunking', 6.8),
        ('4. Embedding', 5.8),
        ('5. Index Store', 4.8),
    ]
    for step, y in ing_steps:
        box = FancyBboxPatch((0.8, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows between ingestion steps
    for i in range(len(ing_steps) - 1):
        ax.annotate('', xy=(2.5, ing_steps[i+1][1] + 0.4), xytext=(2.5, ing_steps[i][1] - 0.4),
                   arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=1.5))
    
    # Details under ingestion
    ax.text(2.5, 4.0, 'PyMuPDF\n1024 tokens\n50 overlap', 
            ha='center', va='center', fontsize=8, style='italic', color=COLORS['dark'])
    
    # VECTOR DATABASE (center)
    vdb_box = FancyBboxPatch((5, 3.5), 5, 6.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(vdb_box)
    ax.text(7.5, 9.7, 'VECTOR DATABASE', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    # ChromaDB icon
    chroma_box = FancyBboxPatch((5.8, 7.8), 3.4, 1.5, boxstyle="round,pad=0.03",
                                 facecolor=COLORS['secondary'], edgecolor='white', linewidth=2)
    ax.add_patch(chroma_box)
    ax.text(7.5, 8.7, 'ChromaDB', ha='center', va='center', fontsize=13, fontweight='bold', color='white')
    ax.text(7.5, 8.2, '768-dim embeddings', ha='center', va='center', fontsize=9, color='white')
    
    # Index types
    indices = [('Document Index', 6.8), ('Reasoning Index', 5.8), ('Metadata Index', 4.8)]
    for name, y in indices:
        box = FancyBboxPatch((5.5, y - 0.35), 4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(7.5, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # RETRIEVAL PIPELINE (right side)
    ret_box = FancyBboxPatch((10.5, 3.5), 4, 6.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ret_box)
    ax.text(12.5, 9.7, 'RETRIEVAL', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['accent'])
    
    ret_steps = [
        ('1. Query Embed', 8.8),
        ('2. Hybrid Search', 7.8),
        ('3. Re-ranking', 6.8),
        ('4. Context Build', 5.8),
        ('5. LLM Generate', 4.8),
    ]
    for step, y in ret_steps:
        box = FancyBboxPatch((10.8, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(12.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows between retrieval steps
    for i in range(len(ret_steps) - 1):
        ax.annotate('', xy=(12.5, ret_steps[i+1][1] + 0.4), xytext=(12.5, ret_steps[i][1] - 0.4),
                   arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=1.5))
    
    # Details
    ax.text(12.5, 4.0, 'BM25+Semantic\nTop-k: 10\nGemini 2.5', 
            ha='center', va='center', fontsize=8, style='italic', color=COLORS['dark'])
    
    # Connecting arrows (horizontal, outside boxes)
    ax.annotate('', xy=(5, 6.5), xytext=(4.5, 6.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(10.5, 6.5), xytext=(10, 6.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Bottom: Output
    out_box = FancyBboxPatch((4, 0.5), 7, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(out_box)
    ax.text(7.5, 2.5, 'GENERATED OUTPUT', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['warning'])
    ax.text(7.5, 1.5, 'Grounded in sources  |  Inline citations  |  Reasoning traces', 
            ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrow to output
    ax.annotate('', xy=(7.5, 3.0), xytext=(12.5, 4.4),
               arrowprops=dict(arrowstyle='->', color=COLORS['warning'], lw=2, connectionstyle="arc3,rad=-0.2"))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "rag_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_workflow_pipeline():
    """Create detailed 8-phase workflow pipeline - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(8, 9.5, '8-Phase Scoping Review Workflow', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    phases = [
        ('Phase 1', 'Research Plan', COLORS['primary'], 
         'Define questions\nSet PICO criteria', 'HITL #1'),
        ('Phase 2', 'Search Strings', COLORS['primary'],
         'Boolean queries\nWoS/Scopus/PubMed', 'HITL #2'),
        ('Phase 3', 'Abstract Screen', COLORS['secondary'],
         'AI categorization\nInc/Exc/Uncertain', 'HITL #3'),
        ('Phase 4', 'Full-text ID', COLORS['secondary'],
         'DOI resolution\nPDF retrieval', ''),
    ]
    
    phases2 = [
        ('Phase 5', 'FT Ingestion', COLORS['accent'],
         'PDF parsing\nVector embedding', 'HITL #4'),
        ('Phase 6', 'Gap Analysis', COLORS['accent'],
         'Theme extraction\nPattern analysis', 'HITL #5'),
        ('Phase 7', 'Article Gen', COLORS['warning'],
         'Section writing\nCitation format', 'HITL #6-7'),
        ('Phase 8', 'Export & Viz', COLORS['danger'],
         'PDF/DOCX\nPRISMA diagram', 'HITL #8-10'),
    ]
    
    # Draw first row (phases 1-4)
    for i, (num, name, color, tasks, hitl) in enumerate(phases):
        x = 0.8 + i * 3.8
        y = 6.5
        
        # Main phase box
        box = FancyBboxPatch((x, y - 1), 3.3, 2.8, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Phase header
        header = FancyBboxPatch((x + 0.1, y + 1.2), 3.1, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x + 1.65, y + 1.45, f'{num}: {name}', ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # Tasks
        ax.text(x + 1.65, y + 0.3, tasks, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        
        # HITL indicator
        if hitl:
            ax.text(x + 1.65, y - 0.7, hitl, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1, pad=0.2))
        
        # Arrow to next
        if i < 3:
            ax.annotate('', xy=(x + 4.0, y + 0.5), xytext=(x + 3.4, y + 0.5),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Draw second row (phases 5-8)
    for i, (num, name, color, tasks, hitl) in enumerate(phases2):
        x = 0.8 + i * 3.8
        y = 2.5
        
        box = FancyBboxPatch((x, y - 1), 3.3, 2.8, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        header = FancyBboxPatch((x + 0.1, y + 1.2), 3.1, 0.5, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x + 1.65, y + 1.45, f'{num}: {name}', ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        ax.text(x + 1.65, y + 0.3, tasks, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        
        if hitl:
            ax.text(x + 1.65, y - 0.7, hitl, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1, pad=0.2))
        
        if i < 3:
            ax.annotate('', xy=(x + 4.0, y + 0.5), xytext=(x + 3.4, y + 0.5),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Connecting arrow between rows (right side, curve down)
    ax.annotate('', xy=(15.0, 4.5), xytext=(15.0, 5.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.plot([14.5, 15.0], [5.5, 5.5], color=COLORS['dark'], lw=2)
    ax.plot([14.5, 15.0], [4.5, 4.5], color=COLORS['dark'], lw=2)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "workflow_pipeline.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_hitl_architecture():
    """Create Human-in-the-Loop architecture diagram - OPTIMIZED (no special chars)"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Human-in-the-Loop (HITL) Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # AI Processing (left)
    ai_box = FancyBboxPatch((0.5, 3), 4, 5.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['secondary'], alpha=0.15, edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(2.5, 8.2, 'AI PROCESSING', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    ai_steps = ['Document Analysis', 'Decision Generation', 'Confidence Score', 'Reasoning Trace', 'Action Queue']
    for i, step in enumerate(ai_steps):
        y = 7.3 - i * 0.9
        box = FancyBboxPatch((0.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # HITL Decision Point (center)
    hitl_box = FancyBboxPatch((5, 3.5), 4, 4.5, boxstyle="round,pad=0.05",
                               facecolor=COLORS['warning'], alpha=0.2, edgecolor=COLORS['warning'], linewidth=3)
    ax.add_patch(hitl_box)
    ax.text(7, 7.7, 'HITL DECISION', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['warning'])
    
    # Decision options (using text instead of symbols)
    decisions = [
        ('[OK] APPROVE', 6.8, COLORS['accent']),
        ('[X] REJECT', 5.9, COLORS['danger']),
        ('[EDIT] MODIFY', 5.0, COLORS['primary']),
        ('[...] DEFER', 4.1, '#6B7280'),
    ]
    for text, y, color in decisions:
        box = FancyBboxPatch((5.3, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor=color, alpha=0.25, edgecolor=color, linewidth=1)
        ax.add_patch(box)
        ax.text(7, y, text, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
    
    # Human Review (right)
    human_box = FancyBboxPatch((9.5, 3), 4, 5.5, boxstyle="round,pad=0.03",
                                facecolor=COLORS['accent'], alpha=0.15, edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(human_box)
    ax.text(11.5, 8.2, 'HUMAN REVIEW', ha='center', va='center',
            fontsize=13, fontweight='bold', color=COLORS['accent'])
    
    human_steps = ['View Reasoning', 'Check Sources', 'Validate Decision', 'Add Comments', 'Submit Action']
    for i, step in enumerate(human_steps):
        y = 7.3 - i * 0.9
        box = FancyBboxPatch((9.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.5, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows (positioned clearly)
    ax.annotate('', xy=(5, 5.5), xytext=(4.5, 5.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(9.5, 5.5), xytext=(9, 5.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Feedback loop (below, curved)
    ax.annotate('', xy=(2.5, 2.8), xytext=(7, 3.3),
               arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=2, 
                             connectionstyle="arc3,rad=0.3", linestyle='--'))
    ax.text(4.8, 2.4, 'Feedback Loop', ha='center', va='center', fontsize=9, 
            style='italic', color=COLORS['danger'])
    
    # 10 HITL points list (bottom, two columns)
    ax.text(7, 1.8, '10 HITL Decision Points', ha='center', va='center', 
            fontsize=11, fontweight='bold', color=COLORS['dark'])
    
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


def create_data_flow():
    """Create data flow diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(8, 9.5, 'Data Flow Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Sources (top left)
    source_box = FancyBboxPatch((0.5, 7), 4.5, 2, boxstyle="round,pad=0.03",
                                 facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(source_box)
    ax.text(2.75, 8.7, 'INPUT SOURCES', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['primary'])
    
    sources = ['PDF Docs', 'Research Plan', 'User Input']
    for i, name in enumerate(sources):
        x = 0.9 + i * 1.4
        box = FancyBboxPatch((x, 7.2), 1.2, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.6, 7.6, name, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Processing 
    proc_box = FancyBboxPatch((5.5, 7), 5, 2, boxstyle="round,pad=0.03",
                               facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(proc_box)
    ax.text(8, 8.7, 'PROCESSING LAYER', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['secondary'])
    
    proc_steps = ['Parse', 'Chunk', 'Embed', 'Index']
    for i, name in enumerate(proc_steps):
        x = 5.8 + i * 1.15
        box = FancyBboxPatch((x, 7.2), 1.0, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.5, 7.6, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Output (top right)
    out_box = FancyBboxPatch((11, 7), 4.5, 2, boxstyle="round,pad=0.03",
                              facecolor=COLORS['danger'], alpha=0.2, edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(out_box)
    ax.text(13.25, 8.7, 'OUTPUT', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['danger'])
    
    outputs = ['Article', 'PDF/DOCX', 'PRISMA']
    for i, name in enumerate(outputs):
        x = 11.4 + i * 1.4
        box = FancyBboxPatch((x, 7.2), 1.2, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['danger'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.6, 7.6, name, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Storage (middle)
    storage_box = FancyBboxPatch((0.5, 3.5), 6, 2.5, boxstyle="round,pad=0.03",
                                  facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(storage_box)
    ax.text(3.5, 5.7, 'STORAGE LAYER', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['warning'])
    
    storages = [('Firestore', 'Metadata'), ('ChromaDB', 'Vectors'), ('Cloud Storage', 'Files')]
    for i, (name, desc) in enumerate(storages):
        x = 0.9 + i * 1.8
        box = FancyBboxPatch((x, 3.7), 1.6, 1.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.8, 4.7, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 0.8, 4.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # AI Generation (middle right)
    ai_box = FancyBboxPatch((7, 3.5), 5.5, 2.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(9.75, 5.7, 'AI GENERATION', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['accent'])
    
    ai_steps = [('RAG Retrieval', ''), ('LLM Generate', 'Gemini 2.5'), ('Validate', '')]
    for i, (name, desc) in enumerate(ai_steps):
        x = 7.3 + i * 1.7
        box = FancyBboxPatch((x, 3.7), 1.5, 1.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.75, 4.7, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        if desc:
            ax.text(x + 0.75, 4.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # HITL (middle far right)
    hitl_box = FancyBboxPatch((13, 3.5), 2.5, 2.5, boxstyle="round,pad=0.03",
                               facecolor=COLORS['warning'], alpha=0.3, edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(hitl_box)
    ax.text(14.25, 5.7, 'HITL', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['warning'])
    ax.text(14.25, 4.5, 'Human\nReview', ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Flow arrows
    # Sources to Processing
    ax.annotate('', xy=(5.5, 8), xytext=(5.0, 8),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Processing to Output
    ax.annotate('', xy=(11, 8), xytext=(10.5, 8),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Processing to Storage
    ax.annotate('', xy=(3.5, 6.0), xytext=(6.5, 7.0),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5, connectionstyle="arc3,rad=0.3"))
    
    # Storage to AI
    ax.annotate('', xy=(7, 4.7), xytext=(6.5, 4.7),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # AI to HITL
    ax.annotate('', xy=(13, 4.7), xytext=(12.5, 4.7),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # HITL to Output
    ax.annotate('', xy=(14.25, 6.0), xytext=(14.25, 7.0),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # User interaction loop at bottom
    ax.text(8, 2.5, 'Continuous Feedback Loop', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['primary'])
    ax.annotate('', xy=(2, 2.8), xytext=(14, 2.8),
               arrowprops=dict(arrowstyle='<->', color=COLORS['primary'], lw=2))
    ax.text(8, 2.0, 'HITL Review & Validation at each phase', ha='center', va='center',
            fontsize=10, style='italic', color=COLORS['primary'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "data_flow.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_security_architecture():
    """Create security architecture diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Security Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Defense layers (stacked, no overlap)
    layers = [
        ('Cloud Armor WAF', 8.2, COLORS['danger'], 'DDoS Protection  |  Rate Limiting  |  Geo Blocking'),
        ('TLS 1.3 + mTLS', 6.8, COLORS['warning'], 'Encryption in Transit  |  Certificate Pinning  |  HSTS'),
        ('Authentication', 5.4, COLORS['accent'], 'Firebase Auth  |  MFA (TOTP)  |  OAuth 2.0'),
        ('Authorization', 4.0, COLORS['primary'], 'RBAC  |  JWT Tokens  |  API Keys'),
        ('Data Security', 2.6, COLORS['secondary'], 'AES-256 at Rest  |  Key Management  |  Audit Logs'),
    ]
    
    for name, y, color, items in layers:
        # Layer box
        box = FancyBboxPatch((0.5, y - 0.5), 13, 1.2, boxstyle="round,pad=0.02",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Layer name (left)
        ax.text(0.8, y + 0.1, name, ha='left', va='center', fontsize=11, fontweight='bold', color=color)
        
        # Items (right)
        ax.text(13.2, y + 0.1, items, ha='right', va='center', fontsize=9, color=COLORS['dark'])
    
    # AI Security (bottom)
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


def create_user_journey():
    """Create user journey diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(8, 10.5, 'User Journey: From Research Question to Publication', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Steps in two rows
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
    
    # Draw first row
    for i, (title, desc, color) in enumerate(steps_row1):
        x = 0.8 + i * 3
        y = 7.5
        
        box = FancyBboxPatch((x, y - 0.8), 2.6, 1.6, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Number circle
        circle = Circle((x + 0.4, y + 0.5), 0.25, facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        ax.text(x + 0.4, y + 0.5, title.split('.')[0].replace(' ', ''), ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # Title and description
        ax.text(x + 1.3, y + 0.4, title.split('. ')[1], ha='center', va='center', 
                fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.3, y - 0.2, desc, ha='center', va='center', fontsize=9, color=COLORS['dark'])
        
        # Arrow to next
        if i < 4:
            ax.annotate('', xy=(x + 3.0, y), xytext=(x + 2.7, y),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # Draw second row
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
    
    # Connecting arrow between rows (right side)
    ax.plot([15.0, 15.5], [7.5, 7.5], color=COLORS['dark'], lw=2)
    ax.plot([15.5, 15.5], [7.5, 4.5], color=COLORS['dark'], lw=2)
    ax.annotate('', xy=(15.0, 4.5), xytext=(15.5, 4.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Timeline at bottom
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


def create_deployment_architecture():
    """Create deployment/infrastructure diagram - OPTIMIZED"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Deployment Architecture (Google Cloud Platform)', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # GCP Region label
    ax.text(7, 8.9, 'Region: europe-west1 (Belgium) - GDPR Compliant', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['primary'])
    
    # Cloud Run Services (left)
    run_box = FancyBboxPatch((0.5, 5), 4, 3.3, boxstyle="round,pad=0.03",
                              facecolor=COLORS['secondary'], alpha=0.15, edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(run_box)
    ax.text(2.5, 8.0, 'Cloud Run Services', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['secondary'])
    
    services = ['API Gateway', 'Backend Service', 'Worker Service']
    for i, name in enumerate(services):
        y = 7.2 - i * 0.8
        box = FancyBboxPatch((0.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Data Services (center)
    data_box = FancyBboxPatch((5, 5), 4, 3.3, boxstyle="round,pad=0.03",
                               facecolor=COLORS['warning'], alpha=0.15, edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(data_box)
    ax.text(7, 8.0, 'Data Services', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['warning'])
    
    data_services = ['Firestore', 'Cloud Storage', 'Memorystore']
    for i, name in enumerate(data_services):
        y = 7.2 - i * 0.8
        box = FancyBboxPatch((5.3, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(7, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # AI Services (right)
    ai_box = FancyBboxPatch((9.5, 5), 4, 3.3, boxstyle="round,pad=0.03",
                             facecolor=COLORS['accent'], alpha=0.15, edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(11.5, 8.0, 'AI Services', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['accent'])
    
    ai_services = ['Vertex AI', 'ChromaDB', 'Embeddings']
    for i, name in enumerate(ai_services):
        y = 7.2 - i * 0.8
        box = FancyBboxPatch((9.8, y - 0.3), 3.4, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.5, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # DevOps (bottom left)
    ops_box = FancyBboxPatch((0.5, 1.5), 4, 3, boxstyle="round,pad=0.03",
                              facecolor=COLORS['danger'], alpha=0.15, edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(ops_box)
    ax.text(2.5, 4.2, 'DevOps & CI/CD', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['danger'])
    
    ops = ['Cloud Build', 'Artifact Registry', 'Terraform']
    for i, name in enumerate(ops):
        y = 3.5 - i * 0.7
        box = FancyBboxPatch((0.8, y - 0.25), 3.4, 0.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['danger'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Monitoring (bottom center)
    mon_box = FancyBboxPatch((5, 1.5), 4, 3, boxstyle="round,pad=0.03",
                              facecolor='#6B7280', alpha=0.15, edgecolor='#6B7280', linewidth=2)
    ax.add_patch(mon_box)
    ax.text(7, 4.2, 'Observability', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#6B7280')
    
    mon = ['Cloud Monitoring', 'Cloud Logging', 'Cloud Trace']
    for i, name in enumerate(mon):
        y = 3.5 - i * 0.7
        box = FancyBboxPatch((5.3, y - 0.25), 3.4, 0.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor='#6B7280', linewidth=1)
        ax.add_patch(box)
        ax.text(7, y, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Security (bottom right)
    sec_box = FancyBboxPatch((9.5, 1.5), 4, 3, boxstyle="round,pad=0.03",
                              facecolor=COLORS['primary'], alpha=0.15, edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(sec_box)
    ax.text(11.5, 4.2, 'Security', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['primary'])
    
    sec = ['Cloud Armor', 'Secret Manager', 'IAM']
    for i, name in enumerate(sec):
        y = 3.5 - i * 0.7
        box = FancyBboxPatch((9.8, y - 0.25), 3.4, 0.5, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.5, y, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Scale info
    ax.text(7, 0.8, 'Auto-scaling: 0-100 instances  |  SLA: 99.9%  |  Multi-zone deployment', 
            ha='center', va='center', fontsize=10, style='italic', color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "deployment_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


# ============================================================================
# PDF GENERATION
# ============================================================================

def create_architecture_pdf(images):
    """Create the architecture PDF presentation (A4, portrait, 10+ pages)"""
    
    filepath = OUTPUT_DIR / "ResearchFlow_Architecture.pdf"
    
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'], fontSize=28, alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['primary']), spaceAfter=20, fontName=UNICODE_FONT_BOLD
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['dark']), spaceAfter=10, fontName=UNICODE_FONT
    )
    
    heading1_style = ParagraphStyle(
        'Heading1', parent=styles['Heading1'], fontSize=18, alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['primary']), spaceBefore=20, spaceAfter=12,
        fontName=UNICODE_FONT_BOLD
    )
    
    heading2_style = ParagraphStyle(
        'Heading2', parent=styles['Heading2'], fontSize=14, alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['secondary']), spaceBefore=15, spaceAfter=8,
        fontName=UNICODE_FONT_BOLD
    )
    
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY,
        textColor=colors.HexColor(COLORS['dark']), spaceAfter=8, leading=14,
        fontName=UNICODE_FONT
    )
    
    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['dark']), spaceAfter=4, leftIndent=15,
        bulletIndent=5, fontName=UNICODE_FONT
    )
    
    story = []
    
    # ==================== PAGE 1: Title Page ====================
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("ResearchFlow", title_style))
    story.append(Paragraph("Tehnična arhitekturna dokumentacija", subtitle_style))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("AI-Powered Scoping Review Platform", 
                          ParagraphStyle('Sub2', fontSize=14, alignment=TA_CENTER,
                                        textColor=colors.HexColor(COLORS['secondary']),
                                        fontName=UNICODE_FONT)))
    story.append(Spacer(1, 3*cm))
    
    # Table of contents
    toc_data = [
        ['Vsebina', 'Stran'],
        ['1. Pregled sistema', '2'],
        ['2. High-Level arhitektura', '3'],
        ['3. Multi-Agent sistem', '4'],
        ['4. Pomnilniška arhitektura', '5'],
        ['5. RAG sistem', '6'],
        ['6. Workflow pipeline', '7'],
        ['7. HITL arhitektura', '8'],
        ['8. Pretok podatkov', '9'],
        ['9. Varnostna arhitektura', '10'],
        ['10. Deployment infrastruktura', '11'],
        ['11. Uporabniška izkušnja', '12'],
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
    story.append(Paragraph(f"Verzija 2.3 | April 2026", 
                          ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, 
                                        textColor=colors.gray, fontName=UNICODE_FONT)))
    story.append(PageBreak())
    
    # ==================== PAGE 2: System Overview ====================
    story.append(Paragraph("1. Pregled sistema", heading1_style))
    story.append(Paragraph(
        "ResearchFlow je napredna platforma za avtomatizirano pisanje scoping review člankov, "
        "ki temelji na multi-agent arhitekturi z AI podporo. Sistem omogoča celoten workflow "
        "od definicije raziskovalnega vprašanja do publikaciji pripravljenega članka.",
        body_style
    ))
    
    story.append(Paragraph("1.1 Ključne tehnologije", heading2_style))
    tech_data = [
        ['Komponenta', 'Tehnologija', 'Namen'],
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
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['light'])),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tech_table)
    
    story.append(Paragraph("1.2 Arhitekturni principi", heading2_style))
    principles = [
        "<b>Cloud-Native:</b> Zgrajen za GCP z auto-scaling in managed services",
        "<b>Event-Driven:</b> Asinhrona obdelava z Pub/Sub za dolgotrajna opravila",
        "<b>Microservices:</b> Ločene storitve za backend, workers, AI processing",
        "<b>HITL-First:</b> Človek vodi AI, 10 kontrolnih točk v workflow-u",
        "<b>Security-by-Design:</b> GDPR compliant, EU data residency, encryption",
    ]
    for p in principles:
        story.append(Paragraph(f"• {p}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 3: High-Level Architecture ====================
    story.append(Paragraph("2. High-Level sistemska arhitektura", heading1_style))
    story.append(Paragraph(
        "Spodnji diagram prikazuje slojevito arhitekturo sistema od uporabniškega vmesnika "
        "do podatkovne plasti, z integriranimi varnostnimi in observability komponentami.",
        body_style
    ))
    if 'high_level' in images:
        story.append(Image(images['high_level'], width=16*cm, height=12*cm))
    
    story.append(Paragraph("Ključne komponente:", heading2_style))
    components = [
        "<b>User Interface Layer:</b> Next.js 14 frontend s chatbot vmesnikom, HITL dashboardom",
        "<b>API Gateway:</b> Cloud Run z avtentikacijo, rate limitingom, load balancing",
        "<b>Backend Services:</b> FastAPI microservices za orchestration, RAG, agents",
        "<b>Data Layer:</b> Firestore za metadata, ChromaDB za vektorje, Cloud Storage za datoteke",
        "<b>Security Layer:</b> TLS 1.3, Cloud Armor WAF, PromptGuard za AI security",
    ]
    for c in components:
        story.append(Paragraph(f"• {c}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 4: Multi-Agent Architecture ====================
    story.append(Paragraph("3. Multi-Agent sistem", heading1_style))
    story.append(Paragraph(
        "ResearchFlow uporablja multi-agent arhitekturo, kjer specializirani agenti upravljajo "
        "različne faze scoping review procesa. Centralni orchestrator koordinira delovanje agentov.",
        body_style
    ))
    if 'multi_agent' in images:
        story.append(Image(images['multi_agent'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Agenti in njihove naloge:", heading2_style))
    agents_desc = [
        "<b>Research Plan Agent:</b> Parsira raziskovalna vprašanja, definira PICO/PCC kriterije",
        "<b>Search String Agent:</b> Generira Boolean iskalne nize za WoS, Scopus, PubMed",
        "<b>Screening Agent:</b> Analizira abstrakte, kategorizira Include/Exclude/Uncertain",
        "<b>Analysis Agent:</b> Identificira vrzeli, ekstrahira teme, prepoznava vzorce",
        "<b>Article Generator:</b> Piše sekcije članka z inline citati v akademskem stilu",
        "<b>Visualization Agent:</b> Generira PRISMA diagrame, Evidence Gap Maps",
    ]
    for a in agents_desc:
        story.append(Paragraph(f"• {a}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 5: Memory Architecture ====================
    story.append(Paragraph("4. Tri-nivojska pomnilniška arhitektura", heading1_style))
    story.append(Paragraph(
        "Sistem uporablja tri-nivojsko pomnilniško arhitekturo za optimalno upravljanje konteksta "
        "in stanja med obdelavo. Vsak nivo ima specifično vlogo in tehnologijo.",
        body_style
    ))
    if 'memory' in images:
        story.append(Image(images['memory'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Pomnilniški nivoji:", heading2_style))
    memory_desc = [
        "<b>Working Memory (Redis):</b> Trenutni kontekst naloge, pogovorna zgodovina, vmesni rezultati, HITL čakalna vrsta. TTL: minute do ure.",
        "<b>Short-Term Memory (ChromaDB):</b> Vektorske vložitve dokumentov, reasoning traces, screening odločitve, rezultati iskanj. TTL: trajanje projekta.",
        "<b>Long-Term Memory (Firestore + Cloud Storage):</b> Celotna zgodovina projekta, uporabniški profili, arhiv dokumentov, generirani članki. TTL: permanentno.",
    ]
    for m in memory_desc:
        story.append(Paragraph(f"• {m}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 6: RAG Architecture ====================
    story.append(Paragraph("5. RAG (Retrieval-Augmented Generation) arhitektura", heading1_style))
    story.append(Paragraph(
        "RAG sistem omogoča groundanje LLM odgovorov v izvornih dokumentih. "
        "Sestoji iz pipeline-a za ingestion in pipeline-a za retrieval z hibridnim iskanjem.",
        body_style
    ))
    if 'rag' in images:
        story.append(Image(images['rag'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Tehnični detajli:", heading2_style))
    rag_details = [
        "<b>Ingestion:</b> PyMuPDF + markitdown za PDF parsing, chunking 1024 tokens z 50 overlap",
        "<b>Embedding:</b> text-embedding-004 model, 768-dimenzionalni vektorji",
        "<b>Indexing:</b> ChromaDB z HNSW algoritmom za hitro similarity search",
        "<b>Retrieval:</b> Hibridno iskanje (BM25 + semantic), RRF fusion, top-k=10",
        "<b>Generation:</b> Gemini 2.5 Pro z grounded prompting in citation formatting",
    ]
    for r in rag_details:
        story.append(Paragraph(f"• {r}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 7: Workflow Pipeline ====================
    story.append(Paragraph("6. 8-fazni Workflow Pipeline", heading1_style))
    story.append(Paragraph(
        "Scoping review proces je razdeljen v 8 zaporednih faz, vsaka s specifičnimi nalogami in "
        "HITL kontrolnimi točkami. Vsaka faza ima jasno definirane vhode in izhode.",
        body_style
    ))
    if 'workflow' in images:
        story.append(Image(images['workflow'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Faze in HITL točke:", heading2_style))
    workflow_desc = [
        "1. <b>Research Plan:</b> Definicija vprašanj, PICO kriteriji - HITL #1 validacija",
        "2. <b>Search Strings:</b> Generacija Boolean izrazov - HITL #2 pregled sintakse",
        "3. <b>Abstract Screening:</b> AI kategorizacija - HITL #3 odločitve",
        "4. <b>Full-text ID:</b> DOI resolucija, pridobivanje PDF-jev",
        "5. <b>Full-text Ingestion:</b> Parsing, chunking - HITL #4 quality check",
        "6. <b>Gap Analysis:</b> Identifikacija vrzeli, teme - HITL #5 validacija tem",
        "7. <b>Article Generation:</b> Pisanje sekcij - HITL #6-7 pregled vsebine",
        "8. <b>Export:</b> PDF/DOCX, vizualizacije - HITL #8-10 končni pregled",
    ]
    for w in workflow_desc:
        story.append(Paragraph(f"• {w}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 8: HITL Architecture ====================
    story.append(Paragraph("7. Human-in-the-Loop (HITL) arhitektura", heading1_style))
    story.append(Paragraph(
        "HITL arhitektura zagotavlja, da človek vodi AI orodje in ne obratno. "
        "10 kontrolnih točk omogoča popoln nadzor nad vsako kritično odločitvijo v procesu.",
        body_style
    ))
    if 'hitl' in images:
        story.append(Image(images['hitl'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("HITL principi:", heading2_style))
    hitl_principles = [
        "<b>Transparentnost:</b> Vsaka AI odločitev ima vidne reasoning traces",
        "<b>Interaktivnost:</b> Uporabnik lahko approve/reject/modify vsako odločitev",
        "<b>Feedback Loop:</b> Rejected odločitve se vrnejo agentu z navodili",
        "<b>Audit Trail:</b> Vse odločitve so logirane za reproducibilnost",
        "<b>Batch Processing:</b> Možnost pregleda večih odločitev hkrati",
    ]
    for h in hitl_principles:
        story.append(Paragraph(f"• {h}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 9: Data Flow ====================
    story.append(Paragraph("8. Pretok podatkov", heading1_style))
    story.append(Paragraph(
        "Podatki tečejo skozi sistem od vhodnih virov (PDF, research plan) preko obdelave "
        "in shranjevanja do končnih izhodov (članek, vizualizacije).",
        body_style
    ))
    if 'data_flow' in images:
        story.append(Image(images['data_flow'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Podatkovni tokovi:", heading2_style))
    data_flows = [
        "<b>Vhod:</b> PDF dokumenti, research plan, uporabniški vnosi - Processing Layer",
        "<b>Obdelava:</b> Parse - Chunk - Embed - Index cikl z validacijo",
        "<b>Shranjevanje:</b> Firestore (metadata), ChromaDB (vektorji), Cloud Storage (datoteke)",
        "<b>AI Generacija:</b> RAG retrieval - LLM generate - Validate - Output",
        "<b>Izhod:</b> Article sections, citations, figures, PDF/DOCX, PRISMA diagram",
    ]
    for d in data_flows:
        story.append(Paragraph(f"• {d}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 10: Security Architecture ====================
    story.append(Paragraph("9. Varnostna arhitektura", heading1_style))
    story.append(Paragraph(
        "Varnost je vgrajena v vse plasti sistema - od omrežne zaščite do AI-specifične "
        "varnosti pred prompt injection napadi.",
        body_style
    ))
    if 'security' in images:
        story.append(Image(images['security'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Varnostne plasti:", heading2_style))
    security_layers = [
        "<b>Perimeter:</b> Cloud Armor WAF, DDoS zaščita, geo-blocking",
        "<b>Transport:</b> TLS 1.3, mTLS za interne storitve, HSTS",
        "<b>Authentication:</b> Firebase Auth z MFA (TOTP), OAuth 2.0 (Google, Microsoft)",
        "<b>Authorization:</b> RBAC (Owner/Editor/Reviewer/Viewer), JWT tokens",
        "<b>Data:</b> AES-256 encryption at rest, Google-managed keys",
        "<b>AI Security:</b> EnhancedPromptGuard (regex + LLM-based injection detection)",
        "<b>Audit:</b> Complete logging v Firestore + BigQuery za compliance",
    ]
    for s in security_layers:
        story.append(Paragraph(f"• {s}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 11: Deployment ====================
    story.append(Paragraph("10. Deployment infrastruktura", heading1_style))
    story.append(Paragraph(
        "ResearchFlow je deployan na Google Cloud Platform v EU regiji (europe-west1) "
        "za GDPR skladnost. Uporablja managed services z auto-scaling.",
        body_style
    ))
    if 'deployment' in images:
        story.append(Image(images['deployment'], width=16*cm, height=10*cm))
    
    story.append(Paragraph("Infrastrukturne specifikacije:", heading2_style))
    infra_specs = [
        "<b>Region:</b> europe-west1 (Belgium) - GDPR compliant, low latency za EU",
        "<b>Compute:</b> Cloud Run z auto-scaling 0-100 instanc",
        "<b>CI/CD:</b> Cloud Build z Terraform za infrastructure-as-code",
        "<b>Monitoring:</b> Cloud Monitoring, Logging, Trace za full observability",
        "<b>SLA:</b> Target 99.9% availability z multi-zone deployment",
    ]
    for i in infra_specs:
        story.append(Paragraph(f"• {i}", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== PAGE 12: User Journey ====================
    story.append(Paragraph("11. Uporabniška izkušnja", heading1_style))
    story.append(Paragraph(
        "Spodnja slika prikazuje celotno uporabniško pot od prijave do končnega izvoza članka. "
        "Tipični čas za dokončanje scoping reviewa je 4-6 tednov namesto tradicionalnih 6-12 mesecev.",
        body_style
    ))
    if 'user_journey' in images:
        story.append(Image(images['user_journey'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Koraki uporabniške poti:", heading2_style))
    journey_steps = [
        "<b>1. Login:</b> Avtentikacija preko Google/Email, MFA opcijsko",
        "<b>2. Create Project:</b> Nov scoping review projekt z imenom in opisom",
        "<b>3. Input Plan:</b> Definicija research questions, PICO, inclusion criteria",
        "<b>4. Generate Strings:</b> AI generira Boolean iskalne nize, uporabnik validira",
        "<b>5. Import Results:</b> Upload .ris/.csv iz WoS/Scopus/PubMed",
        "<b>6. Screening:</b> AI kategorizira abstrakte, uporabnik potrdi/zavrne",
        "<b>7. Full-text:</b> Upload PDF-jev, sistem parsira in indexira",
        "<b>8. Analysis:</b> AI identificira teme in vrzeli, uporabnik validira",
        "<b>9. Writing:</b> AI piše sekcije članka, uporabnik pregleduje/editira",
        "<b>10. Export:</b> Download PDF/DOCX s figurami in referencami",
    ]
    for j in journey_steps:
        story.append(Paragraph(f"• {j}", bullet_style))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Rezultat: Publication-ready scoping review članek z inline citati, "
        "PRISMA diagramom in Evidence Gap Map v 4-6 tednih.",
        ParagraphStyle('Highlight', fontSize=11, alignment=TA_CENTER, 
                      textColor=colors.HexColor(COLORS['accent']), fontName=UNICODE_FONT_BOLD)
    ))
    
    # Build PDF
    doc.build(story)
    return str(filepath)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("ResearchFlow Architecture Presentation Generator v2")
    print("=" * 60)
    
    images = {}
    
    print("\n[1/10] Creating high-level architecture...")
    images['high_level'] = create_high_level_architecture()
    print(f"       Done")
    
    print("\n[2/10] Creating multi-agent architecture...")
    images['multi_agent'] = create_multi_agent_architecture()
    print(f"       Done")
    
    print("\n[3/10] Creating memory architecture...")
    images['memory'] = create_memory_architecture()
    print(f"       Done")
    
    print("\n[4/10] Creating RAG architecture...")
    images['rag'] = create_rag_architecture()
    print(f"       Done")
    
    print("\n[5/10] Creating workflow pipeline...")
    images['workflow'] = create_workflow_pipeline()
    print(f"       Done")
    
    print("\n[6/10] Creating HITL architecture...")
    images['hitl'] = create_hitl_architecture()
    print(f"       Done")
    
    print("\n[7/10] Creating data flow diagram...")
    images['data_flow'] = create_data_flow()
    print(f"       Done")
    
    print("\n[8/10] Creating security architecture...")
    images['security'] = create_security_architecture()
    print(f"       Done")
    
    print("\n[9/10] Creating deployment architecture...")
    images['deployment'] = create_deployment_architecture()
    print(f"       Done")
    
    print("\n[10/10] Creating user journey...")
    images['user_journey'] = create_user_journey()
    print(f"       Done")
    
    print("\n" + "=" * 60)
    print("Generating architecture PDF (A4, 12 pages)...")
    pdf_path = create_architecture_pdf(images)
    print(f"PDF saved to: {pdf_path}")
    print("=" * 60)
    
    return pdf_path


if __name__ == "__main__":
    main()
