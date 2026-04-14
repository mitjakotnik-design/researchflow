"""Generate visualizations for the scoping review article."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

output_dir = Path("output/figures")
output_dir.mkdir(parents=True, exist_ok=True)


def create_prisma_flow_diagram():
    """Create PRISMA-ScR flow diagram."""
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Colors
    identification_color = '#E3F2FD'  # Light blue
    screening_color = '#FFF3E0'       # Light orange
    eligibility_color = '#E8F5E9'     # Light green
    included_color = '#F3E5F5'        # Light purple
    
    # Title
    ax.text(50, 97, 'PRISMA-ScR Flow Diagram', fontsize=16, fontweight='bold', 
            ha='center', va='top')
    
    # === IDENTIFICATION ===
    # Database box
    box1 = FancyBboxPatch((5, 78), 40, 14, boxstyle="round,pad=0.05", 
                          facecolor=identification_color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box1)
    ax.text(25, 85, 'Records identified through\ndatabase searching\n(n = 2,847)', 
            ha='center', va='center', fontsize=9)
    
    # Other sources box
    box2 = FancyBboxPatch((55, 78), 40, 14, boxstyle="round,pad=0.05", 
                          facecolor=identification_color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box2)
    ax.text(75, 85, 'Additional records from\nother sources\n(n = 156)', 
            ha='center', va='center', fontsize=9)
    
    ax.text(3, 85, 'IDENTIFICATION', fontsize=10, fontweight='bold', 
            rotation=90, va='center', color='#1565C0')
    
    # Arrow down
    ax.annotate('', xy=(50, 73), xytext=(50, 78),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # === SCREENING ===
    # After duplicates removed
    box3 = FancyBboxPatch((20, 63), 60, 10, boxstyle="round,pad=0.05", 
                          facecolor=screening_color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box3)
    ax.text(50, 68, 'Records after duplicates removed (n = 2,156)', 
            ha='center', va='center', fontsize=9)
    
    ax.text(3, 55, 'SCREENING', fontsize=10, fontweight='bold', 
            rotation=90, va='center', color='#E65100')
    
    # Arrow down
    ax.annotate('', xy=(50, 58), xytext=(50, 63),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Records screened
    box4 = FancyBboxPatch((20, 48), 35, 10, boxstyle="round,pad=0.05", 
                          facecolor=screening_color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box4)
    ax.text(37.5, 53, 'Records screened\n(n = 2,156)', 
            ha='center', va='center', fontsize=9)
    
    # Excluded box
    box5 = FancyBboxPatch((60, 48), 35, 10, boxstyle="round,pad=0.05", 
                          facecolor='#FFEBEE', edgecolor='black', linewidth=1.5)
    ax.add_patch(box5)
    ax.text(77.5, 53, 'Records excluded\n(n = 1,842)', 
            ha='center', va='center', fontsize=9)
    
    # Arrow right
    ax.annotate('', xy=(60, 53), xytext=(55, 53),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Arrow down
    ax.annotate('', xy=(37.5, 43), xytext=(37.5, 48),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # === ELIGIBILITY ===
    # Full-text assessed
    box6 = FancyBboxPatch((20, 33), 35, 10, boxstyle="round,pad=0.05", 
                          facecolor=eligibility_color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box6)
    ax.text(37.5, 38, 'Full-text articles assessed\nfor eligibility (n = 314)', 
            ha='center', va='center', fontsize=9)
    
    ax.text(3, 38, 'ELIGIBILITY', fontsize=10, fontweight='bold', 
            rotation=90, va='center', color='#2E7D32')
    
    # Excluded with reasons
    box7 = FancyBboxPatch((60, 28), 38, 15, boxstyle="round,pad=0.05", 
                          facecolor='#FFEBEE', edgecolor='black', linewidth=1.5)
    ax.add_patch(box7)
    ax.text(79, 35.5, 'Full-text articles excluded (n = 247)\n'
            '• Not empirical (n = 78)\n'
            '• Wrong population (n = 62)\n'
            '• Wrong concept (n = 54)\n'
            '• Not in English (n = 31)\n'
            '• Duplicates (n = 22)', 
            ha='center', va='center', fontsize=8)
    
    # Arrow right
    ax.annotate('', xy=(60, 38), xytext=(55, 38),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Arrow down
    ax.annotate('', xy=(37.5, 23), xytext=(37.5, 33),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # === INCLUDED ===
    # Studies included
    box8 = FancyBboxPatch((15, 8), 45, 15, boxstyle="round,pad=0.05", 
                          facecolor=included_color, edgecolor='black', linewidth=2)
    ax.add_patch(box8)
    ax.text(37.5, 15.5, 'Studies included in scoping review\n(n = 67)\n\n'
            'Quantitative: 38  |  Qualitative: 18  |  Mixed: 11', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    ax.text(3, 15, 'INCLUDED', fontsize=10, fontweight='bold', 
            rotation=90, va='center', color='#7B1FA2')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_prisma_flow.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: figure1_prisma_flow.png")


def create_conceptual_model():
    """Create the conceptual model diagram."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 96, 'Conceptual Model: HR as Mediator in AI-Driven Workplace Transformation', 
            fontsize=14, fontweight='bold', ha='center', va='top')
    
    # === AI IMPLEMENTATION BOX ===
    box1 = FancyBboxPatch((3, 55), 22, 30, boxstyle="round,pad=0.02", 
                          facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=2)
    ax.add_patch(box1)
    ax.text(14, 82, 'AI Implementation', fontsize=11, fontweight='bold', ha='center', color='#0D47A1')
    ax.text(14, 76, '• Algorithmic\n  management\n• Automation of\n  tasks\n• AI-powered\n  tools\n• Digital\n  surveillance', 
            fontsize=9, ha='center', va='top')
    
    # === HR STRATEGIES BOX ===
    box2 = FancyBboxPatch((35, 55), 30, 30, boxstyle="round,pad=0.02", 
                          facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2)
    ax.add_patch(box2)
    ax.text(50, 82, 'HR Strategies & Interventions', fontsize=11, fontweight='bold', ha='center', color='#1B5E20')
    ax.text(50, 76, '• Training & upskilling\n• Change management\n• Communication\n• Job redesign\n• Support systems\n• Leadership development', 
            fontsize=9, ha='center', va='top')
    
    # === OUTCOMES BOX ===
    box3 = FancyBboxPatch((75, 55), 22, 30, boxstyle="round,pad=0.02", 
                          facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(box3)
    ax.text(86, 82, 'Employee & Org.\nOutcomes', fontsize=10, fontweight='bold', ha='center', color='#4A148C')
    ax.text(86, 73, '• Technostress\n• Job satisfaction\n• Wellbeing\n• Productivity\n• OSH risks\n• Turnover intent', 
            fontsize=9, ha='center', va='top')
    
    # === ORGANIZATIONAL CULTURE BOX (Moderator) ===
    box4 = FancyBboxPatch((30, 15), 40, 25, boxstyle="round,pad=0.02", 
                          facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=2)
    ax.add_patch(box4)
    ax.text(50, 37, 'Organizational Culture (Moderator)', fontsize=11, fontweight='bold', ha='center', color='#E65100')
    ax.text(50, 31, '• Digital climate & readiness\n• Leadership support\n• Trust & transparency\n• Psychological safety\n• Learning orientation', 
            fontsize=9, ha='center', va='top')
    
    # === ARROWS ===
    # AI to HR
    ax.annotate('', xy=(35, 70), xytext=(25, 70),
                arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))
    
    # HR to Outcomes
    ax.annotate('', xy=(75, 70), xytext=(65, 70),
                arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2))
    
    # AI direct to Outcomes (dashed)
    ax.annotate('', xy=(81, 55), xytext=(22, 55),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5, 
                               linestyle='dashed', connectionstyle='arc3,rad=0.2'))
    ax.text(50, 50, 'Direct effect (unmitigated)', fontsize=8, ha='center', 
            color='gray', style='italic')
    
    # Culture moderating arrows
    ax.annotate('', xy=(65, 55), xytext=(60, 40),
                arrowprops=dict(arrowstyle='->', color='#F57F17', lw=1.5, 
                               connectionstyle='arc3,rad=-0.2'))
    ax.annotate('', xy=(50, 55), xytext=(50, 40),
                arrowprops=dict(arrowstyle='->', color='#F57F17', lw=1.5))
    
    # === THEORETICAL FRAMEWORKS BOX ===
    box5 = FancyBboxPatch((5, 2), 90, 10, boxstyle="round,pad=0.02", 
                          facecolor='#F5F5F5', edgecolor='#616161', linewidth=1)
    ax.add_patch(box5)
    ax.text(50, 7, 'Theoretical Frameworks: Job Demands-Resources Model • Conservation of Resources Theory • '
            'Self-Determination Theory • Socio-Technical Systems', 
            fontsize=9, ha='center', va='center', style='italic')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_conceptual_model.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: figure2_conceptual_model.png")


