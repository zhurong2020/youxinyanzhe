#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate historical market crash comparison chart (English only)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Remove Chinese font configuration - use English only
plt.rcParams['axes.unicode_minus'] = False

# Data
events = [
    {
        'name': '2020 Mar\nCOVID-19 Crash',
        'crash': -12.5,
        'recovery': 16.3,
        'time': 'By end of 2020'
    },
    {
        'name': '2022\nFed Rate Hikes',
        'crash': -18.1,
        'recovery': 24.2,
        'time': '2023 recovery'
    },
    {
        'name': '2025 Jan\nDeepSeek Event',
        'crash': -15.0,
        'recovery': 12.0,
        'time': 'Few months later'
    }
]

# Create figure with more height to avoid overlap
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

# Set positions with more spacing
x_pos = np.arange(len(events)) * 1.3  # Increase spacing between bars
width = 0.35

# Draw crash bars (red)
crashes = [e['crash'] for e in events]
bars1 = ax.bar(x_pos - width/2, crashes, width, label='Crash Magnitude',
               color='#e74c3c', alpha=0.9, edgecolor='white', linewidth=1.5)

# Draw recovery bars (green)
recoveries = [e['recovery'] for e in events]
bars2 = ax.bar(x_pos + width/2, recoveries, width, label='Subsequent Recovery',
               color='#2ecc71', alpha=0.9, edgecolor='white', linewidth=1.5)

# Add value labels
for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    height1 = bar1.get_height()
    height2 = bar2.get_height()

    ax.text(bar1.get_x() + bar1.get_width()/2., height1 - 1,
            f'{height1:.1f}%', ha='center', va='top',
            color='white', fontsize=12, fontweight='bold')

    ax.text(bar2.get_x() + bar2.get_width()/2., height2 + 1,
            f'+{height2:.1f}%', ha='center', va='bottom',
            color='white', fontsize=12, fontweight='bold')

    # Add recovery time annotation
    ax.text(x_pos[i], -22, events[i]['time'],
            ha='center', va='top', color='#95a5a6',
            fontsize=10, style='italic')

# Set labels and title
ax.set_xlabel('')
ax.set_ylabel('Return (%)', fontsize=14, color='white', fontweight='bold')
ax.set_title('Historical Market Crashes & Recoveries: Long-Term Perspective',
             fontsize=16, color='white', fontweight='bold', pad=20)

# Set x-axis labels with better spacing
ax.set_xticks(x_pos)
ax.set_xticklabels([e['name'] for e in events], fontsize=10, color='white', linespacing=1.3)

# Set y-axis
ax.set_ylim(-25, 30)
ax.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)
ax.tick_params(axis='y', labelcolor='white', labelsize=11)
ax.grid(axis='y', alpha=0.2, color='white', linestyle='--')

# Legend - move to upper left to avoid overlap with insight box
legend = ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
legend.get_frame().set_facecolor('#16213e')
legend.get_frame().set_edgecolor('white')
for text in legend.get_texts():
    text.set_color('white')

# Add annotation
ax.text(0.5, 0.02, 'Data Source: S&P 500 Historical Data  |  Conclusion: Long-term investors who held through crashes all achieved positive returns',
        transform=ax.transAxes, ha='center', va='bottom',
        fontsize=10, color='#95a5a6', style='italic')

# Add key insight box - slightly lower position to avoid overlap
textstr = 'KEY INSIGHT:\nFor 10-20 year\ninvestment horizon,\ntoday\'s crash is just\na tiny blip'
props = dict(boxstyle='round', facecolor='#e74c3c', alpha=0.85, edgecolor='white', linewidth=2)
ax.text(0.97, 0.88, textstr, transform=ax.transAxes, fontsize=10.5,
        verticalalignment='top', horizontalalignment='right', bbox=props, color='white',
        fontweight='bold', linespacing=1.4)

plt.tight_layout()

# Save image
output_path = 'assets/images/posts/2025/10/market-crash-history-comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#1a1a2e')
print(f"✅ Historical crash comparison chart generated: {output_path}")

plt.close()
