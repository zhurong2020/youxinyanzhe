#!/usr/bin/env python3
"""
Generate A-share vs US stock trading hours comparison chart
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Remove Chinese font configuration - use English only
plt.rcParams['axes.unicode_minus'] = False

# Set dark background style
plt.style.use('dark_background')

# Create figure with two subplots
fig = plt.figure(figsize=(14, 10))

# Subplot 1: Daily Trading Hours Comparison
ax1 = plt.subplot(2, 1, 1)

markets = ['A-Shares\n(China)', 'US Stocks\n(NYSE/NASDAQ)']
daily_hours = [4, 16]
colors = ['#e74c3c', '#2ecc71']

bars = ax1.barh(markets, daily_hours, color=colors, alpha=0.8, height=0.6)

# Add value labels
for i, (bar, hours) in enumerate(zip(bars, daily_hours)):
    width = bar.get_width()
    ax1.text(width + 0.3, bar.get_y() + bar.get_height()/2,
             f'{hours} hours/day',
             ha='left', va='center', fontsize=14, fontweight='bold')

# Add time period annotations
ax1.text(2, 0, '9:30-11:30, 13:00-15:00',
         ha='center', va='center', fontsize=11, color='white', alpha=0.7)

ax1.text(8, 1, 'Pre-market: 4:00-9:30 (5.5h)\nRegular: 9:30-16:00 (6.5h)\nAfter-hours: 16:00-20:00 (4h)',
         ha='center', va='center', fontsize=10, color='white', alpha=0.7)

ax1.set_xlabel('Trading Hours per Day', fontsize=13, fontweight='bold')
ax1.set_title('Daily Trading Hours Comparison', fontsize=16, fontweight='bold', pad=20)
ax1.set_xlim(0, 18)
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Subplot 2: Annual Total Trading Hours
ax2 = plt.subplot(2, 1, 2)

trading_days = [243, 251]
annual_hours = [972, 4016]

x = np.arange(len(markets))
width = 0.35

bars2 = ax2.bar(x, annual_hours, width, color=colors, alpha=0.8)

# Add value labels
for i, (bar, hours, days) in enumerate(zip(bars2, annual_hours, trading_days)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, height + 100,
             f'{hours:,} hours',
             ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax2.text(bar.get_x() + bar.get_width()/2, height/2,
             f'{days} days/year',
             ha='center', va='center', fontsize=11, color='white')

# Add percentage difference annotation
ax2.annotate('', xy=(1, 4016), xytext=(0, 972),
            arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))

ax2.text(0.5, 2500, '+313%\n(4x more)',
         ha='center', va='center', fontsize=14, fontweight='bold',
         color='yellow',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='black', edgecolor='yellow', alpha=0.7))

ax2.set_ylabel('Annual Total Trading Hours', fontsize=13, fontweight='bold')
ax2.set_title('Annual Total Trading Hours Comparison', fontsize=16, fontweight='bold', pad=20)
ax2.set_xticks(x)
ax2.set_xticklabels(markets, fontsize=12)
ax2.set_ylim(0, 4500)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Add overall title
fig.suptitle('A-Shares vs US Stocks: Trading Hours Comparison',
             fontsize=18, fontweight='bold', y=0.98)

# Add insight box
insight_text = ('Key Insight:\n'
               'While trading days are similar (243 vs 251),\n'
               'US stocks offer 4x more trading hours annually\n'
               'due to extended pre-market and after-hours sessions.')

fig.text(0.5, 0.02, insight_text,
         ha='center', va='bottom', fontsize=11,
         bbox=dict(boxstyle='round,pad=1', facecolor='#1a1a2e',
                  edgecolor='#4ecdc4', linewidth=2, alpha=0.9))

plt.tight_layout(rect=[0, 0.06, 1, 0.96])

# Save the chart
output_path = 'assets/images/posts/2025/10/trading-hours-comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#1a1a2e')
print(f"Chart saved to: {output_path}")

# Show file size
import os
file_size = os.path.getsize(output_path)
print(f"File size: {file_size/1024:.1f} KB")
