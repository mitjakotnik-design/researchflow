#!/usr/bin/env python3
"""
ResearchFlow - Professional PDF Presentation Generator
Creates a comprehensive presentation with visualizations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from datetime import datetime

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "presentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
COLORS = {
    'primary': '#2563EB',      # Blue
    'secondary': '#7C3AED',    # Purple
    'accent': '#10B981',       # Green
    'warning': '#F59E0B',      # Orange
    'danger': '#EF4444',       # Red
    'dark': '#1F2937',         # Dark gray
    'light': '#F3F4F6',        # Light gray
    'white': '#FFFFFF',
}

def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple (0-1 range)"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))


# ============================================================================
# VISUALIZATION GENERATION
# ============================================================================

def create_radar_chart():
    """Create competitive radar chart"""
    categories = ['Funkcionalnosti', 'AI zmogljivosti', 'Cena/Vrednost', 
                  'Varnost/GDPR', 'Hitrost', 'Integracije', 'UX', 'Podpora']
    
    # Data for each tool (normalized 0-10)
    researchflow = [9.3, 9.2, 8.5, 6.8, 7.0, 8.0, 8.5, 5.5]
    rayyan = [3.2, 2.5, 7.0, 2.9, 6.5, 6.0, 8.0, 7.0]
    covidence = [5.0, 0.4, 4.5, 4.3, 6.0, 6.5, 5.5, 7.0]
    distillersr = [5.4, 3.3, 2.0, 6.4, 6.5, 8.0, 5.5, 9.0]
    elicit = [1.4, 5.0, 5.0, 4.6, 7.0, 6.5, 7.5, 7.5]
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    # Close the plots
    researchflow += researchflow[:1]
    rayyan += rayyan[:1]
    covidence += covidence[:1]
    distillersr += distillersr[:1]
    elicit += elicit[:1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(polar=True))
    
    # Draw the chart
    ax.plot(angles, researchflow, 'o-', linewidth=3, label='ResearchFlow', color=COLORS['primary'])
    ax.fill(angles, researchflow, alpha=0.25, color=COLORS['primary'])
    
    ax.plot(angles, rayyan, 'o-', linewidth=2, label='Rayyan', color='#FF6B6B')
    ax.plot(angles, covidence, 'o-', linewidth=2, label='Covidence', color='#4ECDC4')
    ax.plot(angles, distillersr, 'o-', linewidth=2, label='DistillerSR', color='#45B7D1')
    ax.plot(angles, elicit, 'o-', linewidth=2, label='Elicit', color='#96CEB4')
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=11, fontweight='bold')
    
    # Set y-axis
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=9)
    
    # Title and legend
    plt.title('Konkurenčna primerjava po kategorijah\n', size=16, fontweight='bold', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "radar_chart.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_market_size_chart():
    """Create market size funnel chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Data
    labels = ['TAM\nGlobal Academic Research\n$4.5B', 
              'SAM\nSR/Scoping Review Tools\n$350M',
              'SOM\n5-Year Target\n$5-15M']
    values = [4500, 350, 10]
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    
    # Create funnel
    y_positions = [0.7, 0.4, 0.1]
    widths = [0.9, 0.6, 0.3]
    
    for i, (label, value, y, width, color) in enumerate(zip(labels, values, y_positions, widths, colors_list)):
        # Draw trapezoid
        left = (1 - width) / 2
        rect = FancyBboxPatch((left, y - 0.08), width, 0.16, 
                               boxstyle="round,pad=0.02", 
                               facecolor=color, edgecolor='white', linewidth=3)
        ax.add_patch(rect)
        
        # Add text
        ax.text(0.5, y, label, ha='center', va='center', 
                fontsize=14, fontweight='bold', color='white')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Tržni potencial (TAM → SAM → SOM)', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "market_funnel.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_workflow_diagram():
    """Create workflow pipeline diagram"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    phases = [
        ('1. Raziskovalni\nnačrt', COLORS['primary'], 'HITL #1'),
        ('2. Iskalni\nnizi', COLORS['primary'], 'HITL #2'),
        ('3. Abstract\nScreening', COLORS['secondary'], 'HITL #3'),
        ('4. Full-text\nID', COLORS['secondary'], ''),
        ('5. Full-text\nIngestion', COLORS['accent'], 'HITL #4'),
        ('6. Gap\nAnalysis', COLORS['accent'], 'HITL #5'),
        ('7. Article\nGeneration', COLORS['warning'], 'HITL #6-7'),
        ('8. Export\n& Viz', COLORS['danger'], 'HITL #8-10'),
    ]
    
    # Draw phases
    box_width = 0.1
    box_height = 0.15
    spacing = 0.115
    y_center = 0.5
    
    for i, (name, color, hitl) in enumerate(phases):
        x = 0.05 + i * spacing
        
        # Main box
        rect = FancyBboxPatch((x, y_center - box_height/2), box_width, box_height,
                               boxstyle="round,pad=0.01", 
                               facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        
        # Phase name
        ax.text(x + box_width/2, y_center, name, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')
        
        # HITL indicator
        if hitl:
            ax.text(x + box_width/2, y_center - box_height/2 - 0.05, hitl,
                    ha='center', va='center', fontsize=8, color=COLORS['dark'],
                    bbox=dict(boxstyle='round', facecolor='#FEF3C7', edgecolor='#F59E0B'))
        
        # Arrow to next
        if i < len(phases) - 1:
            ax.annotate('', xy=(x + spacing - 0.005, y_center),
                       xytext=(x + box_width + 0.005, y_center),
                       arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))
    
    # Title
    ax.text(0.5, 0.85, 'ResearchFlow: 8-fazni Workflow Pipeline', 
            ha='center', fontsize=18, fontweight='bold', transform=ax.transAxes)
    
    ax.text(0.5, 0.2, '10 HITL Decision Points • AI-Powered • Transparent Reasoning',
            ha='center', fontsize=12, style='italic', color=COLORS['dark'], transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "workflow_diagram.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_architecture_diagram():
    """Create system architecture diagram"""
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Layers
    layers = [
        (0.85, 'FRONTEND (Next.js 14)', ['Chatbot', 'Article Viewer', 'Statistics', 'HITL Panel'], COLORS['primary']),
        (0.70, 'API GATEWAY (Cloud Run)', ['Auth', 'Rate Limiting', 'Validation', 'CORS'], '#6B7280'),
        (0.55, 'BACKEND SERVICES', ['Orchestration', 'RAG Service', 'Agent Cluster', 'HITL Manager'], COLORS['secondary']),
        (0.40, 'DATA LAYER', ['Firestore', 'Cloud Storage', 'ChromaDB', 'Redis'], COLORS['accent']),
        (0.25, 'SECURITY', ['TLS 1.3', 'Cloud Armor', 'PromptGuard', 'Audit Logs'], COLORS['danger']),
        (0.10, 'OBSERVABILITY', ['Cloud Monitoring', 'Logging', 'Alerting', 'Dashboards'], '#8B5CF6'),
    ]
    
    for y, title, components, color in layers:
        # Main layer box
        rect = FancyBboxPatch((0.05, y - 0.05), 0.9, 0.1,
                               boxstyle="round,pad=0.01",
                               facecolor=color, alpha=0.2, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # Title
        ax.text(0.07, y + 0.02, title, fontsize=12, fontweight='bold', color=color)
        
        # Components
        comp_spacing = 0.85 / len(components)
        for i, comp in enumerate(components):
            x = 0.1 + i * comp_spacing
            comp_box = FancyBboxPatch((x, y - 0.035), comp_spacing - 0.02, 0.05,
                                       boxstyle="round,pad=0.005",
                                       facecolor=color, alpha=0.7, edgecolor='white')
            ax.add_patch(comp_box)
            ax.text(x + (comp_spacing - 0.02)/2, y - 0.01, comp, 
                    ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('ResearchFlow Sistemska Arhitektura', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "architecture_diagram.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_pricing_comparison():
    """Create pricing comparison chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    tools = ['ResearchFlow\nPro', 'Rayyan\nAdvanced', 'Covidence\nSingle', 'Elicit\nPro', 'DistillerSR\nAcademic']
    prices = [350, 100, 339, 588, 4000]
    colors_list = [COLORS['accent'], '#FF6B6B', '#4ECDC4', '#96CEB4', '#45B7D1']
    
    bars = ax.bar(tools, prices, color=colors_list, edgecolor='white', linewidth=2)
    
    # Add value labels
    for bar, price in zip(bars, prices):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'${price}/leto', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add feature indicators
    features = ['Full Pipeline\n+ AI Generation', 'Samo\nScreening', 'SR Workflow\nNo AI Gen', 'AI Assistant\nNo Workflow', 'Enterprise\nNo AI Gen']
    for i, (bar, feat) in enumerate(zip(bars, features)):
        ax.text(bar.get_x() + bar.get_width()/2, 100,
                feat, ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')
    
    ax.set_ylabel('Letna cena (USD)', fontsize=12, fontweight='bold')
    ax.set_title('Primerjava cen in funkcionalnosti', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 4500)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "pricing_comparison.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_feature_matrix():
    """Create feature comparison matrix heatmap"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Features and tools
    features = [
        'Research Plan Creation',
        'Search String Generation',
        'Abstract Screening',
        'Full-text Analysis',
        'AI Article Generation',
        'RAG Chatbot',
        'HITL Workflow',
        'PRISMA Diagram',
        'Evidence Gap Map',
        'PDF Export',
        'Visible Reasoning',
        'EU Data Residency',
    ]
    
    tools = ['ResearchFlow', 'Rayyan', 'Covidence', 'DistillerSR', 'ASReview', 'Elicit']
    
    # Data: 2 = Full, 1 = Partial, 0 = No
    data = np.array([
        [2, 0, 1, 1, 0, 0],  # Research Plan
        [2, 0, 0, 0, 0, 0],  # Search String
        [2, 2, 2, 2, 2, 1],  # Abstract Screening
        [2, 0, 2, 2, 0, 0],  # Full-text
        [2, 0, 0, 0, 0, 0],  # AI Article - UNIQUE!
        [2, 0, 0, 0, 0, 2],  # RAG Chatbot
        [2, 1, 2, 2, 1, 0],  # HITL
        [2, 2, 2, 2, 0, 0],  # PRISMA
        [2, 0, 0, 1, 0, 0],  # Evidence Gap
        [2, 0, 1, 2, 0, 0],  # PDF Export
        [2, 0, 0, 0, 1, 1],  # Reasoning
        [2, 0, 1, 1, 2, 0],  # EU Data
    ])
    
    # Create custom colormap
    cmap = LinearSegmentedColormap.from_list('custom', ['#FEE2E2', '#FEF3C7', '#D1FAE5'])
    
    im = ax.imshow(data, cmap=cmap, aspect='auto')
    
    # Labels
    ax.set_xticks(np.arange(len(tools)))
    ax.set_yticks(np.arange(len(features)))
    ax.set_xticklabels(tools, fontsize=11, fontweight='bold')
    ax.set_yticklabels(features, fontsize=10)
    
    # Add text annotations
    for i in range(len(features)):
        for j in range(len(tools)):
            text = '✓' if data[i, j] == 2 else ('◐' if data[i, j] == 1 else '✗')
            color = '#065F46' if data[i, j] == 2 else ('#92400E' if data[i, j] == 1 else '#991B1B')
            ax.text(j, i, text, ha='center', va='center', fontsize=14, color=color, fontweight='bold')
    
    # Highlight ResearchFlow column
    ax.axvline(x=-0.5, color=COLORS['primary'], linewidth=3)
    ax.axvline(x=0.5, color=COLORS['primary'], linewidth=3)
    
    ax.set_title('Primerjava funkcionalnosti', fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#D1FAE5', edgecolor='gray', label='✓ Polna podpora'),
        mpatches.Patch(facecolor='#FEF3C7', edgecolor='gray', label='◐ Delna podpora'),
        mpatches.Patch(facecolor='#FEE2E2', edgecolor='gray', label='✗ Ni podpore'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "feature_matrix.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_timeline_chart():
    """Create implementation timeline Gantt chart"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    phases = [
        ('Phase 1: Foundation', 1, 2, COLORS['primary']),
        ('Phase 2: Core Backend', 3, 4, COLORS['primary']),
        ('Phase 3: Agent Enhancement', 5, 6, COLORS['secondary']),
        ('Phase 4: Frontend Dev', 7, 8, COLORS['secondary']),
        ('Phase 5: Integration', 9, 11, COLORS['accent']),
        ('Phase 6: Security', 12, 14, COLORS['warning']),
        ('Phase 7: Testing & QA', 15, 17, COLORS['danger']),
        ('Phase 8: Launch', 18, 20, '#8B5CF6'),
    ]
    
    milestones = [
        (4, 'MVP Backend'),
        (8, 'MVP Frontend'),
        (11, 'Feature Complete'),
        (14, 'Security Audit'),
        (17, 'QA Complete'),
        (20, 'Production Launch'),
    ]
    
    y_positions = range(len(phases), 0, -1)
    
    for i, (name, start, end, color) in enumerate(phases):
        y = y_positions[i]
        # Phase bar
        ax.barh(y, end - start + 1, left=start, height=0.6, 
                color=color, edgecolor='white', linewidth=2)
        # Phase name
        ax.text(start - 0.5, y, name, ha='right', va='center', fontsize=10, fontweight='bold')
        # Week range
        ax.text((start + end) / 2 + 0.5, y, f'W{start}-W{end}', 
                ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    
    # Milestones
    for week, name in milestones:
        ax.axvline(x=week, color='gray', linestyle='--', alpha=0.5)
        ax.text(week, len(phases) + 0.8, name, ha='center', va='bottom', 
                fontsize=8, rotation=45, color=COLORS['dark'])
    
    ax.set_xlim(0, 22)
    ax.set_ylim(0, len(phases) + 2)
    ax.set_xlabel('Tedni', fontsize=12, fontweight='bold')
    ax.set_xticks(range(0, 22, 2))
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_title('Implementacijski načrt (20 tednov)', fontsize=16, fontweight='bold', pad=40)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "timeline_chart.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_swot_diagram():
    """Create SWOT analysis diagram"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    swot_data = {
        'PREDNOSTI (S)': [
            '• Multi-agent sistem že deluje',
            '• HITL pristop za kakovost',
            '• Cloud-native arhitektura',
            '• RAG za transparentnost',
            '• GDPR-ready zasnova',
        ],
        'SLABOSTI (W)': [
            '• Odvisnost od Vertex AI',
            '• Kompleksna arhitektura',
            '• Ni offline načina',
            '• PDF parsing omejitve',
            '• Manjka mobile app',
        ],
        'PRILOŽNOSTI (O)': [
            '• Rastoč trg AI research (25%)',
            '• Univerze iščejo avtomatizacijo',
            '• White-label za institucije',
            '• Razširitev na meta-analize',
            '• Grant funding možnosti',
        ],
        'GROŽNJE (T)': [
            '• Konkurenca (Elsevier, Clarivate)',
            '• API breaking changes',
            '• Regulatorne spremembe (AI Act)',
            '• Akademiki skeptični do AI',
            '• Hallucination tveganja',
        ],
    }
    
    titles = list(swot_data.keys())
    colors_list = [COLORS['accent'], COLORS['warning'], COLORS['primary'], COLORS['danger']]
    
    for ax, title, color in zip(axes.flat, titles, colors_list):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Background
        rect = FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                               boxstyle="round,pad=0.02",
                               facecolor=color, alpha=0.15, edgecolor=color, linewidth=3)
        ax.add_patch(rect)
        
        # Title
        ax.text(0.5, 0.92, title, ha='center', va='top', 
                fontsize=14, fontweight='bold', color=color)
        
        # Items
        items = swot_data[title]
        for i, item in enumerate(items):
            y = 0.78 - i * 0.15
            ax.text(0.08, y, item, ha='left', va='top', fontsize=11, color=COLORS['dark'])
    
    plt.suptitle('SWOT Analiza', fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()
    filepath = OUTPUT_DIR / "swot_diagram.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_cost_breakdown():
    """Create cost breakdown pie chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    # Monthly costs
    services = ['Cloud Run', 'Firestore', 'Vertex AI', 'Memorystore', 'Storage', 'Other']
    costs = [65, 40, 225, 35, 8, 12]
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['warning'], 
                   COLORS['accent'], COLORS['danger'], '#6B7280']
    explode = (0, 0, 0.1, 0, 0, 0)  # Highlight Vertex AI
    
    wedges, texts, autotexts = ax1.pie(costs, labels=services, autopct='%1.1f%%',
                                        colors=colors_list, explode=explode,
                                        shadow=True, startangle=90)
    ax1.set_title(f'Mesečni stroški infrastrukture\n(Total: ${sum(costs)}/mo)', 
                  fontsize=14, fontweight='bold')
    
    # Revenue projection
    years = ['Y1', 'Y2', 'Y3', 'Y4', 'Y5']
    arr = [60, 300, 960, 2200, 4200]  # in thousands
    
    bars = ax2.bar(years, arr, color=COLORS['accent'], edgecolor='white', linewidth=2)
    for bar, revenue in zip(bars, arr):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'${revenue}K', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_ylabel('ARR ($ thousands)', fontsize=12, fontweight='bold')
    ax2.set_title('Projekcija prihodkov (5-letna)', fontsize=14, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "cost_breakdown.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


def create_competitive_scores():
    """Create competitive scores bar chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    tools = ['ResearchFlow', 'DistillerSR', 'Rayyan', 'ASReview', 'Elicit', 'Covidence']
    scores = [8.4, 4.7, 4.4, 4.4, 4.4, 4.0]
    colors_list = [COLORS['accent']] + [COLORS['primary']] * 5
    
    bars = ax.barh(tools, scores, color=colors_list, edgecolor='white', linewidth=2)
    
    # Add score labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{score:.1f}/10', ha='left', va='center', fontsize=12, fontweight='bold')
    
    # Highlight winner
    ax.text(scores[0] / 2, 5.5, '★ WINNER', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    
    ax.set_xlim(0, 10)
    ax.set_xlabel('Weighted Total Score', fontsize=12, fontweight='bold')
    ax.set_title('Končna konkurenčna razvrstitev', fontsize=16, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()
    
    plt.tight_layout()
    filepath = OUTPUT_DIR / "competitive_scores.png"
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return str(filepath)


# ============================================================================
# PDF GENERATION
# ============================================================================

def create_pdf_presentation(images):
    """Create the final PDF presentation"""
    
    filepath = OUTPUT_DIR / "ResearchFlow_Presentation.pdf"
    
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['primary']),
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['dark']),
        spaceAfter=20,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=24,
        alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['primary']),
        spaceBefore=20,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor(COLORS['dark']),
        spaceAfter=10,
        leading=16,
        fontName='Helvetica'
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_LEFT,
        textColor=colors.HexColor(COLORS['dark']),
        spaceAfter=8,
        leftIndent=20,
        bulletIndent=10,
        fontName='Helvetica'
    )
    
    # Build content
    story = []
    
    # ==================== SLIDE 1: Title ====================
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("ResearchFlow", title_style))
    story.append(Paragraph("AI-Powered Scoping Review Platform", subtitle_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Komercialna platforma za avtomatizirano pisanje znanstvenih preglednih člankov",
        ParagraphStyle('Center', alignment=TA_CENTER, fontSize=14, textColor=colors.HexColor(COLORS['dark']))
    ))
    story.append(Spacer(1, 2*cm))
    
    # Key stats
    stats_data = [
        ['8 Faz', '10 HITL', 'AI Gen', 'GDPR'],
        ['Workflow', 'Decision Points', 'Člankov', 'Compliant'],
    ]
    stats_table = Table(stats_data, colWidths=[5*cm, 5*cm, 5*cm, 5*cm])
    stats_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 24),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor(COLORS['dark'])),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        f"Verzija 2.3 | April 2026",
        ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=10, textColor=colors.gray)
    ))
    story.append(PageBreak())
    
    # ==================== SLIDE 2: Problem & Solution ====================
    story.append(Paragraph("Problem & Rešitev", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    problem_solution = [
        ['PROBLEM', 'REŠITEV'],
        ['Pisanje scoping reviewa traja 6-12 mesecev', 'AI-podprta generacija v tednih'],
        ['Manualno pregledovanje 1000+ abstraktov', 'AI screening z HITL validacijo'],
        ['Ročno oblikovanje iskalnih nizov', 'Avtomatska generacija za WoS, Scopus, PubMed'],
        ['Nepreglednost AI odločitev', 'Transparentni reasoning traces'],
        ['Draga orodja (Covidence: $339/review)', 'Dostopna cena ($29-99/mesec)'],
    ]
    
    ps_table = Table(problem_solution, colWidths=[12*cm, 12*cm])
    ps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(COLORS['danger'])),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(COLORS['accent'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FEE2E2'), colors.HexColor('#D1FAE5')]),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(ps_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 3: Workflow ====================
    story.append(Paragraph("8-Fazni Workflow Pipeline", heading_style))
    if 'workflow' in images:
        story.append(Image(images['workflow'], width=26*cm, height=14*cm))
    story.append(PageBreak())
    
    # ==================== SLIDE 4: Architecture ====================
    story.append(Paragraph("Sistemska Arhitektura", heading_style))
    if 'architecture' in images:
        story.append(Image(images['architecture'], width=26*cm, height=16*cm))
    story.append(PageBreak())
    
    # ==================== SLIDE 5: Key Features ====================
    story.append(Paragraph("Ključne Funkcionalnosti", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    features_data = [
        ['Funkcionalnost', 'Opis', 'Edinstveno?'],
        ['AI Article Generation', 'Avtomatska generacija celotnega članka z viri', '✓ DA'],
        ['RAG Chatbot', 'Dostop do vseh dokumentov in reasoning traces', '✓ DA'],
        ['10 HITL Decision Points', 'Človeški nadzor na vsakem kritičnem koraku', '✓ DA'],
        ['Search String Generator', 'Avtomatska generacija za WoS, Scopus, PubMed', '✓ DA'],
        ['Abstract Screening', 'AI-assisted s kategorizacijo Include/Exclude/Uncertain', 'Shared'],
        ['Visualization Suite', 'PRISMA, Evidence Gap Map, Conceptual Model', '✓ DA'],
        ['PDF/DOCX Export', 'Publication-ready izvoz z inline slikami', 'Shared'],
    ]
    
    features_table = Table(features_data, colWidths=[7*cm, 13*cm, 4*cm])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['light'])),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(features_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 6: Feature Matrix ====================
    story.append(Paragraph("Primerjava Funkcionalnosti", heading_style))
    if 'feature_matrix' in images:
        story.append(Image(images['feature_matrix'], width=24*cm, height=16*cm))
    story.append(PageBreak())
    
    # ==================== SLIDE 7: Radar Chart ====================
    story.append(Paragraph("Konkurenčna Primerjava", heading_style))
    if 'radar' in images:
        story.append(Image(images['radar'], width=22*cm, height=15*cm))
    story.append(PageBreak())
    
    # ==================== SLIDE 8: Competitive Scores ====================
    story.append(Paragraph("Končna Razvrstitev", heading_style))
    if 'scores' in images:
        story.append(Image(images['scores'], width=22*cm, height=14*cm))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "ResearchFlow dosega <b>8.4/10</b> - najvišjo oceno med vsemi konkurenti. "
        "Kot edini ponuja celoten pipeline od raziskovalnega načrta do publication-ready PDF z AI generacijo članka.",
        body_style
    ))
    story.append(PageBreak())
    
    # ==================== SLIDE 9: Pricing ====================
    story.append(Paragraph("Cenovna Primerjava", heading_style))
    if 'pricing' in images:
        story.append(Image(images['pricing'], width=22*cm, height=14*cm))
    story.append(Spacer(1, 0.5*cm))
    
    pricing_comparison = [
        ['ResearchFlow Pro', 'Covidence Single', 'DistillerSR Academic'],
        ['$29-99/mesec', '$339/review', '$4,000+/leto'],
        ['$350-1,200/leto', '$1,000-2,000/leto', '$4,000-10,000/leto'],
        ['60-80% ceneje!', '', ''],
    ]
    pricing_table = Table(pricing_comparison, colWidths=[8*cm, 8*cm, 8*cm])
    pricing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TEXTCOLOR', (0, 3), (0, 3), colors.HexColor(COLORS['accent'])),
        ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
    ]))
    story.append(pricing_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 10: Market Potential ====================
    story.append(Paragraph("Tržni Potencial", heading_style))
    if 'market' in images:
        story.append(Image(images['market'], width=20*cm, height=12*cm))
    story.append(Spacer(1, 0.5*cm))
    
    market_points = [
        "• <b>TAM:</b> Global Academic Research Software - $4.5B (2026)",
        "• <b>SAM:</b> Systematic/Scoping Review Tools - $350M (20-25% CAGR)",
        "• <b>SOM:</b> 5-letni cilj - $5-15M ARR, 10,000-30,000 uporabnikov",
        "• <b>Target:</b> PhD študenti (500K+), postdoki (200K+), raziskovalne skupine",
    ]
    for point in market_points:
        story.append(Paragraph(point, bullet_style))
    story.append(PageBreak())
    
    # ==================== SLIDE 11: SWOT ====================
    story.append(Paragraph("SWOT Analiza", heading_style))
    if 'swot' in images:
        story.append(Image(images['swot'], width=24*cm, height=16*cm))
    story.append(PageBreak())
    
    # ==================== SLIDE 12: Timeline ====================
    story.append(Paragraph("Implementacijski Načrt", heading_style))
    if 'timeline' in images:
        story.append(Image(images['timeline'], width=26*cm, height=14*cm))
    story.append(PageBreak())
    
    # ==================== SLIDE 13: Cost & Revenue ====================
    story.append(Paragraph("Finančni Pregled", heading_style))
    if 'costs' in images:
        story.append(Image(images['costs'], width=24*cm, height=12*cm))
    story.append(Spacer(1, 0.5*cm))
    
    financial_summary = [
        ['Metrika', 'Vrednost'],
        ['Mesečni stroški (100 users)', '$280-490'],
        ['Break-even point', '~50 paying users'],
        ['Y1 ARR cilj', '$60K'],
        ['Y5 ARR cilj', '$4.2M'],
        ['CAC target', '< $50'],
        ['LTV target', '> $200'],
    ]
    fin_table = Table(financial_summary, colWidths=[10*cm, 8*cm])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['light'])),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(fin_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 14: Tech Stack ====================
    story.append(Paragraph("Tehnološki Stack", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    tech_data = [
        ['Kategorija', 'Tehnologije'],
        ['Backend', 'Python 3.11+, FastAPI, LangChain'],
        ['Frontend', 'Next.js 14, React, Tailwind CSS, shadcn/ui'],
        ['LLM', 'Vertex AI (Gemini 2.5 Flash/Pro)'],
        ['Vector DB', 'ChromaDB / Vertex AI Matching Engine'],
        ['Database', 'Firestore (NoSQL)'],
        ['Cache', 'Memorystore (Redis)'],
        ['Storage', 'Cloud Storage (EU)'],
        ['Auth', 'Firebase Authentication'],
        ['CI/CD', 'Cloud Build + Terraform'],
        ['Monitoring', 'Cloud Monitoring, Logging, Trace'],
        ['Security', 'Cloud Armor WAF, VPC Service Controls'],
    ]
    tech_table = Table(tech_data, colWidths=[6*cm, 18*cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['secondary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F3E8FF')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tech_table)
    story.append(PageBreak())
    
    # ==================== SLIDE 15: Security ====================
    story.append(Paragraph("Varnost & Skladnost", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    security_points = [
        "<b>GDPR Compliant:</b> EU data residency (europe-west1), data export/deletion API",
        "<b>Authentication:</b> Firebase Auth z MFA, OAuth (Google, Microsoft)",
        "<b>Encryption:</b> TLS 1.3 in transit, AES-256 at rest",
        "<b>AI Security:</b> EnhancedPromptGuard (regex + LLM-based injection detection)",
        "<b>Access Control:</b> Role-based (Owner, Editor, Reviewer, Viewer)",
        "<b>Audit:</b> Complete audit logging to Firestore + BigQuery",
        "<b>Infrastructure:</b> VPC Service Controls, Cloud Armor WAF",
        "<b>Certifications:</b> SOC 2 (planned), HIPAA (optional enterprise tier)",
    ]
    
    for point in security_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    story.append(PageBreak())
    
    # ==================== SLIDE 16: Call to Action ====================
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Zakaj ResearchFlow?", title_style))
    story.append(Spacer(1, 1*cm))
    
    cta_points = [
        "✓ <b>EDINI</b> z AI generacijo celotnega članka",
        "✓ <b>EDINI</b> s celotnim pipelineom (research plan → PDF)",
        "✓ <b>10 HITL</b> decision points za popoln nadzor",
        "✓ <b>60-80%</b> ceneje od enterprise konkurentov",
        "✓ <b>GDPR native</b> z EU data residency",
        "✓ <b>Transparentno:</b> vidni reasoning traces",
    ]
    
    cta_style = ParagraphStyle(
        'CTA',
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor(COLORS['dark']),
        spaceAfter=15,
        fontName='Helvetica'
    )
    
    for point in cta_points:
        story.append(Paragraph(point, cta_style))
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        "Weighted Total Score: <b>8.4/10</b> | Tier: <b>S (Category Creator)</b>",
        ParagraphStyle('Score', fontSize=20, alignment=TA_CENTER, 
                      textColor=colors.HexColor(COLORS['accent']), fontName='Helvetica-Bold')
    ))
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        "GitHub: github.com/mitjakotnik-design/researchflow",
        ParagraphStyle('GitHub', fontSize=12, alignment=TA_CENTER, 
                      textColor=colors.HexColor(COLORS['primary']))
    ))
    
    # Build PDF
    doc.build(story)
    
    return str(filepath)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function to generate all visualizations and PDF"""
    print("=" * 60)
    print("ResearchFlow Presentation Generator")
    print("=" * 60)
    
    # Generate all visualizations
    print("\n[1/10] Creating radar chart...")
    radar_path = create_radar_chart()
    print(f"       ✓ Saved: {radar_path}")
    
    print("\n[2/10] Creating market funnel...")
    market_path = create_market_size_chart()
    print(f"       ✓ Saved: {market_path}")
    
    print("\n[3/10] Creating workflow diagram...")
    workflow_path = create_workflow_diagram()
    print(f"       ✓ Saved: {workflow_path}")
    
    print("\n[4/10] Creating architecture diagram...")
    architecture_path = create_architecture_diagram()
    print(f"       ✓ Saved: {architecture_path}")
    
    print("\n[5/10] Creating pricing comparison...")
    pricing_path = create_pricing_comparison()
    print(f"       ✓ Saved: {pricing_path}")
    
    print("\n[6/10] Creating feature matrix...")
    feature_matrix_path = create_feature_matrix()
    print(f"       ✓ Saved: {feature_matrix_path}")
    
    print("\n[7/10] Creating timeline chart...")
    timeline_path = create_timeline_chart()
    print(f"       ✓ Saved: {timeline_path}")
    
    print("\n[8/10] Creating SWOT diagram...")
    swot_path = create_swot_diagram()
    print(f"       ✓ Saved: {swot_path}")
    
    print("\n[9/10] Creating cost breakdown...")
    cost_path = create_cost_breakdown()
    print(f"       ✓ Saved: {cost_path}")
    
    print("\n[10/10] Creating competitive scores...")
    scores_path = create_competitive_scores()
    print(f"       ✓ Saved: {scores_path}")
    
    # Collect all image paths
    images = {
        'radar': radar_path,
        'market': market_path,
        'workflow': workflow_path,
        'architecture': architecture_path,
        'pricing': pricing_path,
        'feature_matrix': feature_matrix_path,
        'timeline': timeline_path,
        'swot': swot_path,
        'costs': cost_path,
        'scores': scores_path,
    }
    
    # Generate PDF
    print("\n" + "=" * 60)
    print("Generating PDF presentation...")
    pdf_path = create_pdf_presentation(images)
    print(f"✓ PDF saved to: {pdf_path}")
    print("=" * 60)
    
    return pdf_path


if __name__ == "__main__":
    main()
