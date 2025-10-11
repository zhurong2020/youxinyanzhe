#!/usr/bin/env python3
"""
Generate trading strategies advantage comparison chart
Showing how extended trading hours benefit various financial instruments and strategies
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Remove Chinese font configuration - use English only
plt.rcParams['axes.unicode_minus'] = False

# Set dark background style
plt.style.use('dark_background')

# Create figure
fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
fig.text(0.5, 0.95, 'Extended Trading Hours: Strategic Advantages',
         ha='center', va='top', fontsize=22, fontweight='bold')

# Subtitle
fig.text(0.5, 0.91, 'How 16-hour trading windows unlock powerful investment tools',
         ha='center', va='top', fontsize=14, alpha=0.8)

# Left side: A-shares limitations (4 hours)
left_box_y = 7.5
left_box = FancyBboxPatch((0.3, left_box_y), 3.5, 1.2,
                          boxstyle="round,pad=0.1",
                          edgecolor='#e74c3c', facecolor='#2d1818',
                          linewidth=2, alpha=0.8)
ax.add_patch(left_box)

ax.text(2.05, left_box_y + 0.85, 'A-Shares: 4 Hours/Day',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#e74c3c')
ax.text(2.05, left_box_y + 0.45, 'Limited Tools & Flexibility',
        ha='center', va='center', fontsize=11, alpha=0.7)

# Right side: US stocks advantages (16 hours)
right_box_y = 7.5
right_box = FancyBboxPatch((6.2, right_box_y), 3.5, 1.2,
                           boxstyle="round,pad=0.1",
                           edgecolor='#2ecc71', facecolor='#1a2d1a',
                           linewidth=2, alpha=0.8)
ax.add_patch(right_box)

ax.text(7.95, right_box_y + 0.85, 'US Stocks: 16 Hours/Day',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#2ecc71')
ax.text(7.95, right_box_y + 0.45, 'Rich Tools & High Flexibility',
        ha='center', va='center', fontsize=11, alpha=0.7)

# Arrow connecting two sides
arrow = FancyArrowPatch((3.9, left_box_y + 0.6), (6.1, right_box_y + 0.6),
                       arrowstyle='->', mutation_scale=30, linewidth=3,
                       color='#f39c12', alpha=0.8)
ax.add_artist(arrow)
ax.text(5.0, left_box_y + 1.0, '+300%', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#f39c12')

# Strategy comparison sections
strategies = [
    {
        'title': '1. Options Trading',
        'a_share': ['Very limited', 'Only 50ETF options', 'Low liquidity'],
        'us_stock': ['Rich variety', 'Options on all stocks', 'High liquidity', 'Same-day response'],
        'y_pos': 6.0,
        'icon': '📊'
    },
    {
        'title': '2. T+0 Day Trading',
        'a_share': ['T+1 settlement', 'Cannot sell same day', 'High risk control difficulty'],
        'us_stock': ['T+0 settlement', 'Unlimited day trading', 'Intraday grid strategies', '16-hour window flexibility'],
        'y_pos': 4.3,
        'icon': '⚡'
    },
    {
        'title': '3. News Response',
        'a_share': ['Limited reaction time', 'Gap risk next day', 'Forced holding overnight'],
        'us_stock': ['16-hour reaction window', 'Pre-market adjustment', 'After-hours trading', 'Reduce gap risk'],
        'y_pos': 2.6,
        'icon': '📰'
    },
    {
        'title': '4. Risk Management',
        'a_share': ['Cannot exit same day', 'Stop-loss difficulty', '10% daily limit'],
        'us_stock': ['Immediate exit capability', 'Flexible stop-loss', 'No daily limits', 'Multiple time windows'],
        'y_pos': 0.9,
        'icon': '🛡️'
    }
]

for strategy in strategies:
    y = strategy['y_pos']

    # Strategy title with icon
    ax.text(0.5, y + 0.5, f"{strategy['icon']} {strategy['title']}",
            ha='left', va='center', fontsize=13, fontweight='bold',
            color='#4ecdc4')

    # A-share limitations (left column)
    a_box = FancyBboxPatch((0.3, y - 0.5), 3.5, 0.9,
                           boxstyle="round,pad=0.08",
                           edgecolor='#e74c3c', facecolor='#1a1a2e',
                           linewidth=1.5, alpha=0.6)
    ax.add_patch(a_box)

    for i, item in enumerate(strategy['a_share']):
        ax.text(0.5, y - 0.5 + 0.7 - i*0.22, f'• {item}',
                ha='left', va='top', fontsize=9.5, color='#e74c3c', alpha=0.9)

    # US stock advantages (right column)
    us_box = FancyBboxPatch((6.2, y - 0.5), 3.5, 0.9,
                            boxstyle="round,pad=0.08",
                            edgecolor='#2ecc71', facecolor='#1a1a2e',
                            linewidth=1.5, alpha=0.6)
    ax.add_patch(us_box)

    for i, item in enumerate(strategy['us_stock']):
        ax.text(6.4, y - 0.5 + 0.7 - i*0.20, f'✓ {item}',
                ha='left', va='top', fontsize=9.5, color='#2ecc71', alpha=0.9)

# Bottom insight box
insight_box = FancyBboxPatch((0.5, -0.7), 9.0, 0.6,
                            boxstyle="round,pad=0.1",
                            edgecolor='#f39c12', facecolor='#1a1a2e',
                            linewidth=2, alpha=0.9)
ax.add_patch(insight_box)

insight_text = ('💡 Key Takeaway: Extended trading hours (16h vs 4h) provide US stock investors with:\n'
               '   • More flexible risk management  • Richer trading instruments  • Better news response capability  • Higher strategic diversity')

ax.text(5.0, -0.4, insight_text,
        ha='center', va='center', fontsize=10.5, color='#f39c12',
        linespacing=1.6, fontweight='bold')

plt.tight_layout()

# Save the chart
output_path = 'assets/images/posts/2025/10/trading-strategies-advantage.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#1a1a2e')
print(f"Chart saved to: {output_path}")

# Show file size
import os
file_size = os.path.getsize(output_path)
print(f"File size: {file_size/1024:.1f} KB")