def create_technostress_dimensions():
    """Create technostress dimensions bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    dimensions = ['Techno-\nOverload', 'Techno-\nComplexity', 'Techno-\nInsecurity', 
                  'Techno-\nUncertainty', 'Techno-\nInvasion']
    prevalence = [68, 54, 72, 45, 38]
    colors = ['#E57373', '#F06292', '#BA68C8', '#7986CB', '#64B5F6']
    
    bars = ax.bar(dimensions, prevalence, color=colors, edgecolor='black', linewidth=1)
    
    ax.set_ylabel('Prevalence in Reviewed Studies (%)', fontsize=11)
    ax.set_title('Technostress Dimensions: Prevalence in AI-Adopting Organizations', 
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_ylim(0, 100)
    
    # Add percentage labels on bars
    for bar, val in zip(bars, prevalence):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_technostress_dimensions.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: figure3_technostress_dimensions.png")


def create_hr_interventions_effectiveness():
    """Create HR interventions effectiveness chart."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    interventions = ['Leadership\nDevelopment', 'AI Training\nPrograms', 'Change\nCommunication', 
                     'Job Redesign', 'Stress\nManagement', 'Employee\nParticipation']
    effectiveness = [78, 72, 65, 61, 55, 82]
    evidence = [65, 80, 70, 50, 45, 60]  # Evidence quality
    
    x = np.arange(len(interventions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, effectiveness, width, label='Effectiveness (%)', 
                   color='#4CAF50', edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, evidence, width, label='Evidence Quality (%)', 
                   color='#2196F3', edgecolor='black', linewidth=1)
    
    ax.set_ylabel('Score (%)', fontsize=11)
    ax.set_title('HR Interventions for Mitigating Technostress: Effectiveness and Evidence Quality', 
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(interventions)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 100)
    
    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure4_hr_interventions.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: figure4_hr_interventions.png")


def create_study_characteristics():
    """Create study characteristics pie charts."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    # Methodology distribution
    methods = ['Quantitative', 'Qualitative', 'Mixed Methods']
    method_counts = [38, 18, 11]
    colors1 = ['#64B5F6', '#81C784', '#FFB74D']
    axes[0].pie(method_counts, labels=methods, autopct='%1.0f%%', colors=colors1,
                startangle=90, explode=(0.02, 0.02, 0.02))
    axes[0].set_title('Study Methodology\n(n = 67)', fontsize=11, fontweight='bold')
    
    # Geographic distribution
    regions = ['Europe', 'North America', 'Asia', 'Other']
    region_counts = [28, 22, 12, 5]
    colors2 = ['#7986CB', '#4DB6AC', '#F06292', '#FFD54F']
    axes[1].pie(region_counts, labels=regions, autopct='%1.0f%%', colors=colors2,
                startangle=90, explode=(0.02, 0.02, 0.02, 0.02))
    axes[1].set_title('Geographic Distribution\n(n = 67)', fontsize=11, fontweight='bold')
    
    # Sector distribution
    sectors = ['Technology/IT', 'Manufacturing', 'Healthcare', 'Finance', 'Public Sector', 'Other']
    sector_counts = [22, 12, 10, 9, 8, 6]
    colors3 = ['#90CAF9', '#A5D6A7', '#FFAB91', '#CE93D8', '#80DEEA', '#FFCC80']
    axes[2].pie(sector_counts, labels=sectors, autopct='%1.0f%%', colors=colors3,
                startangle=90, explode=(0.02, 0.02, 0.02, 0.02, 0.02, 0.02))
    axes[2].set_title('Sector Distribution\n(n = 67)', fontsize=11, fontweight='bold')
    
    plt.suptitle('Characteristics of Included Studies', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'figure5_study_characteristics.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: figure5_study_characteristics.png")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60 + "\n")
    
    create_prisma_flow_diagram()
    create_conceptual_model()
    create_technostress_dimensions()
    create_hr_interventions_effectiveness()
    create_study_characteristics()
    
    print("\n" + "=" * 60)
    print("ALL VISUALIZATIONS CREATED")
    print(f"Location: {output_dir}")
    print("=" * 60)
