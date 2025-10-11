#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate US stock trading hours windows chart (English only)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Remove Chinese font configuration - use English only
plt.rcParams['axes.unicode_minus'] = False

# Create figure
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#ffffff')

# Hide axes
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.2, 'US Stock Trading Windows: Response After Oct 10 Crash',
        fontsize=18, fontweight='bold', ha='center', color='#2c3e50')

# Subtitle
ax.text(5, 8.7, 'Three Time Windows for Flexible Operations',
        fontsize=12, ha='center', color='#7f8c8d', style='italic')

# Define three time windows
windows = [
    {
        'title': 'Option 1: Friday After-Hours',
        'subtitle': '(Fastest to Lock Low Price)',
        'us_time': 'ET 16:00-20:00',
        'cn_time': 'Beijing Sat\n4:00-8:00 AM',
        'color': '#e74c3c',
        'y_pos': 6.5
    },
    {
        'title': 'Option 2: Monday Pre-Market',
        'subtitle': '(Before Market Opens)',
        'us_time': 'ET 4:00-9:30',
        'cn_time': 'Beijing Mon\nBefore 8:00 PM',
        'color': '#f39c12',
        'y_pos': 4.2
    },
    {
        'title': 'Option 3: Monday Regular Hours',
        'subtitle': '(Best Liquidity)',
        'us_time': 'ET 9:30-16:00',
        'cn_time': 'Beijing Mon\nAfter 9:30 PM',
        'color': '#27ae60',
        'y_pos': 1.9
    }
]

# Draw three time windows
for i, window in enumerate(windows):
    y = window['y_pos']
    color = window['color']

    # Main box
    box = FancyBboxPatch((0.5, y), 9, 1.5, boxstyle="round,pad=0.1",
                          edgecolor=color, facecolor=color, alpha=0.15,
                          linewidth=3)
    ax.add_patch(box)

    # Title
    ax.text(1, y + 1.2, window['title'],
            fontsize=14, fontweight='bold', color=color, va='top')

    ax.text(1, y + 0.85, window['subtitle'],
            fontsize=10, color='#7f8c8d', va='top', style='italic')

    # US time box
    us_box = FancyBboxPatch((3.8, y + 0.15), 2, 1.1, boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor='white', alpha=0.9,
                            linewidth=2)
    ax.add_patch(us_box)

    ax.text(4.8, y + 0.95, window['us_time'],
            fontsize=10, ha='center', va='top', color='#2c3e50',
            fontweight='bold', linespacing=1.5)

    # Arrow
    arrow = FancyArrowPatch((5.9, y + 0.7), (6.5, y + 0.7),
                           arrowstyle='->', mutation_scale=20,
                           color=color, linewidth=2.5)
    ax.add_artist(arrow)

    # Beijing time box
    cn_box = FancyBboxPatch((6.6, y + 0.15), 2.3, 1.1, boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor='white', alpha=0.9,
                            linewidth=2)
    ax.add_patch(cn_box)

    ax.text(7.75, y + 0.95, window['cn_time'],
            fontsize=10, ha='center', va='top', color='#2c3e50',
            fontweight='bold', linespacing=1.5)

# Bottom info box
info_box = FancyBboxPatch((0.5, 0.2), 9, 1.3, boxstyle="round,pad=0.1",
                          edgecolor='#3498db', facecolor='#ebf5fb',
                          linewidth=2, alpha=0.9)
ax.add_patch(info_box)

# Info text
ax.text(5, 1.15, 'KEY PRINCIPLE',
        fontsize=13, fontweight='bold', ha='center', color='#3498db')

ax.text(5, 0.75, 'Manual position size should not exceed single DCA amount | US stocks support fractional shares',
        fontsize=10, ha='center', color='#2c3e50', va='top')

ax.text(5, 0.45, 'Advantage: More decision buffer time vs A-share "instant hell at open"',
        fontsize=9, ha='center', color='#7f8c8d', va='top', style='italic')

# Top date annotation
date_box = FancyBboxPatch((7.5, 7.8), 2, 0.6, boxstyle="round,pad=0.05",
                          edgecolor='#e74c3c', facecolor='#e74c3c',
                          linewidth=2, alpha=0.9)
ax.add_patch(date_box)

ax.text(8.5, 8.25, 'Oct 10, 2025',
        fontsize=11, ha='center', va='center', color='white', fontweight='bold')

ax.text(8.5, 7.95, 'S&P 500 -2.71%',
        fontsize=9, ha='center', va='center', color='white')

plt.tight_layout()

# Save image
output_path = 'assets/images/posts/2025/10/trading-hours-windows.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
print(f"✅ Trading hours windows chart generated: {output_path}")

plt.close()
