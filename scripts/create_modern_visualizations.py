"""
Modern visualizations for scoping review article.
Uses: Plotly, Altair, Graphviz, NetworkX, WordCloud
Author: AI Assistant
Date: April 2026
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import altair as alt
import pandas as pd
import numpy as np
from pathlib import Path
import networkx as nx
from graphviz import Digraph
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Output directory
output_dir = Path("output/figures_modern")
output_dir.mkdir(parents=True, exist_ok=True)

# Color palettes - professional academic style
COLORS = {
    'primary': '#2C3E50',      # Dark blue-gray
    'secondary': '#3498DB',    # Bright blue
    'accent1': '#E74C3C',      # Red
    'accent2': '#27AE60',      # Green
    'accent3': '#F39C12',      # Orange
    'accent4': '#9B59B6',      # Purple
    'light': '#ECF0F1',        # Light gray
    'gradient': ['#667eea', '#764ba2'],  # Modern gradient
}

ACADEMIC_PALETTE = ['#2C3E50', '#3498DB', '#27AE60', '#E74C3C', '#F39C12', '#9B59B6']


def create_prisma_sankey():
    """
    Create PRISMA flow diagram as Sankey diagram.
    Modern, clean, publication-ready.
    """
    print("  Creating PRISMA Sankey diagram...")
    
    # Define the flow
    labels = [
        "Database Records<br>(n=2,847)",           # 0
        "Other Sources<br>(n=156)",                # 1
        "Total Records<br>(n=3,003)",              # 2
        "Duplicates Removed<br>(n=847)",           # 3
        "After Duplicates<br>(n=2,156)",           # 4
        "Title/Abstract Screening",                 # 5
        "Excluded at Screening<br>(n=1,842)",      # 6
        "Full-text Assessment<br>(n=314)",         # 7
        "Excluded Full-text<br>(n=247)",           # 8
        "Final Included<br>(n=67)"                 # 9
    ]
    
    # Source -> Target connections - Total Records splits to Duplicates AND After Duplicates
    source = [0, 1, 2, 2, 4, 5, 5, 7, 7]
    target = [2, 2, 3, 4, 5, 6, 7, 8, 9]
    value =  [2847, 156, 847, 2156, 2156, 1842, 314, 247, 67]
    
    # Colors for links
    link_colors = [
        'rgba(52, 152, 219, 0.4)',   # Database -> Total (blue)
        'rgba(52, 152, 219, 0.4)',   # Other -> Total (blue)
        'rgba(231, 76, 60, 0.4)',    # Total -> Duplicates Removed (red)
        'rgba(39, 174, 96, 0.4)',    # Total -> After Duplicates (green)
        'rgba(39, 174, 96, 0.4)',    # After Duplicates -> Screening (green)
        'rgba(231, 76, 60, 0.4)',    # Screening -> Excluded (red)
        'rgba(39, 174, 96, 0.4)',    # Screening -> Full-text (green)
        'rgba(231, 76, 60, 0.4)',    # Full-text -> Excluded (red)
        'rgba(39, 174, 96, 0.6)',    # Full-text -> Final (green)
    ]
    
    node_colors = [
        '#3498DB', '#3498DB',        # Sources (blue)
        '#2980B9',                    # Total Records (dark blue)
        '#E74C3C',                    # Duplicates removed (red)
        '#27AE60',                    # After duplicates (green)
        '#27AE60',                    # Screening (green)
        '#E74C3C',                    # Excluded (red)
        '#F39C12',                    # Full-text (orange)
        '#E74C3C',                    # Excluded (red)
        '#2C3E50',                    # Final (dark)
    ]
    
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=40,
            thickness=25,
            line=dict(color='white', width=2),
            label=labels,
            color=node_colors,
            x=[0.01, 0.01, 0.2, 0.35, 0.35, 0.5, 0.65, 0.65, 0.85, 0.85],
            y=[0.3, 0.7, 0.5, 0.85, 0.35, 0.35, 0.85, 0.35, 0.95, 0.2],
            hovertemplate='%{label}<extra></extra>'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            hovertemplate='%{value} records<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text='<b>PRISMA-ScR Flow Diagram</b><br><sup>Systematic Study Selection Process</sup>',
            x=0.5,
            font=dict(size=18, family='Arial', color='#2C3E50')
        ),
        font=dict(size=12, family='Arial'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=700,
        width=1000,
        margin=dict(t=80, l=30, r=30, b=30)
    )
    
    fig.write_image(str(output_dir / 'fig1_prisma_sankey.png'), scale=3)
    fig.write_html(str(output_dir / 'fig1_prisma_sankey.html'))
    print("    ✓ fig1_prisma_sankey.png + .html")


def create_prisma_graphviz():
    """
    Create PRISMA flow diagram using Graphviz for cleaner flowchart.
    """
    print("  Creating PRISMA Graphviz flowchart...")
    
    dot = Digraph(comment='PRISMA Flow', format='png')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='0.6')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='11')
    
    # Identification phase
    with dot.subgraph(name='cluster_0') as c:
        c.attr(label='IDENTIFICATION', fontsize='12', fontname='Arial Bold', 
               style='filled', color='#E3F2FD', fontcolor='#1565C0')
        c.node('A', 'Database Records\n(n = 2,847)', fillcolor='#BBDEFB')
        c.node('B', 'Other Sources\n(n = 156)', fillcolor='#BBDEFB')
    
    # Merge node
    dot.node('C', 'Total Records\n(n = 3,003)', fillcolor='#90CAF9')
    
    # Screening phase
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='SCREENING', fontsize='12', fontname='Arial Bold',
               style='filled', color='#FFF3E0', fontcolor='#E65100')
        c.node('D', 'After Duplicates Removed\n(n = 2,156)', fillcolor='#FFE0B2')
        c.node('E', 'Records Screened\n(n = 2,156)', fillcolor='#FFCC80')
    
    dot.node('F', 'Records Excluded\n(n = 1,842)', fillcolor='#FFCDD2', shape='box')
    
    # Eligibility phase
    with dot.subgraph(name='cluster_2') as c:
        c.attr(label='ELIGIBILITY', fontsize='12', fontname='Arial Bold',
               style='filled', color='#E8F5E9', fontcolor='#2E7D32')
        c.node('G', 'Full-text Assessed\n(n = 314)', fillcolor='#C8E6C9')
    
    dot.node('H', 'Full-text Excluded\n(n = 247)\n\n• Not empirical (78)\n• Wrong population (62)\n• Wrong concept (54)\n• Not English (31)\n• Duplicates (22)', 
             fillcolor='#FFCDD2', fontsize='10')
    
    # Included phase
    with dot.subgraph(name='cluster_3') as c:
        c.attr(label='INCLUDED', fontsize='12', fontname='Arial Bold',
               style='filled', color='#EDE7F6', fontcolor='#512DA8')
        c.node('I', 'Studies Included\n(n = 67)\n\nQuantitative: 38\nQualitative: 18\nMixed: 11', 
               fillcolor='#D1C4E9', fontsize='10')
    
    # Edges
    dot.edge('A', 'C')
    dot.edge('B', 'C')
    dot.edge('C', 'D')
    dot.edge('D', 'E')
    dot.edge('E', 'F')
    dot.edge('E', 'G')
    dot.edge('G', 'H')
    dot.edge('G', 'I')
    
    dot.render(str(output_dir / 'fig1_prisma_flow'), cleanup=True)
    print("    ✓ fig1_prisma_flow.png")


def create_conceptual_model_network():
    """
    Create conceptual model as interactive network diagram.
    """
    print("  Creating Conceptual Model network...")
    
    # Create figure with custom layout
    fig = go.Figure()
    
    # Define node positions (x, y)
    nodes = {
        'AI Implementation': (0, 0.5),
        'HR Strategies': (0.5, 0.5),
        'Outcomes': (1, 0.5),
        'Organizational\nCulture': (0.5, 0),
    }
    
    # Node details
    node_info = {
        'AI Implementation': ['Algorithmic management', 'Task automation', 'AI-powered tools', 'Digital surveillance'],
        'HR Strategies': ['Training & upskilling', 'Change management', 'Communication', 'Job redesign', 'Support systems'],
        'Outcomes': ['Technostress (−)', 'Job satisfaction (+)', 'Wellbeing (+/−)', 'Productivity (+)', 'OSH risks (−)'],
        'Organizational\nCulture': ['Digital climate', 'Leadership support', 'Trust & transparency', 'Psychological safety'],
    }
    
    colors = ['#3498DB', '#27AE60', '#9B59B6', '#F39C12']
    
    # Add nodes as scatter points with boxes around them
    for i, (name, pos) in enumerate(nodes.items()):
        # Add background rectangle
        fig.add_shape(
            type='rect',
            x0=pos[0]-0.15, x1=pos[0]+0.15,
            y0=pos[1]-0.18, y1=pos[1]+0.18,
            fillcolor=colors[i],
            opacity=0.2,
            line=dict(color=colors[i], width=3),
            layer='below'
        )
        
        # Add node label
        fig.add_annotation(
            x=pos[0], y=pos[1]+0.12,
            text=f"<b>{name}</b>",
            showarrow=False,
            font=dict(size=14, color=colors[i]),
        )
        
        # Add details
        details = '<br>'.join([f"• {item}" for item in node_info[name]])
        fig.add_annotation(
            x=pos[0], y=pos[1]-0.03,
            text=details,
            showarrow=False,
            font=dict(size=10, color='#2C3E50'),
            align='center'
        )
    
    # Add main horizontal arrows (AI -> HR -> Outcomes) with solid lines
    # Arrow: AI -> HR (solid)
    fig.add_annotation(
        x=0.35, y=0.5,
        ax=0.15, ay=0.5,
        xref='x', yref='y',
        axref='x', ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor='#3498DB',
    )
    
    # Arrow: HR -> Outcomes (solid)
    fig.add_annotation(
        x=0.85, y=0.5,
        ax=0.65, ay=0.5,
        xref='x', yref='y',
        axref='x', ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor='#27AE60',
    )
    
    # Arrow: Culture -> HR (solid, vertical up)
    fig.add_annotation(
        x=0.5, y=0.32,
        ax=0.5, ay=0.18,
        xref='x', yref='y',
        axref='x', ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor='#F39C12',
    )
    
    # Arrow: Culture -> Outcomes (solid, 90° angles: up then right)
    # Draw as orthogonal path: up from Culture, then right to Outcomes
    # First segment: vertical line from (0.65, 0.18) to (0.65, 0.35)
    fig.add_shape(
        type='line',
        x0=0.65, y0=0.18,
        x1=0.65, y1=0.35,
        line=dict(color='#F39C12', width=3),
    )
    # Second segment: horizontal line from (0.65, 0.35) to (0.85, 0.35)
    fig.add_shape(
        type='line',
        x0=0.65, y0=0.35,
        x1=0.82, y1=0.35,
        line=dict(color='#F39C12', width=3),
    )
    # Arrowhead at end
    fig.add_annotation(
        x=0.85, y=0.35,
        ax=0.80, ay=0.35,
        xref='x', yref='y',
        axref='x', ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor='#F39C12',
    )
    
    # Direct effect arrow (AI -> Outcomes) - 90° solid path going ABOVE
    # Symmetric path: center of AI upper edge -> up -> horizontal -> down -> center of Outcomes upper edge
    # AI box: center at (0, 0.5), upper edge at y=0.68
    # Outcomes box: center at (1, 0.5), upper edge at y=0.68
    # Halfway between boxes (0.68) and title area (~0.95) is about 0.82
    
    # First segment: vertical up from center of AI upper edge (0, 0.68) to (0, 0.80)
    fig.add_shape(
        type='line',
        x0=0, y0=0.68,
        x1=0, y1=0.80,
        line=dict(color='#95A5A6', width=2),
    )
    # Second segment: horizontal from (0, 0.80) to (1, 0.80)
    fig.add_shape(
        type='line',
        x0=0, y0=0.80,
        x1=1, y1=0.80,
        line=dict(color='#95A5A6', width=2),
    )
    # Third segment: vertical down from (1, 0.80) to (1, 0.71) with arrow
    fig.add_shape(
        type='line',
        x0=1, y0=0.80,
        x1=1, y1=0.71,
        line=dict(color='#95A5A6', width=2),
    )
    # Arrowhead at the end pointing to center of Outcomes upper edge
    fig.add_annotation(
        x=1, y=0.68,
        ax=1, ay=0.73,
        xref='x', yref='y',
        axref='x', ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor='#95A5A6',
    )
    
    # Label for direct effect
    fig.add_annotation(
        x=0.5, y=0.83,
        text='<i>Direct effect (unmitigated)</i>',
        showarrow=False,
        font=dict(size=9, color='#95A5A6'),
    )
    
    # Add legend for theoretical frameworks
    fig.add_annotation(
        x=0.5, y=-0.25,
        text="<i>Theoretical Frameworks: JD-R Model • COR Theory • Self-Determination Theory • Socio-Technical Systems</i>",
        showarrow=False,
        font=dict(size=11, color='#7F8C8D'),
    )
    
    fig.update_layout(
        title=dict(
            text='<b>Conceptual Model: HR as Mediator in AI-Driven Workplace Transformation</b>',
            x=0.5, y=0.95,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        xaxis=dict(range=[-0.3, 1.3], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-0.4, 0.8], showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=600,
        width=1100,
        margin=dict(t=80, l=30, r=30, b=50)
    )
    
    fig.write_image(str(output_dir / 'fig2_conceptual_model.png'), scale=3)
    fig.write_html(str(output_dir / 'fig2_conceptual_model.html'))
    print("    ✓ fig2_conceptual_model.png + .html")


def create_technostress_lollipop():
    """
    Create technostress dimensions as lollipop chart.
    Clean, modern, publication-ready.
    """
    print("  Creating Technostress lollipop chart...")
    
    df = pd.DataFrame({
        'Dimension': ['Techno-Insecurity', 'Techno-Overload', 'Techno-Complexity', 
                      'Techno-Uncertainty', 'Techno-Invasion'],
        'Prevalence': [72, 68, 54, 45, 38],
        'Description': [
            'Job security fears from AI/automation',
            'Information & task overload',
            'Difficulty mastering new technologies',
            'Constant technological changes',
            'Work-life boundary erosion'
        ]
    })
    df = df.sort_values('Prevalence', ascending=True)
    
    fig = go.Figure()
    
    # Add horizontal lines (the "sticks")
    for i, row in df.iterrows():
        fig.add_shape(
            type='line',
            x0=0, x1=row['Prevalence'],
            y0=row['Dimension'], y1=row['Dimension'],
            line=dict(color='#BDC3C7', width=2)
        )
    
    # Add the dots
    fig.add_trace(go.Scatter(
        x=df['Prevalence'],
        y=df['Dimension'],
        mode='markers+text',
        marker=dict(
            size=40,
            color=df['Prevalence'],
            colorscale='RdYlGn_r',
            line=dict(color='white', width=2)
        ),
        text=df['Prevalence'].apply(lambda x: f'{x}%'),
        textposition='middle center',
        textfont=dict(color='white', size=11, family='Arial Bold'),
        hovertemplate='<b>%{y}</b><br>Prevalence: %{x}%<extra></extra>'
    ))
    
    # Add descriptions
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row['Prevalence'] + 3,
            y=row['Dimension'],
            text=row['Description'],
            showarrow=False,
            xanchor='left',
            font=dict(size=10, color='#7F8C8D')
        )
    
    fig.update_layout(
        title=dict(
            text='<b>Technostress Dimensions in AI-Adopting Organizations</b><br><sup>Percentage of studies reporting each dimension</sup>',
            x=0.5,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        xaxis=dict(
            title='Prevalence in Reviewed Studies (%)',
            range=[0, 100],
            showgrid=True,
            gridcolor='#ECF0F1',
            zeroline=True,
            zerolinecolor='#BDC3C7'
        ),
        yaxis=dict(showgrid=False, categoryorder='array', categoryarray=df['Dimension'].tolist()),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=450,
        width=900,
        margin=dict(t=80, l=150, r=200, b=60),
        showlegend=False
    )
    
    fig.write_image(str(output_dir / 'fig3_technostress_lollipop.png'), scale=3)
    fig.write_html(str(output_dir / 'fig3_technostress_lollipop.html'))
    print("    ✓ fig3_technostress_lollipop.png + .html")


def create_technostress_radar():
    """
    Create technostress dimensions as radar/spider chart.
    """
    print("  Creating Technostress radar chart...")
    
    categories = ['Techno-\nInsecurity', 'Techno-\nOverload', 'Techno-\nComplexity', 
                  'Techno-\nUncertainty', 'Techno-\nInvasion']
    
    fig = go.Figure()
    
    # Prevalence data
    prevalence = [72, 68, 54, 45, 38]
    
    fig.add_trace(go.Scatterpolar(
        r=prevalence + [prevalence[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(231, 76, 60, 0.3)',
        line=dict(color='#E74C3C', width=3),
        name='Prevalence (%)',
        hovertemplate='%{theta}: %{r}%<extra></extra>'
    ))
    
    # Add reference circles
    for val in [25, 50, 75, 100]:
        fig.add_trace(go.Scatterpolar(
            r=[val]*6,
            theta=categories + [categories[0]],
            mode='lines',
            line=dict(color='#ECF0F1', width=1, dash='dot'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                gridcolor='#ECF0F1',
                linecolor='#BDC3C7'
            ),
            angularaxis=dict(
                gridcolor='#ECF0F1',
                linecolor='#BDC3C7'
            ),
            bgcolor='white'
        ),
        title=dict(
            text='<b>Technostress Dimensions Profile</b><br><sup>Prevalence in AI-adopting organizations (%)</sup>',
            x=0.5,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        paper_bgcolor='white',
        height=550,
        width=600,
        margin=dict(t=100, l=80, r=80, b=50),
        showlegend=False
    )
    
    fig.write_image(str(output_dir / 'fig3_technostress_radar.png'), scale=3)
    fig.write_html(str(output_dir / 'fig3_technostress_radar.html'))
    print("    ✓ fig3_technostress_radar.png + .html")


def create_hr_interventions_dumbbell():
    """
    Create HR interventions as dumbbell/Cleveland dot plot.
    Shows effectiveness vs evidence quality.
    """
    print("  Creating HR interventions dumbbell chart...")
    
    df = pd.DataFrame({
        'Intervention': ['Employee Participation', 'Leadership Development', 'AI Training Programs',
                         'Change Communication', 'Job Redesign', 'Stress Management'],
        'Effectiveness': [82, 78, 72, 65, 61, 55],
        'Evidence': [60, 65, 80, 70, 50, 45]
    })
    df = df.sort_values('Effectiveness', ascending=True)
    
    fig = go.Figure()
    
    # Add connecting lines
    for i, row in df.iterrows():
        fig.add_shape(
            type='line',
            x0=row['Evidence'], x1=row['Effectiveness'],
            y0=row['Intervention'], y1=row['Intervention'],
            line=dict(color='#BDC3C7', width=4)
        )
    
    # Add evidence dots (blue)
    fig.add_trace(go.Scatter(
        x=df['Evidence'],
        y=df['Intervention'],
        mode='markers',
        marker=dict(size=18, color='#3498DB', line=dict(color='white', width=2)),
        name='Evidence Quality',
        hovertemplate='<b>%{y}</b><br>Evidence Quality: %{x}%<extra></extra>'
    ))
    
    # Add effectiveness dots (green)
    fig.add_trace(go.Scatter(
        x=df['Effectiveness'],
        y=df['Intervention'],
        mode='markers',
        marker=dict(size=18, color='#27AE60', line=dict(color='white', width=2)),
        name='Effectiveness',
        hovertemplate='<b>%{y}</b><br>Effectiveness: %{x}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>HR Interventions for Mitigating Technostress</b><br><sup>Comparing Effectiveness vs Evidence Quality</sup>',
            x=0.5,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        xaxis=dict(
            title='Score (%)',
            range=[30, 95],
            showgrid=True,
            gridcolor='#ECF0F1',
            dtick=10
        ),
        yaxis=dict(showgrid=False),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=450,
        width=850,
        margin=dict(t=100, l=180, r=50, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )
    
    fig.write_image(str(output_dir / 'fig4_hr_interventions.png'), scale=3)
    fig.write_html(str(output_dir / 'fig4_hr_interventions.html'))
    print("    ✓ fig4_hr_interventions.png + .html")


def create_study_characteristics_treemap():
    """
    Create study characteristics as treemap.
    """
    print("  Creating Study characteristics treemap...")
    
    # Hierarchical data
    data = {
        'Category': ['Methodology']*3 + ['Region']*4 + ['Sector']*6,
        'Subcategory': [
            'Quantitative', 'Qualitative', 'Mixed Methods',
            'Europe', 'North America', 'Asia', 'Other Regions',
            'Technology/IT', 'Manufacturing', 'Healthcare', 'Finance', 'Public Sector', 'Other'
        ],
        'Count': [38, 18, 11, 28, 22, 12, 5, 22, 12, 10, 9, 8, 6],
        'Parent': ['Methodology']*3 + ['Region']*4 + ['Sector']*6
    }
    
    df = pd.DataFrame(data)
    
    # Add parent rows
    parents_df = pd.DataFrame({
        'Category': ['', '', ''],
        'Subcategory': ['Methodology', 'Region', 'Sector'],
        'Count': [67, 67, 67],
        'Parent': ['', '', '']
    })
    
    fig = px.treemap(
        df,
        path=['Category', 'Subcategory'],
        values='Count',
        color='Count',
        color_continuous_scale='Blues',
        title='<b>Characteristics of Included Studies (n = 67)</b>'
    )
    
    fig.update_layout(
        font=dict(size=12, family='Arial'),
        paper_bgcolor='white',
        height=500,
        width=900,
        margin=dict(t=60, l=20, r=20, b=20)
    )
    
    fig.update_traces(
        textinfo='label+value',
        textfont=dict(color='white'),
        hovertemplate='<b>%{label}</b><br>Studies: %{value}<extra></extra>'
    )
    
    fig.write_image(str(output_dir / 'fig5_study_treemap.png'), scale=3)
    fig.write_html(str(output_dir / 'fig5_study_treemap.html'))
    print("    ✓ fig5_study_treemap.png + .html")


def create_study_characteristics_sunburst():
    """
    Create study characteristics as sunburst chart.
    """
    print("  Creating Study characteristics sunburst...")
    
    fig = go.Figure(go.Sunburst(
        ids=[
            'root',
            'method', 'quant', 'qual', 'mixed',
            'region', 'europe', 'namerica', 'asia', 'other_reg',
            'sector', 'tech', 'mfg', 'health', 'finance', 'public', 'other_sec'
        ],
        labels=[
            '',  # Empty label for root - we'll add it as annotation
            '<b>Methodology</b>', 'Quantitative<br>(n=38)', 'Qualitative<br>(n=18)', 'Mixed<br>(n=11)',
            '<b>Region</b>', 'Europe<br>(n=28)', 'N. America<br>(n=22)', 'Asia<br>(n=12)', 'Other<br>(n=5)',
            '<b>Sector</b>', 'Tech/IT<br>(n=22)', 'Manufacturing<br>(n=12)', 'Healthcare<br>(n=10)', 'Finance<br>(n=9)', 'Public<br>(n=8)', 'Other<br>(n=6)'
        ],
        parents=[
            '',
            'root', 'method', 'method', 'method',
            'root', 'region', 'region', 'region', 'region',
            'root', 'sector', 'sector', 'sector', 'sector', 'sector', 'sector'
        ],
        values=[
            0,
            0, 38, 18, 11,
            0, 28, 22, 12, 5,
            0, 22, 12, 10, 9, 8, 6
        ],
        branchvalues='remainder',
        marker=dict(
            colors=[
                '#2C3E50',  # Root (dark)
                '#3498DB', '#5DADE2', '#85C1E9', '#AED6F1',  # Methodology (blues)
                '#27AE60', '#52BE80', '#7DCEA0', '#A9DFBF', '#D5F5E3',  # Region (greens)
                '#9B59B6', '#AF7AC5', '#BB8FCE', '#C39BD3', '#D2B4DE', '#E8DAEF', '#F4ECF7'  # Sector (purples)
            ],
            line=dict(color='white', width=2)
        ),
        textfont=dict(size=11, color='#1a252f'),  # Default black text
        hovertemplate='<b>%{label}</b><br>Studies: %{value}<extra></extra>'
    ))
    
    # Add center text as annotation (white on dark background)
    fig.add_annotation(
        x=0.5, y=0.5,
        xref='paper', yref='paper',
        text='<b>Studies</b><br>(n=67)',
        showarrow=False,
        font=dict(size=14, color='white', family='Arial'),
        align='center'
    )
    
    fig.update_layout(
        title=dict(
            text='<b>Study Characteristics Overview</b>',
            x=0.5,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        paper_bgcolor='white',
        height=600,
        width=700,
        margin=dict(t=60, l=20, r=20, b=20)
    )
    
    fig.write_image(str(output_dir / 'fig5_study_sunburst.png'), scale=3)
    fig.write_html(str(output_dir / 'fig5_study_sunburst.html'))
    print("    ✓ fig5_study_sunburst.png + .html")


def create_geographic_choropleth():
    """
    Create geographic distribution as world map.
    """
    print("  Creating Geographic choropleth map...")
    
    # Country-level data (ISO codes)
    df = pd.DataFrame({
        'Country': ['United Kingdom', 'Germany', 'Netherlands', 'Sweden', 'France', 
                    'United States', 'Canada', 'China', 'South Korea', 'Singapore',
                    'Australia', 'India', 'Japan', 'Italy', 'Spain'],
        'ISO': ['GBR', 'DEU', 'NLD', 'SWE', 'FRA', 
                'USA', 'CAN', 'CHN', 'KOR', 'SGP',
                'AUS', 'IND', 'JPN', 'ITA', 'ESP'],
        'Studies': [8, 6, 4, 3, 3, 15, 7, 5, 4, 3, 3, 2, 2, 2, 2]
    })
    
    fig = px.choropleth(
        df,
        locations='ISO',
        color='Studies',
        hover_name='Country',
        color_continuous_scale='Blues',
        range_color=[0, 15],
        title='<b>Geographic Distribution of Included Studies</b>'
    )
    
    fig.update_geos(
        showcountries=True,
        countrycolor='#BDC3C7',
        showcoastlines=True,
        coastlinecolor='#95A5A6',
        showland=True,
        landcolor='#F8F9FA',
        showocean=True,
        oceancolor='#E8F4F8',
        projection_type='natural earth'
    )
    
    fig.update_layout(
        font=dict(size=12, family='Arial'),
        paper_bgcolor='white',
        height=500,
        width=1000,
        margin=dict(t=60, l=20, r=20, b=20),
        coloraxis_colorbar=dict(title='Studies')
    )
    
    fig.write_image(str(output_dir / 'fig6_geographic_map.png'), scale=3)
    fig.write_html(str(output_dir / 'fig6_geographic_map.html'))
    print("    ✓ fig6_geographic_map.png + .html")


def create_publication_timeline():
    """
    Create publication timeline as area chart.
    """
    print("  Creating Publication timeline...")
    
    df = pd.DataFrame({
        'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
        'Quantitative': [1, 1, 2, 3, 4, 5, 6, 7, 5, 3, 1],
        'Qualitative': [0, 1, 1, 1, 2, 2, 3, 4, 3, 1, 0],
        'Mixed': [0, 0, 0, 1, 1, 1, 2, 3, 2, 1, 0]
    })
    
    fig = go.Figure()
    
    colors = ['#3498DB', '#27AE60', '#F39C12']
    methods = ['Quantitative', 'Qualitative', 'Mixed']
    
    for method, color in zip(methods, colors):
        fig.add_trace(go.Scatter(
            x=df['Year'],
            y=df[method],
            name=method,
            mode='lines',
            line=dict(width=0.5, color=color),
            stackgroup='one',
            fillcolor=color.replace(')', ',0.6)').replace('rgb', 'rgba') if 'rgb' in color else color,
            hovertemplate='%{y} studies<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text='<b>Publication Timeline by Methodology</b><br><sup>Number of studies published per year</sup>',
            x=0.5,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        xaxis=dict(title='Year', dtick=1, range=[2014.5, 2025.5]),
        yaxis=dict(title='Number of Studies'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=400,
        width=900,
        margin=dict(t=80, l=60, r=30, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#ECF0F1')
    fig.update_yaxes(showgrid=True, gridcolor='#ECF0F1')
    
    fig.write_image(str(output_dir / 'fig7_timeline.png'), scale=3)
    fig.write_html(str(output_dir / 'fig7_timeline.html'))
    print("    ✓ fig7_timeline.png + .html")


def create_keywords_wordcloud():
    """
    Create keywords word cloud.
    """
    print("  Creating Keywords wordcloud...")
    
    keywords = {
        'technostress': 45, 'artificial intelligence': 42, 'HR': 38, 'AI adoption': 35,
        'digital transformation': 32, 'employee wellbeing': 30, 'organizational culture': 28,
        'automation': 26, 'job insecurity': 24, 'machine learning': 22,
        'psychosocial risks': 20, 'work stress': 19, 'algorithmic management': 18,
        'training': 17, 'change management': 16, 'leadership': 15, 'burnout': 14,
        'Industry 4.0': 13, 'job demands': 12, 'digital workplace': 11,
        'employee engagement': 10, 'remote work': 9, 'skills gap': 8,
        'mental health': 8, 'productivity': 7, 'trust': 7, 'transparency': 6,
        'upskilling': 6, 'reskilling': 5, 'human-AI collaboration': 5
    }
    
    wc = WordCloud(
        width=1200, height=600,
        background_color='white',
        colormap='viridis',
        max_words=50,
        prefer_horizontal=0.7,
        min_font_size=10,
        max_font_size=120,
        random_state=42,
        contour_color='#2C3E50',
        contour_width=1
    ).generate_from_frequencies(keywords)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Key Concepts in Reviewed Literature', fontsize=16, fontweight='bold', 
                 color='#2C3E50', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'fig8_keywords_cloud.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("    ✓ fig8_keywords_cloud.png")


def create_evidence_gap_matrix():
    """
    Create evidence gap matrix/heatmap.
    """
    print("  Creating Evidence gap matrix...")
    
    # Define the matrix data
    populations = ['IT workers', 'Manufacturing', 'Healthcare', 'Public sector', 'Older workers', 'Gig workers']
    outcomes = ['Technostress', 'Wellbeing', 'Productivity', 'OSH risks', 'Turnover']
    
    # Evidence levels: 0=no evidence, 1=limited, 2=moderate, 3=strong
    data = np.array([
        [3, 3, 2, 2, 2],  # IT workers
        [2, 2, 2, 2, 1],  # Manufacturing
        [2, 2, 1, 2, 1],  # Healthcare
        [1, 1, 1, 1, 1],  # Public sector
        [1, 1, 0, 0, 0],  # Older workers
        [2, 1, 1, 2, 1],  # Gig workers
    ])
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=outcomes,
        y=populations,
        colorscale=[
            [0, '#FFEBEE'],      # No evidence - light red
            [0.33, '#FFCDD2'],   # Limited
            [0.67, '#81C784'],   # Moderate - light green
            [1, '#2E7D32']       # Strong - dark green
        ],
        showscale=True,
        colorbar=dict(
            title='Evidence Level',
            tickvals=[0.5, 1.5, 2.5],
            ticktext=['Limited', 'Moderate', 'Strong']
        ),
        hovertemplate='Population: %{y}<br>Outcome: %{x}<br>Evidence: %{z}<extra></extra>'
    ))
    
    # Add text annotations
    for i, pop in enumerate(populations):
        for j, out in enumerate(outcomes):
            level = data[i, j]
            text = ['None', 'Limited', 'Moderate', 'Strong'][level]
            color = 'white' if level >= 2 else '#2C3E50'
            fig.add_annotation(
                x=out, y=pop,
                text=text,
                showarrow=False,
                font=dict(size=10, color=color)
            )
    
    fig.update_layout(
        title=dict(
            text='<b>Evidence Gap Map</b>',
            x=0.5,
            y=0.98,
            font=dict(size=16, family='Arial', color='#2C3E50')
        ),
        xaxis=dict(title='', side='top', tickfont=dict(size=11)),
        yaxis=dict(title='', autorange='reversed', tickfont=dict(size=11)),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=500,
        width=800,
        margin=dict(t=100, l=120, r=80, b=40),
    )
    
    # Add subtitle centered between title and heatmap top
    fig.add_annotation(
        x=0.5, y=1.12, xref='paper', yref='paper',
        text='Research coverage by population and outcome',
        showarrow=False,
        font=dict(size=11, color='#7F8C8D')
    )
    
    fig.write_image(str(output_dir / 'fig9_evidence_gaps.png'), scale=3)
    fig.write_html(str(output_dir / 'fig9_evidence_gaps.html'))
    print("    ✓ fig9_evidence_gaps.png + .html")


def main():
    """Generate all modern visualizations."""
    print("\n" + "="*70)
    print("  GENERATING MODERN VISUALIZATIONS")
    print("  Using: Plotly, Altair, Graphviz, NetworkX, WordCloud")
    print("="*70 + "\n")
    
    # Generate all visualizations
    create_prisma_sankey()
    # create_prisma_graphviz()  # Requires Graphviz system install
    create_conceptual_model_network()
    create_technostress_lollipop()
    create_technostress_radar()
    create_hr_interventions_dumbbell()
    create_study_characteristics_treemap()
    create_study_characteristics_sunburst()
    create_geographic_choropleth()
    create_publication_timeline()
    create_keywords_wordcloud()
    create_evidence_gap_matrix()
    
    print("\n" + "="*70)
    print(f"  ALL VISUALIZATIONS CREATED")
    print(f"  Location: {output_dir}")
    print("  Formats: PNG (high-res) + HTML (interactive)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
