---
author_profile: true
breadcrumbs: true
categories:
- 技术赋能
- 认知升级
comments: true
date: 2025-09-24 10:30:00
excerpt: 授人以鱼不如授人以渔。从Python基础到策略架构，从参数优化到风控设计，手把手教你改造定投策略，实现从使用者到创造者的蜕变。
header:
  overlay_filter: 0.5
  overlay_image: assets/images/posts/2025/09/strategy-modification-cover.png
  teaser: assets/images/posts/2025/09/strategy-modification-teaser.png
last_modified_at: '2025-09-24 10:45:50'
layout: single
related: true
share: true
title: 开源定投策略改造指南：从使用者到创造者
toc: true
toc_icon: list
toc_label: 本页内容
toc_sticky: true
---

授人以鱼不如授人以渔。本文将带你深入理解Moomoo定投策略的核心架构，掌握参数优化的科学方法，并学会根据自己的需求改造策略。从突破10股限制到设计个性化回撤系统，让我们一起踏上从使用者到创造者的进阶之路。

<!-- more -->

## 🎧 音频版本

如果您更喜欢收听而非阅读，我们提供了本文的音频版本：

📹 **YouTube播客**：[点击收听](https://youtu.be/example){:target="_blank"}
⏱️ **时长**：约25分钟
🎯 **适合场景**：通勤路上、运动时、做家务时

音频版本包含了文章的核心内容，配合代码示例阅读效果更佳。

---

## 系列文章导航

本文是TQQQ定投策略系列的第3篇（完结篇）：
- 第1篇：[回测分析——从-60%回撤到盈利](https://zhurong2020.github.io/youxinyanzhe/posts/2025/09/from-60-percent-drawdown-to-profit-turnaround/){:target="_blank"}
- 第2篇：[TQQQ定投深度剖析：为什么周投能赢日投？](https://zhurong2020.github.io/youxinyanzhe/posts/2025/09/tqqq-weekly-vs-daily-analysis/){:target="_blank"}
- **第3篇：开源定投策略改造指南**（本文）

---

## 引言：为什么要学会改造策略？

在前两篇文章中，我们展示了定投策略在2025年TQQQ暴跌60%后仍能获得33%-51%收益的惊人表现。但更重要的是：**你应该理解并掌握这个策略，而不是盲目使用**。

> 💡 **核心理念**：
> - 知其然，更要知其所以然
> - 授人以渔，而非授人以鱼
> - **免费版已具备完整功能**，可自由改造升级
> - **完整版是作者实践经验**，提供参考思路

### 量化策略解决了什么问题？

**手工定投的痛点**：
- 😰 **择时焦虑**："今天涨了，要不要等回调？"
- 😟 **执行困难**："又忘记定投了..."
- 😵 **情绪干扰**："跌这么多，还要继续投吗？"
- 😫 **缺乏纪律**："这次先不投了，等等再说"

**量化定投的优势**：
- ✅ **自动执行**：启动策略，一切交给程序
- ✅ **克服人性**：不受恐惧贪婪影响
- ✅ **纪律保障**：严格按计划执行
- ✅ **数据驱动**：基于回测优化参数

## 1. 策略架构解析

### 1.1 Moomoo量化策略标准框架

> 📚 **查看官方文档**：在Moomoo量化功能界面，点击右上角的"查看量化文档"可获取完整API说明。
>
> 💎 **完整版福利**：购买完整版策略的用户将额外获得：
> - 📄 《Moomoo量化策略框架具体说明》整理版
> - 📄 《Moomoo量化功能常用API函数及其用法》完整版
> - 包含46个API函数的详细说明和示例代码

> ⚠️ **重要版本提示**：
> - 本策略已在**Moomoo Windows版本**下测试通过
> - 下载Moomoo时请选择**Legacy版本**（传统版本）
> - Legacy版本拥有更稳定的量化功能支持
> - 下载地址：在Moomoo官网下载页面选择"Previous versions"

Moomoo量化策略基于Python，采用标准化的三层框架设计：

```python
# Moomoo策略的标准框架（必须遵循）
class Strategy(StrategyBase):  # 类名必须是Strategy
    def initialize(self):  # 初始化，仅在策略启动时运行一次
        self.trigger_symbols()  # 约定函数1：定义运行标的
        self.custom_indicator()  # 约定函数2：注册指标
        self.global_variables()  # 约定函数3：定义全局变量

    def trigger_symbols(self):    # 定义运行标的（最多8个）
        self.运行标的1 = declare_trig_symbol()
        self.运行标的2 = declare_trig_symbol()

    def global_variables(self):   # 定义全局变量
        self.a = 10  # 数值型全局变量
        self.b = Contract('US.AAPL')  # 标的型全局变量

    def custom_indicator(self): # 注册自定义指标
        # 使用麦语言注册指标
        self.register_indicator(
            indicator_name='MA',
            script='''MA1:MA(CLOSE,P1),COLORFF8D1E;''',
            param_list=['P1']
        )

    def handle_data(self):  # 主函数，每次收到触发信号会运行一次
        ## 策略的执行逻辑写在这里
        pass
```

### 1.2 框架核心要点

**三个层面的函数体系**：
1. **基础框架函数**（必须包含）：
   - `initialize()`: 策略启动时运行一次，完成初始化
   - `handle_data()`: 按设定周期重复运行，执行交易逻辑

2. **约定函数**（在initialize中调用）：
   - `trigger_symbols()`: 设置交易标的和触发周期（最多8个标的）
   - `custom_indicator()`: 定义技术指标（使用麦语言）
   - `global_variables()`: 设置策略参数

3. **自定义函数**（根据需求添加）：
   - 计算函数：如计算网格价格、持仓等
   - 交易函数：如执行买入、卖出逻辑
   - 风控函数：如止损、仓位控制等

> ⚠️ **重要提示**：
> - **类名必须是`Strategy`**，不能使用其他名称
> - 不要在`initialize()`内增加过多逻辑，会导致策略启动缓慢
> - Python标准库支持，但禁用了读写硬盘、网络请求等功能
> - 自定义变量名不能与内置API函数重名

### 1.3 免费版策略核心架构

免费版采用3层回撤定投系统，核心参数如下：

```python
# 核心参数配置（示例）
DRAWDOWN_LAYERS = [5, 15, 20]  # 回撤阈值：5%、15%、20%
MULTIPLIERS = [1.2, 1.5, 1.8]  # 对应加仓倍数
BASE_SHARES = 5  # 基础定投股数
INTERVAL_DAYS = 7  # 定投间隔（天）
MAX_SHARES_PER_ORDER = 10  # 单次最大买入限制
```

### 1.3 策略执行流程

```
开始
  ↓
检查间隔时间 → 不满足 → 等待下一周期
  ↓ 满足
计算当前回撤
  ↓
匹配回撤层级
  ↓
计算买入数量 = 基础量 × 层级倍数
  ↓
执行买入
  ↓
更新持仓信息
```

## 2. 从简单修改开始

### 2.1 突破10股限制（入门改造）

**问题**：默认单次最多买10股，大资金不够用怎么办？

**探索思路**：
1. 🔍 搜索关键词："10"、"max"、"limit"
2. 📍 定位到`MAX_SHARES_PER_ORDER`变量
3. 🔧 修改为你需要的数值

```python
# 原始代码（在global_variables函数中）
def global_variables(self):
    self.MAX_SHARES_PER_ORDER = 10

# 改造示例1：提升固定限制
def global_variables(self):
    self.MAX_SHARES_PER_ORDER = 50  # 提升到50股

# 改造示例2：根据资金动态调整（使用Moomoo API）
def handle_data(self):
    # 获取当前账户总现金（USD）
    account_cash = total_cash(currency=Currency.USD)

    if account_cash > 100000:
        max_shares = 100
    elif account_cash > 50000:
        max_shares = 50
    else:
        max_shares = 10

    # 执行买入逻辑
    shares_to_buy = min(max_shares, calculated_shares)
```

> ⚠️ **注意事项**：
> - 大额订单可能影响成交价格
> - 建议分批买入，避免冲击成本
> - 考虑标的流动性

### 2.2 修改投资频率（基础改造）

**从周投改为日投**：

```python
# 原始：每周投资
INTERVAL_DAYS = 7

# 改造1：每日投资
INTERVAL_DAYS = 1

# 改造2：工作日投资（需要额外逻辑）
import datetime

def is_trading_day(date):
    """判断是否为交易日"""
    # 跳过周末
    if date.weekday() >= 5:
        return False
    # 跳过美国节假日（需要节假日列表）
    if date in US_HOLIDAYS:
        return False
    return True

# 改造3：动态频率（市场越跌投得越频繁）
def get_dynamic_interval(drawdown):
    """根据回撤动态调整频率"""
    if drawdown > 20:
        return 1  # 大跌时每日投
    elif drawdown > 10:
        return 3  # 中等回撤每3天投
    else:
        return 7  # 正常情况每周投
```

### 2.3 个性化买入金额

**需求**：不想按股数，想按金额定投

```python
# 原始：按股数
shares_to_buy = BASE_SHARES * multiplier

# 改造：按金额
TARGET_AMOUNT = 1000  # 每次投$1000
current_price = get_current_price()
shares_to_buy = int(TARGET_AMOUNT / current_price)

# 更进一步：金额也分层
AMOUNT_LAYERS = [500, 1000, 2000, 5000]  # 不同回撤对应的金额
drawdown_index = get_drawdown_layer_index(current_drawdown)
target_amount = AMOUNT_LAYERS[drawdown_index]
shares_to_buy = int(target_amount / current_price)
```

## 3. 进阶改造：设计你的回撤系统

### 3.1 理解回撤层级设计

免费版的[5%, 15%, 20%]是一个相对保守的设置。让我们看看如何根据不同需求设计：

```python
# 保守型投资者（适合SPY/VOO）
CONSERVATIVE_LAYERS = [3, 6, 10, 15]
CONSERVATIVE_MULTIPLIERS = [1.1, 1.2, 1.3, 1.5]

# 平衡型投资者（适合QQQ）
BALANCED_LAYERS = [5, 10, 15, 20, 25]
BALANCED_MULTIPLIERS = [1.2, 1.5, 2.0, 2.5, 3.0]

# 激进型投资者（适合TQQQ）
AGGRESSIVE_LAYERS = [5, 10, 15, 20, 30, 40, 50]
AGGRESSIVE_MULTIPLIERS = [1.2, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0]

# 完整版的设计思路（7层系统）
COMPLETE_LAYERS = [5, 10, 15, 20, 30, 50, 70]
COMPLETE_MULTIPLIERS = [1.2, 1.5, 2.0, 3.0, 5.0, 7.0, 10.0]
```

### 3.2 加入激进乘数（高级特性）

完整版的一个亮点是"激进乘数"，在极端行情时加大投入：

```python
def calculate_aggressive_multiplier(drawdown, volatility):
    """计算激进乘数"""
    base_multiplier = 1.0

    # 基于回撤深度
    if drawdown > 50:
        base_multiplier = 2.0
    elif drawdown > 30:
        base_multiplier = 1.5
    elif drawdown > 20:
        base_multiplier = 1.2

    # 基于市场恐慌指数（VIX）
    if volatility > 30:  # VIX > 30表示极度恐慌
        base_multiplier *= 1.3

    # 设置上限，避免过度激进
    return min(base_multiplier, 2.0)

# 应用激进乘数
final_shares = base_shares * layer_multiplier * aggressive_multiplier
```

### 3.3 智能化改造：自适应参数

```python
class AdaptiveStrategy:
    """自适应定投策略"""

    def __init__(self):
        self.performance_history = []
        self.parameter_sets = [
            {'layers': [5, 15, 20], 'mults': [1.2, 1.5, 1.8]},
            {'layers': [5, 10, 15, 25], 'mults': [1.3, 1.6, 2.0, 2.5]},
            {'layers': [10, 20, 30], 'mults': [1.5, 2.0, 3.0]}
        ]
        self.current_params = 0

    def evaluate_performance(self):
        """评估当前参数表现"""
        recent_performance = calculate_recent_returns()
        self.performance_history.append(recent_performance)

        # 如果连续3个月表现不佳，切换参数
        if len(self.performance_history) >= 3:
            if all(p < 0 for p in self.performance_history[-3:]):
                self.switch_parameters()

    def switch_parameters(self):
        """切换到下一组参数"""
        self.current_params = (self.current_params + 1) % len(self.parameter_sets)
        params = self.parameter_sets[self.current_params]
        self.update_strategy(params['layers'], params['mults'])
```

## 4. 回测验证：改造成功的试金石

### 4.1 回测的重要性

> 🚨 **铁律**：没有充分回测，绝不投入真金白银！

一个改造是否成功，回测数据会告诉你答案。基于前两篇文章的数据，我们知道：
- TQQQ在2025年1-9月经历了-60%的极端回撤
- 免费版策略获得了33%-36%的收益
- 完整版策略获得了51%的收益

### 4.2 回测检查清单

```python
def backtest_checklist():
    """回测检查清单"""
    tests = {
        '2020疫情暴跌': test_covid_crash(),      # 测试V型反弹
        '2022熊市': test_2022_bear(),             # 测试持续下跌
        '2025极端回撤': test_2025_crash(),        # 测试60%回撤
        '横盘震荡': test_sideways_market(),       # 测试震荡市
        '单边上涨': test_bull_market()            # 测试牛市
    }

    for scenario, result in tests.items():
        print(f"{scenario}:")
        print(f"  收益率: {result['return']:.2%}")
        print(f"  最大回撤: {result['max_drawdown']:.2%}")
        print(f"  夏普比率: {result['sharpe_ratio']:.2f}")
```

### 4.3 参数优化实战

基于TQQQ的特性（高波动、深回撤），我们可以这样优化：

```python
# 参数优化示例
import itertools

def optimize_parameters():
    """网格搜索最优参数"""

    # 参数空间
    layer_options = [
        [5, 15, 25],
        [5, 15, 30],
        [10, 20, 30],
        [5, 10, 20, 30]
    ]

    multiplier_options = [
        [1.2, 1.5, 2.0],
        [1.3, 1.8, 2.5],
        [1.5, 2.0, 3.0],
        [1.2, 1.5, 2.0, 3.0]
    ]

    best_params = None
    best_return = -float('inf')

    # 遍历所有组合
    for layers, mults in itertools.product(layer_options, multiplier_options):
        if len(layers) != len(mults):
            continue

        result = backtest_with_params(layers, mults)

        # 综合评分（不只看收益率）
        score = (result['return'] * 0.5 +
                -result['max_drawdown'] * 0.3 +
                result['sharpe_ratio'] * 0.2)

        if score > best_return:
            best_return = score
            best_params = (layers, mults)

    return best_params
```

## 5. 实战案例：从失败中学习

### 5.1 案例一：过度激进的教训

```python
# ❌ 失败的改造
CRAZY_LAYERS = [5, 10, 15]
CRAZY_MULTIPLIERS = [5, 10, 20]  # 太激进了！

# 回测结果：
# - 小幅下跌就用光了所有资金
# - 无法应对持续下跌
# - 最终爆仓
```

**教训**：加仓倍数要循序渐进，给自己留有余地。

### 5.2 案例二：频率过高的代价

```python
# ❌ 每小时定投
INTERVAL_HOURS = 1  # 太频繁了！

# 问题：
# 1. 手续费侵蚀利润
# 2. 无法有效降低成本
# 3. 心理压力巨大
```

**教训**：交易频率要适度，考虑手续费成本。

### 5.3 案例三：成功的平衡

```python
# ✅ 成功的改造（某群友分享）
# 针对TQQQ优化的5层系统
MY_LAYERS = [5, 10, 20, 35, 50]
MY_MULTIPLIERS = [1.2, 1.5, 2.5, 4.0, 6.0]

# 加入市场情绪判断
def get_market_sentiment():
    vix = get_vix_value()
    if vix > 30:  # 恐慌
        return 1.5
    elif vix < 20:  # 贪婪
        return 0.8
    else:
        return 1.0

# 结果：2025年1-9月收益率45%，介于免费版和完整版之间
```

## 6. 进阶技巧：多策略组合

### 6.1 策略组合思路

不要把鸡蛋放在一个篮子里，可以同时运行多个策略：

```python
# 策略组合示例
strategies = {
    'conservative_dca': {
        'target': 'SPY',
        'allocation': 0.4,  # 40%资金
        'params': conservative_params
    },
    'balanced_dca': {
        'target': 'QQQ',
        'allocation': 0.3,  # 30%资金
        'params': balanced_params
    },
    'aggressive_dca': {
        'target': 'TQQQ',
        'allocation': 0.2,  # 20%资金
        'params': aggressive_params
    },
    'cash_reserve': {
        'allocation': 0.1  # 10%现金储备
    }
}
```

### 6.2 风险管理增强

```python
class RiskManagedStrategy:
    """带风险管理的定投策略"""

    def __init__(self):
        self.max_position_pct = 0.8  # 最大仓位80%
        self.stop_loss_pct = 0.3     # 止损线30%
        self.take_profit_pct = 0.5   # 止盈线50%

    def check_risk_limits(self):
        """检查风险限制"""
        # 仓位控制
        if self.position_value / self.total_value > self.max_position_pct:
            return "PAUSE"  # 暂停买入

        # 止损检查
        if self.unrealized_loss_pct > self.stop_loss_pct:
            return "REDUCE"  # 减仓

        # 止盈检查
        if self.unrealized_gain_pct > self.take_profit_pct:
            return "TAKE_PROFIT"  # 部分止盈

        return "NORMAL"
```

## 7. 学习路径与社区文化

### 7.1 四步学习法

1. **理解原理**（第1周）
   - 读懂每个函数的作用
   - 理解策略执行流程
   - 运行回测，观察结果

2. **简单修改**（第2周）
   - 修改基础参数
   - 调整投资频率
   - 改变买入数量

3. **深度改造**（第3-4周）
   - 设计自己的回撤系统
   - 添加新功能
   - 优化参数组合

4. **创新突破**（第2个月）
   - 开发全新策略
   - 结合其他指标
   - 分享社区，获得反馈

### 7.2 常见问题解答

**Q1：完全不懂Python怎么办？**
A：可以借助ChatGPT/Claude等AI工具辅助理解和修改代码。先从最简单的参数修改开始。

**Q2：改坏了怎么办？**
A：始终保留原始版本备份。每次修改前复制一份，改坏了可以恢复。

**Q3：如何知道改造是否成功？**
A：看三个指标：
- 回测收益率是否提升
- 最大回撤是否可控
- 夏普比率是否改善

**Q4：需要多久能学会？**
A：因人而异。有编程基础1-2周，零基础1-2个月。关键是持续练习。

## 8. 完整代码示例

这里提供一个符合Moomoo官方框架的完整定投策略示例：

```python
"""
Moomoo量化定投策略示例
符合官方框架要求，可直接在量化平台运行
"""

class Strategy(StrategyBase):  # 注意：类名必须是Strategy
    def initialize(self):
        """初始化函数，策略启动时运行一次"""
        self.trigger_symbols()    # 定义运行标的
        self.custom_indicator()    # 注册指标
        self.global_variables()    # 定义全局变量

    def trigger_symbols(self):
        """定义运行标的（最多8个）"""
        self.运行标的1 = declare_trig_symbol()  # 将在运行时指定具体标的

    def custom_indicator(self):
        """注册自定义指标（如需要）"""
        # 注册20日均线指标
        self.register_indicator(
            indicator_name='MA20',
            script='''MA20:MA(CLOSE,20),COLORFF8D1E;''',
            param_list=[]
        )

    def global_variables(self):
        """定义全局变量 - 策略参数配置区"""
        # ========== 可修改参数区 ==========
        # 基础参数
        self.base_shares = show_variable(5, GlobalType.FLOAT)  # 基础定投股数
        self.interval_days = 7  # 定投间隔（天）

        # 回撤层级设置（可自定义）
        self.drawdown_layers = [5, 10, 20, 30]  # 回撤阈值
        self.multipliers = [1.2, 1.5, 2.5, 4.0]  # 对应加仓倍数

        # 高级参数
        self.use_aggressive_mode = True  # 是否启用激进模式
        self.max_shares_per_order = 50  # 单次最大买入股数

        # 内部变量（策略运行时使用）
        self.last_buy_time = None
        self.high_price = 0
        self.total_cost = 0
        self.total_shares = 0

    def handle_data(self):
        """主函数，每次收到触发信号运行一次"""
        # 获取当前价格
        symbol = self.运行标的1
        current_price = current_price(symbol, THType.FTH)

        if current_price <= 0:
            return

        # 更新历史最高价
        if current_price > self.high_price:
            self.high_price = current_price

        # 计算回撤
        if self.high_price > 0:
            drawdown = (self.high_price - current_price) / self.high_price * 100
        else:
            drawdown = 0

        # 获取当前时间
        current_time = device_time(TimeZone.DEVICE_TIME_ZONE)

        # 判断是否应该买入
        should_buy = False
        if self.last_buy_time is None:
            should_buy = True
        else:
            days_passed = (current_time - self.last_buy_time).days
            if days_passed >= self.interval_days:
                should_buy = True

        if not should_buy:
            return

        # 计算买入股数
        shares_to_buy = self.calculate_shares_to_buy(drawdown)

        # 检查资金是否充足
        available_cash = total_cash(currency=Currency.USD)
        required_cash = shares_to_buy * current_price

        if required_cash > available_cash:
            # 资金不足，调整买入数量
            shares_to_buy = int(available_cash / current_price)

        if shares_to_buy <= 0:
            print(f"资金不足，跳过本次定投")
            return

        # 执行买入
        try:
            # 下市价单
            order_id = place_market(
                symbol=symbol,
                qty=shares_to_buy,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )

            # 更新统计信息
            self.last_buy_time = current_time
            self.total_shares += shares_to_buy
            self.total_cost += shares_to_buy * current_price

            # 打印日志
            avg_cost = self.total_cost / self.total_shares if self.total_shares > 0 else 0
            print(f"执行定投: 买入{shares_to_buy}股 @ ${current_price:.2f}")
            print(f"回撤: {drawdown:.1f}%, 平均成本: ${avg_cost:.2f}")

        except Exception as e:
            print(f"下单失败: {e}")

    def calculate_shares_to_buy(self, drawdown):
        """根据回撤计算买入股数"""
        # 基础股数
        shares = float(self.base_shares)

        # 根据回撤层级获取倍数
        multiplier = 1.0
        for i, threshold in enumerate(self.drawdown_layers):
            if drawdown <= threshold:
                multiplier = self.multipliers[i]
                break
        else:
            # 超过最大阈值，使用最大倍数
            multiplier = self.multipliers[-1]

        # 计算加仓股数
        shares = shares * multiplier

        # 如果启用激进模式，深度回撤时额外加仓
        if self.use_aggressive_mode and drawdown > 30:
            shares = shares * 1.5

        # 限制最大股数
        shares = min(int(shares), self.max_shares_per_order)

        return shares

    def check_stop_loss(self):
        """检查止损条件（可选功能）"""
        # 获取当前持仓
        symbol = self.运行标的1
        position_qty = position_holding_qty(symbol)

        if position_qty <= 0:
            return

        # 获取持仓成本
        avg_cost = position_cost(symbol, CostPriceModel.AVG)
        current_price = current_price(symbol, THType.FTH)

        # 计算损失百分比
        loss_pct = (current_price - avg_cost) / avg_cost * 100

        # 如果损失超过30%，考虑止损
        if loss_pct < -30:
            print(f"触发止损警告: 损失{abs(loss_pct):.1f}%")
            # 可以在这里添加止损逻辑
```

### 关键API函数说明

```python
# 常用价格获取
current_price(symbol, THType.FTH)  # 获取最新价格
bid(symbol, level=1)  # 买一价
ask(symbol, level=1)  # 卖一价
mid_price(symbol)  # 买卖中间价

# 账户信息
total_cash(Currency.USD)  # 总现金
available_fund(Currency.USD)  # 可用资金
market_value_security(Currency.USD)  # 证券市值

# 持仓信息
position_holding_qty(symbol)  # 持仓数量（适用于股票和期权）
position_cost(symbol, CostPriceModel.AVG)  # 平均成本

# 下单函数
place_market(symbol, qty, side, time_in_force)  # 市价单
place_limit(symbol, price, qty, side, time_in_force)  # 限价单
cancel_order_by_symbol(symbol, TradeSide.ALL)  # 撤单

# 时间函数
device_time(TimeZone.DEVICE_TIME_ZONE)  # 获取当前时间

# K线数据
bar_high(symbol, BarType.H1, select=1)  # K线最高价
bar_custom(symbol, data_type, custom_num, custom_type)  # 自定义K线

# 策略控制
quit_strategy()  # 退出策略（止损清仓后使用）
```

> 🔥 **期权持仓检测重要提示**：
> - 使用 `position_holding_qty()` 检测个人期权持仓（负数=卖出，正数=买入）
> - 不要使用 `option_position()`，它返回的是市场总未平仓量，不是个人持仓
> - 完整版用户将获得包含此类重要发现的详细文档

## 9. 写在最后：从模仿到创新

### 9.1 成长路径总结

通过本系列三篇文章，我们完成了一个完整的学习闭环：

1. **第一篇**：看到策略的威力（33%-51%的实战收益）
2. **第二篇**：理解策略的原理（周投vs日投的数学逻辑）
3. **第三篇**：掌握改造的方法（从使用到创造）

### 9.2 核心收获

- 📊 **数据思维**：用回测验证，不凭感觉交易
- 🛠️ **动手能力**：能修改代码，解决实际问题
- 🎯 **系统思维**：理解策略设计的底层逻辑
- 💪 **独立能力**：从依赖他人到独立决策

### 9.3 持续进化

> "The best investment you can make is in yourself." - Warren Buffett

记住，真正的财富不是你赚了多少钱，而是你学到了什么，以及你能持续创造价值的能力。

每一行代码的修改，都是你投资能力的升级。
每一次回测的分析，都是你认知水平的提升。
每一个策略的改进，都是你独立思考的体现。

## 资源汇总

### 策略获取

**免费版策略**：
- 📦 完整源码 + 使用说明
- 🆓 可自由修改、分享、商用
- ✅ 功能完整，不是试用版
- 💡 建议先从免费版开始学习

**完整版策略**（¥299）：
- 📖 7层深度加仓系统
- 📊 5年回测数据包
- 📄 **Moomoo量化文档整理版**（2个文件）
  - 《Moomoo量化策略框架具体说明》
  - 《Moomoo量化功能常用API函数及其用法》（46个函数详解）
- 👥 VIP交流群
- 🎯 一对一安装指导
- ♻️ 后续版本免费升级

> 获取方式：评论区留言"策略获取"

### 学习资源

- **技术博客**：[zhurong2020.github.io](https://zhurong2020.github.io)
- **YouTube频道**：定期更新策略讲解视频
- **交流群**：加入社区，与同行者交流

### 重要提醒

> 🔔 **使用注意事项**：
> - Moomoo策略需要**每天手动启动**
> - 关闭软件后策略会停止运行
> - 建议设置开盘提醒，养成启动习惯
> - 可同时运行多个策略
> - **推荐使用Moomoo Windows Legacy版本**（传统版本）

---

## 系列总结

通过这个系列，我们探讨了：

1. **实战验证**：用真实数据证明策略有效性
2. **原理剖析**：深入理解投资频率的影响
3. **实践指南**：手把手教你改造优化策略

最重要的是：**开始行动，持续学习，共同成长**。

如果这个系列对你有帮助，欢迎：
- 💬 分享你的改造经验
- ⭐ 转发给需要的朋友
- 🎯 在评论区交流讨论

让我们一起在量化投资的道路上不断前行！

---

**免责声明**：
- 本文仅供教育参考，不构成投资建议
- 历史表现不代表未来收益
- 投资有风险，入市需谨慎

**作者简介**：前银行从业者，现专注于量化投资研究。坚信开源和分享的力量，致力于帮助普通投资者掌握科学的投资方法。

**#量化投资 #策略改造 #Python编程 #开源精神 #TQQQ定投**


{% assign investment_tags = 'QDII基金,指数投资,标普500,纳斯达克100,定投策略,基金投资,股票投资,投资理财,量化交易,投资策略,风险管理,资产配置,投资心理,美股投资,ETF投资' | split: ',' %}
{% assign show_investment_disclaimer = false %}
{% for tag in page.tags %}
  {% if investment_tags contains tag %}
    {% assign show_investment_disclaimer = true %}
    {% break %}
  {% endif %}
{% endfor %}

{% if show_investment_disclaimer %}
---

**💭 学习分享声明**：这里记录的是我在投资理财学习路上的个人思考和实践心得。正如《金钱心理学》所言："每个人的情况不同"，投资决策需要结合您的具体情况、风险承受能力和投资目标。本文仅供学习交流，不构成投资建议，请保持独立思考，持续学习。

{% endif %}

如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**: 您需要有一个 GitHub 账号来发表评论。