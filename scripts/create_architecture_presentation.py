#!/usr/bin/env python3
"""
ResearchFlow - Technical Architecture Presentation
Detailed architecture documentation with visualizations
Minimum 10 A4 pages
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

# Configure matplotlib to use Unicode-compatible font
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
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
# Use Segoe UI which is standard on Windows and supports all Unicode characters

UNICODE_FONT = 'SegoeUI'
UNICODE_FONT_BOLD = 'SegoeUIBold'

# Register Segoe UI fonts directly
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
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_high_level_architecture():
    """Create high-level system architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(7, 11.5, 'ResearchFlow - High-Level System Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # USER LAYER
    user_box = FancyBboxPatch((1, 9.5), 12, 1.2, boxstyle="round,pad=0.03",
                               facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(user_box)
    ax.text(7, 10.1, 'USER INTERFACE LAYER', ha='center', va='center', 
            fontsize=12, fontweight='bold', color=COLORS['primary'])
    
    # User components
    user_components = ['Next.js 14\nFrontend', 'React\nComponents', 'Chatbot\nInterface', 'HITL\nDashboard']
    for i, comp in enumerate(user_components):
        x = 2 + i * 3
        box = FancyBboxPatch((x, 9.6), 2.2, 0.9, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.1, 10.05, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # API GATEWAY
    api_box = FancyBboxPatch((1, 7.8), 12, 1.2, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(api_box)
    ax.text(7, 8.4, 'API GATEWAY (Cloud Run)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['secondary'])
    
    api_components = ['Authentication', 'Rate Limiting', 'Request\nValidation', 'Load\nBalancing']
    for i, comp in enumerate(api_components):
        x = 2 + i * 3
        box = FancyBboxPatch((x, 7.9), 2.2, 0.9, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.1, 8.35, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # BACKEND SERVICES
    backend_box = FancyBboxPatch((1, 4.5), 12, 2.8, boxstyle="round,pad=0.03",
                                  facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(backend_box)
    ax.text(7, 7.0, 'BACKEND SERVICES (Python/FastAPI)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['accent'])
    
    # Row 1: Core Services
    services_row1 = ['Orchestration\nService', 'RAG\nService', 'Agent\nCluster', 'HITL\nManager']
    for i, comp in enumerate(services_row1):
        x = 2 + i * 3
        box = FancyBboxPatch((x, 6.0), 2.2, 0.85, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.1, 6.42, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Row 2: Specialized Services  
    services_row2 = ['Document\nProcessor', 'Search String\nGenerator', 'Article\nGenerator', 'Export\nService']
    for i, comp in enumerate(services_row2):
        x = 2 + i * 3
        box = FancyBboxPatch((x, 4.9), 2.2, 0.85, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.1, 5.32, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # DATA LAYER
    data_box = FancyBboxPatch((1, 2.0), 12, 2.0, boxstyle="round,pad=0.03",
                               facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(data_box)
    ax.text(7, 3.7, 'DATA LAYER', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['warning'])
    
    data_components = [
        ('Firestore', 'Documents\nMetadata'),
        ('ChromaDB', 'Vector\nEmbeddings'),
        ('Cloud Storage', 'PDFs\nExports'),
        ('Redis', 'Cache\nSessions')
    ]
    for i, (name, desc) in enumerate(data_components):
        x = 2 + i * 3
        box = FancyBboxPatch((x, 2.2), 2.2, 1.3, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.1, 3.1, name, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.1, 2.6, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # AI LAYER (side)
    ai_box = FancyBboxPatch((0.2, 4.5), 0.6, 2.8, boxstyle="round,pad=0.02",
                             facecolor=COLORS['red_light'], edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(0.5, 5.9, 'VERTEX\nAI\n\nGemini\n2.5', ha='center', va='center', 
            fontsize=8, fontweight='bold', color=COLORS['danger'], rotation=0)
    
    # SECURITY LAYER (bottom)
    sec_box = FancyBboxPatch((1, 0.5), 12, 1.0, boxstyle="round,pad=0.03",
                              facecolor=COLORS['red_light'], edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(sec_box)
    ax.text(7, 1.0, 'SECURITY & OBSERVABILITY', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['danger'])
    
    sec_components = ['TLS 1.3', 'Cloud Armor', 'PromptGuard', 'Audit Logs', 'Monitoring']
    for i, comp in enumerate(sec_components):
        x = 1.5 + i * 2.3
        ax.text(x + 0.8, 0.65, comp, ha='center', va='center', fontsize=9, color=COLORS['dark'],
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=COLORS['danger'], linewidth=0.5))
    
    # Arrows between layers
    arrow_style = dict(arrowstyle='->', color=COLORS['dark'], lw=1.5)
    ax.annotate('', xy=(7, 9.5), xytext=(7, 9.0), arrowprops=arrow_style)
    ax.annotate('', xy=(7, 7.8), xytext=(7, 7.3), arrowprops=arrow_style)
    ax.annotate('', xy=(7, 4.5), xytext=(7, 4.0), arrowprops=arrow_style)
    
    # Arrow to Vertex AI
    ax.annotate('', xy=(0.8, 5.9), xytext=(1.0, 5.9), arrowprops=dict(arrowstyle='<->', color=COLORS['danger'], lw=1.5))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "high_level_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_multi_agent_architecture():
    """Create multi-agent system architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7, 10.5, 'Multi-Agent System Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # ORCHESTRATOR (center top)
    orch_box = FancyBboxPatch((5, 8.5), 4, 1.5, boxstyle="round,pad=0.05",
                               facecolor=COLORS['primary'], edgecolor=COLORS['dark'], linewidth=2)
    ax.add_patch(orch_box)
    ax.text(7, 9.4, 'ORCHESTRATOR', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    ax.text(7, 8.9, 'Workflow Coordination\nState Management', ha='center', va='center', 
            fontsize=10, color='white')
    
    # AGENT CLUSTER
    agents = [
        (1.5, 5.5, 'Research Plan\nAgent', COLORS['secondary'], 
         '• Parse research questions\n• Define PICO/PCC\n• Set inclusion criteria'),
        (5, 5.5, 'Search String\nAgent', COLORS['accent'],
         '• Generate Boolean queries\n• Multi-database formats\n• Validate syntax'),
        (8.5, 5.5, 'Screening\nAgent', COLORS['warning'],
         '• Abstract analysis\n• Include/Exclude/Uncertain\n• Reasoning traces'),
        (12, 5.5, 'Analysis\nAgent', COLORS['danger'],
         '• Gap identification\n• Theme extraction\n• Pattern recognition'),
    ]
    
    for x, y, name, color, desc in agents:
        # Agent box
        box = FancyBboxPatch((x - 1.3, y - 1.5), 2.6, 3.0, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.2, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Agent header
        header = FancyBboxPatch((x - 1.2, y + 0.8), 2.4, 0.6, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x, y + 1.1, name, ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        
        # Agent description
        ax.text(x, y - 0.3, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        
        # Arrow from orchestrator
        ax.annotate('', xy=(x, y + 1.5), xytext=(7, 8.5),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2, connectionstyle="arc3,rad=0.1"))
    
    # Second row of agents
    agents_row2 = [
        (3, 1.5, 'Article\nGenerator', COLORS['secondary'],
         '• Section generation\n• Citation formatting\n• Academic style'),
        (7, 1.5, 'Export\nAgent', COLORS['accent'],
         '• PDF rendering\n• DOCX conversion\n• Figure embedding'),
        (11, 1.5, 'Visualization\nAgent', COLORS['warning'],
         '• PRISMA diagrams\n• Evidence maps\n• Charts & graphs'),
    ]
    
    for x, y, name, color, desc in agents_row2:
        box = FancyBboxPatch((x - 1.3, y - 1.2), 2.6, 2.4, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.2, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        header = FancyBboxPatch((x - 1.2, y + 0.5), 2.4, 0.6, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x, y + 0.8, name, ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        ax.text(x, y - 0.3, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Connection lines between agent rows
    ax.plot([3, 3], [2.7, 4.0], color=COLORS['dark'], linestyle='--', linewidth=1, alpha=0.5)
    ax.plot([7, 7], [2.7, 4.0], color=COLORS['dark'], linestyle='--', linewidth=1, alpha=0.5)
    ax.plot([11, 11], [2.7, 4.0], color=COLORS['dark'], linestyle='--', linewidth=1, alpha=0.5)
    
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
    
    # Working Memory (top)
    wm_box = FancyBboxPatch((0.5, 6.5), 13, 2.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=3)
    ax.add_patch(wm_box)
    ax.text(7, 8.7, 'WORKING MEMORY (Redis)', ha='center', va='center',
            fontsize=14, fontweight='bold', color=COLORS['accent'])
    
    wm_items = [
        ('Current Task\nContext', 'Active agent state,\ncurrent step info'),
        ('Conversation\nHistory', 'Recent user queries,\nagent responses'),
        ('Intermediate\nResults', 'Partial computations,\ntemporary data'),
        ('HITL Queue', 'Pending decisions,\nuser notifications'),
    ]
    for i, (title, desc) in enumerate(wm_items):
        x = 1.5 + i * 3.2
        box = FancyBboxPatch((x, 6.7), 2.8, 1.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.4, 8.0, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.4, 7.3, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Short-Term Memory (middle)
    stm_box = FancyBboxPatch((0.5, 3.5), 13, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=3)
    ax.add_patch(stm_box)
    ax.text(7, 5.7, 'SHORT-TERM MEMORY (ChromaDB)', ha='center', va='center',
            fontsize=14, fontweight='bold', color=COLORS['secondary'])
    
    stm_items = [
        ('Document\nChunks', 'Semantic embeddings,\n768-dim vectors'),
        ('Reasoning\nTraces', 'AI decision logs,\nexplanations'),
        ('Screening\nDecisions', 'Include/Exclude/Uncertain,\nconfidence scores'),
        ('Search\nResults', 'Query results cache,\nranked documents'),
    ]
    for i, (title, desc) in enumerate(stm_items):
        x = 1.5 + i * 3.2
        box = FancyBboxPatch((x, 3.7), 2.8, 1.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.4, 5.0, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.4, 4.3, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Long-Term Memory (bottom)
    ltm_box = FancyBboxPatch((0.5, 0.5), 13, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=3)
    ax.add_patch(ltm_box)
    ax.text(7, 2.7, 'LONG-TERM MEMORY (Firestore + Cloud Storage)', ha='center', va='center',
            fontsize=14, fontweight='bold', color=COLORS['primary'])
    
    ltm_items = [
        ('Project\nState', 'Full project history,\nversioned snapshots'),
        ('User\nProfiles', 'Preferences, roles,\naudit trail'),
        ('Document\nArchive', 'Original PDFs,\nprocessed text'),
        ('Generated\nArticles', 'Final outputs,\nexport history'),
    ]
    for i, (title, desc) in enumerate(ltm_items):
        x = 1.5 + i * 3.2
        box = FancyBboxPatch((x, 0.7), 2.8, 1.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 1.4, 2.0, title, ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 1.4, 1.3, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # Arrows between tiers
    ax.annotate('', xy=(7, 6.5), xytext=(7, 6.0), 
                arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(7, 3.5), xytext=(7, 3.0), 
                arrowprops=dict(arrowstyle='<->', color=COLORS['dark'], lw=2))
    
    # Labels
    ax.text(7.5, 6.25, 'Promote/Evict', ha='left', va='center', fontsize=9, style='italic')
    ax.text(7.5, 3.25, 'Persist/Load', ha='left', va='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "memory_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_rag_architecture():
    """Create RAG system architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(7, 10.5, 'RAG (Retrieval-Augmented Generation) Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # INGESTION PIPELINE (left side)
    ing_box = FancyBboxPatch((0.3, 4), 3.5, 5.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
    ax.add_patch(ing_box)
    ax.text(2.05, 9.2, 'INGESTION', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['primary'])
    
    ing_steps = [
        ('1. PDF Upload', 8.5),
        ('2. Text Extraction', 7.7),
        ('3. Chunking', 6.9),
        ('4. Embedding', 6.1),
        ('5. Index Storage', 5.3),
    ]
    for step, y in ing_steps:
        box = FancyBboxPatch((0.6, y - 0.3), 2.9, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['primary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.05, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows between ingestion steps
    for i in range(len(ing_steps) - 1):
        ax.annotate('', xy=(2.05, ing_steps[i+1][1] + 0.35), xytext=(2.05, ing_steps[i][1] - 0.35),
                   arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=1.5))
    
    # Details under ingestion
    ax.text(2.05, 4.5, 'PyMuPDF + markitdown\nChunk: 1024 tokens\n50 token overlap\ntext-embedding-004', 
            ha='center', va='center', fontsize=8, style='italic', color=COLORS['dark'])
    
    # VECTOR DATABASE (center)
    vdb_box = FancyBboxPatch((4.5, 4), 5, 5.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(vdb_box)
    ax.text(7, 9.2, 'VECTOR DATABASE', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['secondary'])
    
    # ChromaDB icon
    chroma_box = FancyBboxPatch((5.5, 7.2), 3, 1.5, boxstyle="round,pad=0.03",
                                 facecolor=COLORS['secondary'], edgecolor='white', linewidth=2)
    ax.add_patch(chroma_box)
    ax.text(7, 8.1, 'ChromaDB', ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    ax.text(7, 7.6, '768-dim embeddings', ha='center', va='center', fontsize=10, color='white')
    
    # Index types
    indices = [('Document\nIndex', 6.3), ('Reasoning\nIndex', 5.4), ('Metadata\nIndex', 4.5)]
    for name, y in indices:
        box = FancyBboxPatch((5.2, y - 0.3), 1.5, 0.6, boxstyle="round,pad=0.01",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(5.95, y, name, ha='center', va='center', fontsize=8, color=COLORS['dark'])
        
        box2 = FancyBboxPatch((7.3, y - 0.3), 1.5, 0.6, boxstyle="round,pad=0.01",
                               facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box2)
        ax.text(8.05, y, 'HNSW\nSearch', ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # RETRIEVAL PIPELINE (right side)
    ret_box = FancyBboxPatch((10.2, 4), 3.5, 5.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ret_box)
    ax.text(11.95, 9.2, 'RETRIEVAL', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['accent'])
    
    ret_steps = [
        ('1. Query Embed', 8.5),
        ('2. Hybrid Search', 7.7),
        ('3. Re-ranking', 6.9),
        ('4. Context Build', 6.1),
        ('5. LLM Generate', 5.3),
    ]
    for step, y in ret_steps:
        box = FancyBboxPatch((10.5, y - 0.3), 2.9, 0.6, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.95, y, step, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrows between retrieval steps
    for i in range(len(ret_steps) - 1):
        ax.annotate('', xy=(11.95, ret_steps[i+1][1] + 0.35), xytext=(11.95, ret_steps[i][1] - 0.35),
                   arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=1.5))
    
    # Details under retrieval
    ax.text(11.95, 4.5, 'BM25 + Semantic\nTop-k: 10\nRRF fusion\nGemini 2.5 Pro', 
            ha='center', va='center', fontsize=8, style='italic', color=COLORS['dark'])
    
    # Connecting arrows
    ax.annotate('', xy=(4.5, 5.3), xytext=(3.8, 5.3),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(10.2, 7.7), xytext=(9.5, 7.7),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Bottom: Output
    out_box = FancyBboxPatch((4, 0.5), 6, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(out_box)
    ax.text(7, 2.5, 'GENERATED OUTPUT', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['warning'])
    ax.text(7, 1.6, '• Grounded in source documents\n• Inline citations [Author, Year]\n• Visible reasoning traces', 
            ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Arrow to output
    ax.annotate('', xy=(7, 3.0), xytext=(11.95, 5.0),
               arrowprops=dict(arrowstyle='->', color=COLORS['warning'], lw=2, connectionstyle="arc3,rad=-0.2"))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "rag_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_workflow_pipeline():
    """Create detailed 8-phase workflow pipeline"""
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    ax.text(8, 10.5, '8-Phase Scoping Review Workflow', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    phases = [
        ('Phase 1', 'Research Plan\nCreation', COLORS['primary'], 
         ['Define research questions', 'Set PICO/PCC criteria', 'Specify inclusion/exclusion'], 'HITL #1'),
        ('Phase 2', 'Search String\nGeneration', COLORS['primary'],
         ['Boolean query generation', 'WoS/Scopus/PubMed formats', 'Syntax validation'], 'HITL #2'),
        ('Phase 3', 'Abstract\nScreening', COLORS['secondary'],
         ['AI-assisted categorization', 'Include/Exclude/Uncertain', 'Reasoning traces'], 'HITL #3'),
        ('Phase 4', 'Full-text\nIdentification', COLORS['secondary'],
         ['Retrieve full PDFs', 'DOI resolution', 'Source linking'], ''),
        ('Phase 5', 'Full-text\nIngestion', COLORS['accent'],
         ['PDF parsing', 'Text chunking', 'Vector embedding'], 'HITL #4'),
        ('Phase 6', 'Gap\nAnalysis', COLORS['accent'],
         ['Theme extraction', 'Gap identification', 'Pattern analysis'], 'HITL #5'),
        ('Phase 7', 'Article\nGeneration', COLORS['warning'],
         ['Section generation', 'Citation formatting', 'Academic style'], 'HITL #6-7'),
        ('Phase 8', 'Export &\nVisualization', COLORS['danger'],
         ['PDF/DOCX export', 'PRISMA diagram', 'Evidence maps'], 'HITL #8-10'),
    ]
    
    # Draw phases in 2 rows
    for i, (num, name, color, tasks, hitl) in enumerate(phases[:4]):
        x = 1 + i * 3.8
        y = 7
        
        # Main phase box
        box = FancyBboxPatch((x, y - 1), 3.2, 3, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Phase header
        header = FancyBboxPatch((x + 0.1, y + 1.3), 3, 0.6, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x + 1.6, y + 1.6, f'{num}: {name}', ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # Tasks
        for j, task in enumerate(tasks):
            ax.text(x + 0.3, y + 0.8 - j * 0.5, f'• {task}', ha='left', va='center', 
                    fontsize=8, color=COLORS['dark'])
        
        # HITL indicator
        if hitl:
            ax.text(x + 1.6, y - 0.8, hitl, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1))
        
        # Arrow to next
        if i < 3:
            ax.annotate('', xy=(x + 3.5, y + 0.5), xytext=(x + 3.2, y + 0.5),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Second row (phases 5-8)
    for i, (num, name, color, tasks, hitl) in enumerate(phases[4:]):
        x = 1 + i * 3.8
        y = 2.5
        
        box = FancyBboxPatch((x, y - 1), 3.2, 3, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        header = FancyBboxPatch((x + 0.1, y + 1.3), 3, 0.6, boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(header)
        ax.text(x + 1.6, y + 1.6, f'{num}: {name}', ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        for j, task in enumerate(tasks):
            ax.text(x + 0.3, y + 0.8 - j * 0.5, f'• {task}', ha='left', va='center', 
                    fontsize=8, color=COLORS['dark'])
        
        if hitl:
            ax.text(x + 1.6, y - 0.8, hitl, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1))
        
        if i < 3:
            ax.annotate('', xy=(x + 3.5, y + 0.5), xytext=(x + 3.2, y + 0.5),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Connecting arrow between rows
    ax.annotate('', xy=(14.5, 6.0), xytext=(14.5, 7.0),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2, connectionstyle="arc3,rad=0"))
    ax.annotate('', xy=(1.5, 5.5), xytext=(14.5, 5.5),
               arrowprops=dict(arrowstyle='-', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(1.5, 4.5), xytext=(1.5, 5.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "workflow_pipeline.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_hitl_architecture():
    """Create Human-in-the-Loop architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Human-in-the-Loop (HITL) Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # AI Processing (left)
    ai_box = FancyBboxPatch((0.5, 2), 4, 6.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['secondary'], alpha=0.2, edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(2.5, 8.2, 'AI PROCESSING', ha='center', va='center',
            fontsize=14, fontweight='bold', color=COLORS['secondary'])
    
    ai_steps = [
        ('Document Analysis', 7.3),
        ('Decision Generation', 6.3),
        ('Confidence Score', 5.3),
        ('Reasoning Trace', 4.3),
        ('Action Queue', 3.3),
    ]
    for step, y in ai_steps:
        box = FancyBboxPatch((0.8, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(2.5, y, step, ha='center', va='center', fontsize=11, color=COLORS['dark'])
    
    # HITL Decision Point (center)
    hitl_box = FancyBboxPatch((5, 3.5), 4, 4, boxstyle="round,pad=0.05",
                               facecolor=COLORS['warning'], alpha=0.3, edgecolor=COLORS['warning'], linewidth=3)
    ax.add_patch(hitl_box)
    ax.text(7, 7.2, 'HITL DECISION\nPOINT', ha='center', va='center',
            fontsize=14, fontweight='bold', color=COLORS['warning'])
    
    # Decision options
    decisions = [
        ('✓ APPROVE', 6.2, COLORS['accent']),
        ('✗ REJECT', 5.4, COLORS['danger']),
        ('✎ MODIFY', 4.6, COLORS['primary']),
        ('⟲ DEFER', 3.8, '#6B7280'),
    ]
    for text, y, color in decisions:
        box = FancyBboxPatch((5.5, y - 0.25), 3, 0.5, boxstyle="round,pad=0.02",
                              facecolor=color, alpha=0.3, edgecolor=color, linewidth=1)
        ax.add_patch(box)
        ax.text(7, y, text, ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['dark'])
    
    # Human Review (right)
    human_box = FancyBboxPatch((9.5, 2), 4, 6.5, boxstyle="round,pad=0.03",
                                facecolor=COLORS['accent'], alpha=0.2, edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(human_box)
    ax.text(11.5, 8.2, 'HUMAN REVIEW', ha='center', va='center',
            fontsize=14, fontweight='bold', color=COLORS['accent'])
    
    human_steps = [
        ('View Reasoning', 7.3),
        ('Check Sources', 6.3),
        ('Validate Decision', 5.3),
        ('Add Comments', 4.3),
        ('Submit Action', 3.3),
    ]
    for step, y in human_steps:
        box = FancyBboxPatch((9.8, y - 0.35), 3.4, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(11.5, y, step, ha='center', va='center', fontsize=11, color=COLORS['dark'])
    
    # Arrows
    ax.annotate('', xy=(5, 5.5), xytext=(4.5, 5.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    ax.annotate('', xy=(9.5, 5.5), xytext=(9, 5.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Feedback loop
    ax.annotate('', xy=(2.5, 2.5), xytext=(7, 3.2),
               arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=2, 
                             connectionstyle="arc3,rad=-0.3", linestyle='--'))
    ax.text(4.5, 2.3, 'Feedback Loop', ha='center', va='center', fontsize=9, 
            style='italic', color=COLORS['danger'])
    
    # 10 HITL points list
    hitl_points = [
        'HITL #1: Research Plan Review',
        'HITL #2: Search String Validation',
        'HITL #3: Screening Decisions',
        'HITL #4: Full-text Selection',
        'HITL #5: Theme Validation',
        'HITL #6: Article Structure',
        'HITL #7: Citation Check',
        'HITL #8: Language/Style',
        'HITL #9: Figures Review',
        'HITL #10: Final Approval',
    ]
    
    ax.text(7, 1.5, '10 HITL Decision Points:', ha='center', va='center', 
            fontsize=11, fontweight='bold', color=COLORS['dark'])
    
    for i, point in enumerate(hitl_points[:5]):
        ax.text(3, 1.0 - i * 0.3, point, ha='left', va='center', fontsize=8, color=COLORS['dark'])
    for i, point in enumerate(hitl_points[5:]):
        ax.text(8, 1.0 - i * 0.3, point, ha='left', va='center', fontsize=8, color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "hitl_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_data_flow():
    """Create data flow diagram"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(8, 9.5, 'Data Flow Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # Sources (top left)
    sources = [('PDF\nDocuments', 0.5), ('Research\nPlan', 1.8), ('User\nInput', 3.1)]
    for name, x in sources:
        box = FancyBboxPatch((x, 7.8), 1.1, 1.2, boxstyle="round,pad=0.02",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=2)
        ax.add_patch(box)
        ax.text(x + 0.55, 8.4, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
    
    # Processing
    proc_box = FancyBboxPatch((5, 6.5), 6, 2.5, boxstyle="round,pad=0.03",
                               facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(proc_box)
    ax.text(8, 8.6, 'PROCESSING LAYER', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['secondary'])
    
    proc_steps = [('Parse', 5.5), ('Chunk', 6.8), ('Embed', 8.1), ('Index', 9.4)]
    for name, x in proc_steps:
        box = FancyBboxPatch((x, 6.8), 1.1, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.55, 7.15, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Storage
    storage_box = FancyBboxPatch((0.5, 3.5), 6, 2.5, boxstyle="round,pad=0.03",
                                  facecolor=COLORS['orange_light'], edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(storage_box)
    ax.text(3.5, 5.6, 'STORAGE LAYER', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['warning'])
    
    storages = [('Firestore', 1, 'Metadata'), ('ChromaDB', 2.8, 'Vectors'), ('Cloud\nStorage', 4.6, 'Files')]
    for name, x, desc in storages:
        box = FancyBboxPatch((x, 3.8), 1.4, 1.4, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.7, 4.7, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        ax.text(x + 0.7, 4.2, desc, ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    # AI Generation
    ai_box = FancyBboxPatch((7, 3.5), 4.5, 2.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['green_light'], edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(9.25, 5.6, 'AI GENERATION', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['accent'])
    
    ai_steps = [('RAG\nRetrieval', 7.3), ('LLM\nGenerate', 8.8), ('Validate', 10.3)]
    for name, x in ai_steps:
        box = FancyBboxPatch((x, 3.8), 1.3, 1.4, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.65, 4.5, name, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Output (right)
    out_box = FancyBboxPatch((12, 3.5), 3.5, 5.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['red_light'], edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(out_box)
    ax.text(13.75, 8.6, 'OUTPUT', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['danger'])
    
    outputs = [('Article\nSections', 8.0), ('Citations', 7.0), ('Figures', 6.0), ('PDF/DOCX', 5.0), ('PRISMA', 4.0)]
    for name, y in outputs:
        box = FancyBboxPatch((12.2, y - 0.35), 3.1, 0.7, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['danger'], linewidth=1)
        ax.add_patch(box)
        ax.text(13.75, y, name, ha='center', va='center', fontsize=10, color=COLORS['dark'])
    
    # Flow arrows
    # Sources to Processing
    for x in [1.05, 2.35, 3.65]:
        ax.annotate('', xy=(5, 7.5), xytext=(x, 7.8),
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # Processing to Storage
    ax.annotate('', xy=(3.5, 6.0), xytext=(8, 6.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5, connectionstyle="arc3,rad=0.2"))
    
    # Storage to AI
    ax.annotate('', xy=(7, 4.5), xytext=(6.5, 4.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # AI to Output
    ax.annotate('', xy=(12, 5.5), xytext=(11.5, 4.8),
               arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
    
    # User interaction loop
    ax.text(8, 1.5, 'Continuous Feedback Loop', ha='center', va='center',
            fontsize=11, fontweight='bold', color=COLORS['primary'])
    ax.annotate('', xy=(2, 3.5), xytext=(13, 3.5),
               arrowprops=dict(arrowstyle='<->', color=COLORS['primary'], lw=2, 
                             connectionstyle="arc3,rad=-0.3"))
    ax.text(7.5, 2.5, 'HITL Review & Validation', ha='center', va='center',
            fontsize=10, style='italic', color=COLORS['primary'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "data_flow.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_security_architecture():
    """Create security architecture diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Security Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # External perimeter
    ext_box = FancyBboxPatch((0.3, 0.5), 13.4, 8.5, boxstyle="round,pad=0.05",
                              facecolor='white', edgecolor=COLORS['danger'], linewidth=3, linestyle='--')
    ax.add_patch(ext_box)
    ax.text(7, 8.7, 'EXTERNAL PERIMETER', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['danger'])
    
    # Defense layers
    layers = [
        ('Cloud Armor WAF', 8.0, COLORS['danger'], ['DDoS Protection', 'Rate Limiting', 'Geo Blocking']),
        ('TLS 1.3 + mTLS', 6.5, COLORS['warning'], ['Encryption in Transit', 'Certificate Pinning', 'HSTS']),
        ('Authentication', 5.0, COLORS['accent'], ['Firebase Auth', 'MFA (TOTP)', 'OAuth 2.0']),
        ('Authorization', 3.5, COLORS['primary'], ['RBAC', 'JWT Tokens', 'API Keys']),
        ('Data Security', 2.0, COLORS['secondary'], ['AES-256 at Rest', 'Key Management', 'Audit Logs']),
    ]
    
    for name, y, color, items in layers:
        # Layer box
        box = FancyBboxPatch((1, y - 0.6), 12, 1.2, boxstyle="round,pad=0.02",
                              facecolor=color, alpha=0.2, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Layer name
        ax.text(2.5, y, name, ha='center', va='center', fontsize=11, fontweight='bold', color=color)
        
        # Items
        for i, item in enumerate(items):
            x = 5 + i * 2.8
            item_box = FancyBboxPatch((x, y - 0.35), 2.5, 0.7, boxstyle="round,pad=0.02",
                                       facecolor='white', edgecolor=color, linewidth=1)
            ax.add_patch(item_box)
            ax.text(x + 1.25, y, item, ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # AI Security (right side callout)
    ai_sec_box = FancyBboxPatch((11.5, 5.5), 2, 2.5, boxstyle="round,pad=0.02",
                                 facecolor=COLORS['purple_light'], edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(ai_sec_box)
    ax.text(12.5, 7.6, 'AI Security', ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['secondary'])
    ai_items = ['PromptGuard', 'Injection Filter', 'Output Sanitize']
    for i, item in enumerate(ai_items):
        ax.text(12.5, 7.1 - i * 0.5, f'• {item}', ha='center', va='center', fontsize=8, color=COLORS['dark'])
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "security_architecture.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_user_journey():
    """Create user journey diagram"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    ax.text(8, 11.5, 'User Journey: From Research Question to Publication', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    steps = [
        (1, 10, 'START', '1. Login & Create Project',
         'User authenticates via\nGoogle/Email and creates\na new scoping review project', COLORS['primary']),
        (4.5, 10, 'DEFINE', '2. Input Research Plan',
         'Define research questions,\nPICO/PCC criteria,\ninclusion/exclusion rules', COLORS['primary']),
        (8, 10, 'GENERATE', '3. Generate Search Strings',
         'AI creates Boolean queries\nfor WoS, Scopus, PubMed\n→ HITL validates', COLORS['secondary']),
        (11.5, 10, 'IMPORT', '4. Import Results',
         'Upload exported search\nresults (.ris, .csv)\nfrom databases', COLORS['secondary']),
        (14, 8, 'SCREEN', '5. Abstract Screening',
         'AI categorizes each abstract\nas Include/Exclude/Uncertain\n→ HITL reviews decisions', COLORS['accent']),
        (11.5, 6, 'RETRIEVE', '6. Get Full Texts',
         'System identifies PDFs\nvia DOI/links,\nuser uploads remaining', COLORS['accent']),
        (8, 6, 'ANALYZE', '7. Full-text Analysis',
         'AI extracts data, identifies\nthemes, finds gaps\n→ HITL validates themes', COLORS['warning']),
        (4.5, 6, 'WRITE', '8. Article Generation',
         'AI writes sections with\ninline citations\n→ HITL reviews each section', COLORS['warning']),
        (1, 6, 'VISUALIZE', '9. Create Figures',
         'Generate PRISMA diagram,\nEvidence Gap Map,\nConceptual Model', COLORS['danger']),
        (1, 3.5, 'EXPORT', '10. Export & Publish',
         'Download publication-ready\nPDF/DOCX with figures,\nreferences formatted', COLORS['danger']),
    ]
    
    for x, y, stage, title, desc, color in steps:
        # Step box
        box = FancyBboxPatch((x - 1.3, y - 1.8), 2.6, 1.6, boxstyle="round,pad=0.03",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        
        # Stage badge
        badge = FancyBboxPatch((x - 0.5, y - 0.3), 1, 0.4, boxstyle="round,pad=0.02",
                                facecolor=color, edgecolor='white', linewidth=1)
        ax.add_patch(badge)
        ax.text(x, y - 0.1, stage, ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        
        # Title
        ax.text(x, y - 0.65, title, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        
        # Description
        ax.text(x, y - 1.35, desc, ha='center', va='center', fontsize=7, color=COLORS['dark'])
    
    # Flow arrows
    arrows = [
        ((2.3, 10), (3.2, 10)),
        ((5.8, 10), (6.7, 10)),
        ((9.3, 10), (10.2, 10)),
        ((12.8, 10), (13.5, 9.0)),
        ((14, 7.5), (13, 6.5)),
        ((10.2, 6), (9.3, 6)),
        ((6.7, 6), (5.8, 6)),
        ((3.2, 6), (2.3, 6)),
        ((1, 5.2), (1, 4.5)),
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Timeline
    ax.plot([0.5, 15.5], [2, 2], color=COLORS['dark'], linewidth=2)
    timeline_points = [
        (2, 'Day 1-2', 'Setup & Plan'),
        (5, 'Day 3-5', 'Search & Import'),
        (8, 'Week 2', 'Screening'),
        (11, 'Week 3-4', 'Analysis'),
        (14, 'Week 5-6', 'Writing & Export'),
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
    """Create deployment/infrastructure diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'Deployment Architecture (Google Cloud Platform)', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark'])
    
    # GCP Region
    gcp_box = FancyBboxPatch((0.3, 0.5), 13.4, 8.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['blue_light'], edgecolor=COLORS['primary'], linewidth=3)
    ax.add_patch(gcp_box)
    ax.text(7, 8.7, 'GCP Region: europe-west1 (Belgium) - GDPR Compliant', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['primary'])
    
    # Cloud Run Services
    run_box = FancyBboxPatch((0.8, 5.5), 6, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['secondary'], alpha=0.2, edgecolor=COLORS['secondary'], linewidth=2)
    ax.add_patch(run_box)
    ax.text(3.8, 7.7, 'Cloud Run Services', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['secondary'])
    
    services = [
        ('API\nGateway', 1.3, 6.3),
        ('Backend\nService', 3.3, 6.3),
        ('Worker\nService', 5.3, 6.3),
    ]
    for name, x, y in services:
        box = FancyBboxPatch((x, y - 0.5), 1.5, 1, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['secondary'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.75, y, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
    
    # Data Services
    data_box = FancyBboxPatch((7.2, 5.5), 6, 2.5, boxstyle="round,pad=0.03",
                               facecolor=COLORS['warning'], alpha=0.2, edgecolor=COLORS['warning'], linewidth=2)
    ax.add_patch(data_box)
    ax.text(10.2, 7.7, 'Data Services', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['warning'])
    
    data_services = [
        ('Firestore', 7.7, 6.3),
        ('Cloud\nStorage', 9.7, 6.3),
        ('Memory-\nstore', 11.7, 6.3),
    ]
    for name, x, y in data_services:
        box = FancyBboxPatch((x, y - 0.5), 1.5, 1, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['warning'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.75, y, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
    
    # AI Services
    ai_box = FancyBboxPatch((0.8, 2.5), 4, 2.5, boxstyle="round,pad=0.03",
                             facecolor=COLORS['accent'], alpha=0.2, edgecolor=COLORS['accent'], linewidth=2)
    ax.add_patch(ai_box)
    ax.text(2.8, 4.7, 'AI Services', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['accent'])
    
    ai_services = [('Vertex AI\nGemini 2.5', 1.3, 3.3), ('ChromaDB\n(Managed)', 3.3, 3.3)]
    for name, x, y in ai_services:
        box = FancyBboxPatch((x, y - 0.5), 1.5, 1, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['accent'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.75, y, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
    
    # DevOps
    ops_box = FancyBboxPatch((5.2, 2.5), 4.2, 2.5, boxstyle="round,pad=0.03",
                              facecolor=COLORS['danger'], alpha=0.2, edgecolor=COLORS['danger'], linewidth=2)
    ax.add_patch(ops_box)
    ax.text(7.3, 4.7, 'DevOps & CI/CD', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['danger'])
    
    ops_services = [('Cloud\nBuild', 5.7, 3.3), ('Artifact\nRegistry', 7.7, 3.3)]
    for name, x, y in ops_services:
        box = FancyBboxPatch((x, y - 0.5), 1.5, 1, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor=COLORS['danger'], linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.75, y, name, ha='center', va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
    
    # Monitoring
    mon_box = FancyBboxPatch((9.8, 2.5), 3.4, 2.5, boxstyle="round,pad=0.03",
                              facecolor='#6B7280', alpha=0.2, edgecolor='#6B7280', linewidth=2)
    ax.add_patch(mon_box)
    ax.text(11.5, 4.7, 'Observability', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#6B7280')
    
    mon_services = [('Cloud\nMonitoring', 10.3, 3.3), ('Cloud\nLogging', 12.0, 3.0)]
    for name, x, y in mon_services:
        box = FancyBboxPatch((x, y - 0.4), 1.3, 0.8, boxstyle="round,pad=0.02",
                              facecolor='white', edgecolor='#6B7280', linewidth=1)
        ax.add_patch(box)
        ax.text(x + 0.65, y, name, ha='center', va='center', fontsize=8, fontweight='bold', color=COLORS['dark'])
    
    # External: Users
    users_box = FancyBboxPatch((5.5, 8.5), 3, 1, boxstyle="round,pad=0.02",
                                facecolor=COLORS['primary'], edgecolor=COLORS['dark'], linewidth=2)
    ax.add_patch(users_box)
    ax.text(7, 9.0, 'Users (Web App)', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    
    # CDN
    ax.text(7, 8.3, '↓ Cloud CDN + Load Balancer', ha='center', va='center', fontsize=9, color=COLORS['dark'])
    
    # Scale indicators
    ax.text(0.5, 1.2, 'Auto-scaling: 0-100 instances | Region: EU | SLA: 99.9%', 
            ha='left', va='center', fontsize=9, style='italic', color=COLORS['dark'])
    
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
    story.append(Paragraph("Tehnična Arhitekturna Dokumentacija", 
                          ParagraphStyle('Subtitle', fontSize=16, alignment=TA_CENTER, 
                                        textColor=colors.HexColor(COLORS['dark']))))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("AI-Powered Scoping Review Platform", 
                          ParagraphStyle('Sub2', fontSize=14, alignment=TA_CENTER,
                                        textColor=colors.HexColor(COLORS['secondary']))))
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
        ('FONTNAME', (0, 0), (-1, 0), 'SegoeUIBold'),
        ('FONTNAME', (0, 1), (-1, -1), 'SegoeUI'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['light'])),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(toc_table)
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(f"Verzija 2.3 | April 2026", 
                          ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, textColor=colors.gray)))
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
        ('FONTNAME', (0, 0), (-1, 0), 'SegoeUIBold'),
        ('FONTNAME', (0, 1), (-1, -1), 'SegoeUI'),
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
        story.append(Image(images['high_level'], width=16*cm, height=13*cm))
    
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
        story.append(Image(images['multi_agent'], width=16*cm, height=12*cm))
    
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
        story.append(Image(images['rag'], width=16*cm, height=12*cm))
    
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
        story.append(Image(images['workflow'], width=16*cm, height=11*cm))
    
    story.append(Paragraph("Faze in HITL točke:", heading2_style))
    workflow_desc = [
        "1. <b>Research Plan:</b> Definicija vprašanj, PICO kriteriji → HITL #1 validacija",
        "2. <b>Search Strings:</b> Generacija Boolean izrazov → HITL #2 pregled sintakse",
        "3. <b>Abstract Screening:</b> AI kategorizacija → HITL #3 odločitve",
        "4. <b>Full-text ID:</b> DOI resolucija, pridobivanje PDF-jev",
        "5. <b>Full-text Ingestion:</b> Parsing, chunking → HITL #4 quality check",
        "6. <b>Gap Analysis:</b> Identifikacija vrzeli, teme → HITL #5 validacija tem",
        "7. <b>Article Generation:</b> Pisanje sekcij → HITL #6-7 pregled vsebine",
        "8. <b>Export:</b> PDF/DOCX, vizualizacije → HITL #8-10 končni pregled",
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
        story.append(Image(images['hitl'], width=16*cm, height=11*cm))
    
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
        "<b>Vhod:</b> PDF dokumenti, research plan, uporabniški vnosi → Processing Layer",
        "<b>Obdelava:</b> Parse → Chunk → Embed → Index cikl z validacijo",
        "<b>Shranjevanje:</b> Firestore (metadata), ChromaDB (vektorji), Cloud Storage (datoteke)",
        "<b>AI Generacija:</b> RAG retrieval → LLM generate → Validate → Output",
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
        "ResearchFlow je deployane na Google Cloud Platform v EU regiji (europe-west1) "
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
        "<b>4. Generate Strings:</b> AI generira Boolean iskalne nize → uporabnik validira",
        "<b>5. Import Results:</b> Upload .ris/.csv iz WoS/Scopus/PubMed",
        "<b>6. Screening:</b> AI kategorizira abstrakte → uporabnik potrdi/zavrne",
        "<b>7. Full-text:</b> Upload PDF-jev → sistem parsira in indexira",
        "<b>8. Analysis:</b> AI identificira teme in vrzeli → uporabnik validira",
        "<b>9. Writing:</b> AI piše sekcije članka → uporabnik pregleduje/editira",
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
    print("ResearchFlow Architecture Presentation Generator")
    print("=" * 60)
    
    images = {}
    
    print("\n[1/10] Creating high-level architecture...")
    images['high_level'] = create_high_level_architecture()
    print(f"       ✓ Saved")
    
    print("\n[2/10] Creating multi-agent architecture...")
    images['multi_agent'] = create_multi_agent_architecture()
    print(f"       ✓ Saved")
    
    print("\n[3/10] Creating memory architecture...")
    images['memory'] = create_memory_architecture()
    print(f"       ✓ Saved")
    
    print("\n[4/10] Creating RAG architecture...")
    images['rag'] = create_rag_architecture()
    print(f"       ✓ Saved")
    
    print("\n[5/10] Creating workflow pipeline...")
    images['workflow'] = create_workflow_pipeline()
    print(f"       ✓ Saved")
    
    print("\n[6/10] Creating HITL architecture...")
    images['hitl'] = create_hitl_architecture()
    print(f"       ✓ Saved")
    
    print("\n[7/10] Creating data flow diagram...")
    images['data_flow'] = create_data_flow()
    print(f"       ✓ Saved")
    
    print("\n[8/10] Creating security architecture...")
    images['security'] = create_security_architecture()
    print(f"       ✓ Saved")
    
    print("\n[9/10] Creating deployment architecture...")
    images['deployment'] = create_deployment_architecture()
    print(f"       ✓ Saved")
    
    print("\n[10/10] Creating user journey...")
    images['user_journey'] = create_user_journey()
    print(f"       ✓ Saved")
    
    print("\n" + "=" * 60)
    print("Generating architecture PDF (A4, 12 pages)...")
    pdf_path = create_architecture_pdf(images)
    print(f"✓ PDF saved to: {pdf_path}")
    print("=" * 60)
    
    return pdf_path


if __name__ == "__main__":
    main()
