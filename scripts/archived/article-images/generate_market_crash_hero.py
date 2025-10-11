#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate market crash hero image (English only)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

# Remove Chinese font configuration - use English only
plt.rcParams['axes.unicode_minus'] = False

# Create figure
fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

# Hide axes
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Main title
ax.text(5, 8.5, 'MARKET CRASH',
        fontsize=52, fontweight='bold', ha='center', color='#e74c3c',
        family='sans-serif')

ax.text(5, 7.8, 'Long-Term Investor\'s Guide',
        fontsize=28, ha='center', color='white', fontweight='bold')

# Event date and data
event_box = FancyBboxPatch((1.5, 6.3), 7, 1, boxstyle="round,pad=0.1",
                          edgecolor='#e74c3c', facecolor='#e74c3c',
                          linewidth=3, alpha=0.2)
ax.add_patch(event_box)

ax.text(5, 6.95, 'October 10, 2025',
        fontsize=20, ha='center', color='#e74c3c', fontweight='bold')

ax.text(5, 6.5, 'S&P 500: -157 pts (-2.71%)  |  Market Cap: -$1.56 Trillion',
        fontsize=14, ha='center', color='white')

# Left side - Crisis indicator
crisis_circle = Circle((2, 4.5), 0.8, color='#e74c3c', alpha=0.3, zorder=1)
ax.add_patch(crisis_circle)

ax.text(2, 4.5, '!',
        fontsize=80, ha='center', va='center', color='#e74c3c',
        fontweight='bold', zorder=2)

ax.text(2, 3.2, 'CRISIS?',
        fontsize=16, ha='center', color='#e74c3c', fontweight='bold')

# Arrow pointing to the right
arrow = FancyArrowPatch((3.2, 4.5), (4.5, 4.5),
                       arrowstyle='->', mutation_scale=40,
                       color='white', linewidth=4, alpha=0.8)
ax.add_artist(arrow)

# Right side - Opportunity indicator
opp_circle = Circle((8, 4.5), 0.8, color='#2ecc71', alpha=0.3, zorder=1)
ax.add_patch(opp_circle)

ax.text(8, 4.5, '$',
        fontsize=70, ha='center', va='center', color='#2ecc71',
        fontweight='bold', zorder=2)

ax.text(8, 3.2, 'OPPORTUNITY!',
        fontsize=16, ha='center', color='#2ecc71', fontweight='bold')

# Center text
ax.text(5, 4.7, 'OR',
        fontsize=20, ha='center', va='center', color='#95a5a6',
        fontweight='bold', style='italic')

# Bottom key message
message_box = FancyBboxPatch((1, 1.5), 8, 1.2, boxstyle="round,pad=0.15",
                            edgecolor='#3498db', facecolor='#2c3e50',
                            linewidth=3, alpha=0.9)
ax.add_patch(message_box)

ax.text(5, 2.35, 'When the market crashes, what separates investors',
        fontsize=14, ha='center', color='white')

ax.text(5, 1.95, 'is not account balance - it\'s INVESTMENT PHILOSOPHY',
        fontsize=16, ha='center', color='#3498db', fontweight='bold')

# Top corner annotation
ax.text(9.7, 9.5, 'YouXin Workshop',
        fontsize=11, ha='right', color='#95a5a6', style='italic')

ax.text(9.7, 9.2, 'Long-Term Investing Series',
        fontsize=9, ha='right', color='#7f8c8d', style='italic')

plt.tight_layout()

# Save image
output_path = 'assets/images/posts/2025/10/market-crash-guide.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#1a1a2e')
print(f"✅ Market crash hero image generated: {output_path}")

plt.close()
