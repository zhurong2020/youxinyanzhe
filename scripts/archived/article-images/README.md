# Article Image Generation Scripts Archive

这个目录存放用于生成博文配图的临时Python脚本。

## 归档原因

这些脚本是为特定文章一次性生成配图而编写的临时工具，文章完成后不再需要频繁使用。

## 脚本列表

### 市场暴跌文章配图（2025-10-12）

1. **generate_market_crash_hero.py**
   - 用途：生成文章头图 `market-crash-guide.png`
   - 特点：危机与机遇视觉对比设计

2. **generate_crash_history_chart.py**
   - 用途：生成历史暴跌对比图 `market-crash-history-comparison.png`
   - 数据：2020新冠、2022加息、2025 DeepSeek事件对比

3. **generate_trading_hours_chart.py**
   - 用途：生成交易时间窗口图 `trading-hours-windows.png`
   - 内容：周五盘后、周一盘前、周一常规交易3个时间窗口

4. **generate_trading_hours_comparison.py**
   - 用途：生成交易时长对比图 `trading-hours-comparison.png`
   - 数据：A股972h vs 美股4,016h年度对比

5. **generate_trading_strategies_advantage.py**
   - 用途：生成交易策略优势对比图（未使用）
   - 说明：最终使用AI生成的图片替代

## 技术规范

- **语言**：Python 3
- **依赖**：matplotlib
- **文本要求**：所有图表文本使用英文（避免中文字体问题）
- **输出格式**：PNG，300 DPI
- **色彩方案**：深色背景 (#1a1a2e)，专业金融风格

## 如何使用

如果需要重新生成或修改图片：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行脚本
python scripts/archived/article-images/generate_xxx.py
```

## 归档日期

2025-10-11

## 相关文章

- [市场暴跌时的长期投资者指南：坚守还是离场？](_drafts/2025-10-12-market-crash-long-term-investor-guide.md)
