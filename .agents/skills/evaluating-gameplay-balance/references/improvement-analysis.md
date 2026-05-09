# 游戏平衡改进分析

基于可重复的模拟或游玩测试遥测数据改进动作小游戏的指南。
目标是结构性改进规则、生成逻辑和状态转换，而非数值微调。

## 重要：规范护栏

项目特定的执行规则不在本参考文档范围内。本文档涵盖可复用的改进分析和实现模式。

注意事项：

- 即使本指南使用了探索比率，也应将该指标视为检测器而非优化目标。
- 将存活时间视为辅助指标，优先考虑体验品质。

## 1. 本指南的目的

分析可重复测试框架的输出日志，执行以下操作。

- **根本原因识别**：识别设计缺陷，而非仅看表面症状
- **结构性改进**：改变规则和生成算法
- **验证循环**：使用相同的指标集重新对比改进前后

## 2. 日志输入契约

首选的引擎无关契约定义在 `log-contract.md` 中。分析目标是以下结构。

```json
{
  "version": "1.0",
  "timestamp_utc": "2026-03-05T12:00:00",
  "run_config": {
    "seed_set": [2001, 2002, 2003],
    "fixed_dt": 0.0166667,
    "max_ticks": 3600,
    "policy_budget": "same before and after",
    "input_schema": {
      "primary": {"type": "boolean", "timing": ["pressed", "held", "released"]}
    },
    "visible_state_schema": ["player_position", "hazards", "rewards"],
    "policy_visibility": {
      "hold_action": [],
      "exploratory": ["player_position", "hazards", "rewards"]
    }
  },
  "monotonous": {
    "cases": {
      "no_input":     {"score": 0,  "elapsed": 4.2,  "ended": true},
      "hold_action":  {"score": 30, "elapsed": 16.7, "ended": true},
      "spam_action":  {"score": 42, "elapsed": 18.1, "ended": true}
    },
    "max_score": 42
  },
  "exploratory": {
    "best": {"score": 95, "elapsed": 24.9, "ended": true},
    "best_seed": 2001,
    "best_variant": 3
  },
  "exploratory_ratio": 2.26,
  "telemetry": {
    "death_analysis": {},
    "spawn_analysis": {},
    "scoring_analysis": {},
    "input_analysis": {}
  }
}
```

- `monotonous.cases` 的默认键为 `no_input` / `hold_action` / `spam_action`；允许使用与游戏操控匹配的自定义策略。
- `run_config` 记录改进前后必须保持不变的对比条件，包括策略可见性。
- `exploratory_ratio` 放在顶层（`exploratory.best.score / monotonous.max_score`）。
- `telemetry` 的具体内容可能因游戏实现而异，但必须保留以下四个分析视角。

## 3. 日志分析视角

### 3.1 死亡分析

检查项：

- 死亡位置偏差（集中在相同坐标附近）
- 输入后 1-3 帧内频繁死亡
- 仅特定危险物具有不成比例的高死亡率

常见原因：

- 不可避免的生成
- 高速进入且无预警
- 不足的失败恢复设计（如无敌帧/击退）

相关平衡模式：`balance-patterns.md` 中的难度缩放、边界/失败和生成安全模式。

### 3.2 生成分析

检查项：

- 最小生成间隔低于反应极限
- 生成位置偏向屏幕某部分
- 危险物类型分布过度集中

常见原因：

- 不足的生成冷却设计
- 纯随机生成而无空间区域管理
- 难度提升时的约束释放过于突然

相关平衡模式：`balance-patterns.md` 中的生成间隔下限、安全距离、区域冷却和自适应生成模式。

### 3.3 得分分析

检查项：

- 只存在一条得分路径
- 对风险动作（擦弹等）没有差异化奖励
- 后期难度仅减少得分机会
- 输入量不应与得分过度关联（不要奖励原始输入次数本身）

常见原因：

- 仅有固定得分
- 无风险关联的倍率
- 各阶段奖励重新设计不足

相关平衡模式：`balance-patterns.md` 中的风险驱动得分、连击重置和放置/时机质量模式。

### 3.4 输入分析

检查项：

- `hold_primary` / `pulse_primary` 始终为最优
- 某个单一自定义策略模式始终为最优
- 探索性输入几乎没有优势（探索比率不提升）

常见原因：

- 每种输入状态无权衡
- 动作选择无上下文依赖
- 玩家状态机过于简单

相关平衡模式：`balance-patterns.md` 中的输入状态权衡、上下文输入语义、状态衰减和多资源张力模式。

### 3.5 体验完整性门槛

在 KPI 检查之前，以下条件必须成立。

- 失败原因可以解释为游戏世界内的危险
- 得分原因可以解释为游戏内事件因果关系
- 在至少 2 分钟的人工游玩中，没有不公平的即死或无法解释的得分变化

## 4. 问题模式与结构性修复

### 4.1 不可避免的死亡聚集

症状：

- 死亡在同一区域重复出现
- 无预警地受到伤害

不充分的应对：

```text
# Insufficient: only lower speed
hazard_speed = hazard_speed * 0.8
```

推荐的应对：

```text
# Better: spawn checks that preserve an escape route
spawn_hazard:
  repeat up to N candidates:
    candidate = random_spawn_point()
    if has_escape_route(candidate, player_position, player_radius):
      commit_spawn(candidate)
      stop
  if no candidate is fair:
    skip_or_delay_spawn

has_escape_route(candidate, player_position, player_radius):
  minimum_clearance = player_radius * 3
  return distance(candidate, player_position) >= minimum_clearance
```

### 4.2 单调输入主导

症状：

- 仅狂按或长按就能获得高分

不充分的应对：

```text
# Insufficient: only add a fixed cooldown
if action_cooldown > 0:
  ignore_action
```

推荐的应对：

```text
# Better: environment behavior changes by input state
apply_action_rule(action_mode):
  if action_mode is spam:
    heat += 0.25
    score_multiplier = 1.0
  if action_mode is rhythm:
    heat = max(0, heat - 0.1)
    score_multiplier = 1.5
  if action_mode is hold:
    charge += 0.2
    if charge exceeds safe_limit:
      expose_hitbox_or_reduce_mobility
```

### 4.3 平坦的难度曲线

`difficulty` 约定：初始值 `1`，之后每经过一分钟 `+1`（参见 `balance-patterns.md` §1）。

症状：

- 前期和后期游玩感觉相同
- 难度增加只是"变快了"

不充分的应对：

```text
# Insufficient: linear increment only
difficulty += elapsed_delta * constant
```

推荐的应对：

```text
# Better: add readable phase transitions
update_phase(elapsed_seconds):
  if elapsed_seconds < early_limit: phase = early
  else if elapsed_seconds < mid_limit: phase = middle
  else: phase = late

apply_phase_rules:
  early:
    complex_hazard = off
    warning_time = generous
  middle:
    complex_hazard = on
    warning_time = moderate
  late:
    complex_hazard = on
    mastery_bonus = on
    warning_time = short_but_reactable
```

### 4.4 空间分布偏差

症状：

- 生成点偏向中心或边缘
- 未使用的屏幕区域变成固定死角

推荐的应对：

```text
# Better: spawn with cell cooldown
last_spawn_time_by_cell = {}
cell_cooldown = fixed_reaction_window

choose_spawn_cell(cells, now):
  best_cell = none
  best_score = negative_infinity
  for each cell:
    if now - last_spawn_time_by_cell[cell.id] < cell_cooldown:
      continue
    score = distance_from_player(cell) + route_fairness(cell)
    if score > best_score:
      best_score = score
      best_cell = cell
  return best_cell
```

## 5. 改进流程

### 5.1 获取基线日志

从项目的可重复测试框架收集基线日志。

需要保留的最小值：

- `monotonous.max_score`
- `exploratory.best.score`
- `exploratory_ratio`
- `telemetry`（death_analysis / spawn_analysis / scoring_analysis / input_analysis）

### 5.2 生成改进提案

每次改进聚焦一个问题。

- 问题名称
- 根本原因（逻辑层面）
- 要修改的目标模块/脚本/系统（按职责划分）
- 变更详情（规则/生成/状态转换）
- 预期效果（哪些指标会变化以及如何变化）
- 体验假设（玩家学到什么、什么感觉好）
- 预期副作用（不公平/单调的风险）

### 5.3 实现并重新测试

- 从 `balance-patterns.md` 中应用**一个**适用的模式
- 重新测试并再次对比探索比率和辅助指标
- 如果恶化，尝试另一个模式而非立即回滚

### 5.4 状态快照策略（可选）

将生成的截图或状态摘要视为**状态一致性证据**，而非精确的最终渲染评判。

- 用途：
  - 可重复地记录场景 A/B/C 阶段差异（低密度/高密度/受伤前后）
  - 验证放置、密度和主角/危险/奖励角色的分离
- 非用途：
  - 评判辉光、后处理效果、字体或最终 UI 外观的品质
- 实现建议：
  - 从测试框架调用类似 `capture_debug_frame(path)` 的 API 从游戏状态生成图像
  - 固定截图时机（编码场景 A/B/C 条件）并优先保证可比性
  - 如果引擎的渲染截图在自动化中不稳定，则使用状态快照方法作为权威依据
- 评判操作：
  - Web/人工游玩截图是视觉品质的权威来源
  - 将 headless 图像限制在 CI 回归检查中（构图/密度/角色分解检测）

#### 最小实现模式

提供可从测试中调用的图像生成或状态摘要 API。

```text
capture_debug_frame(path):
  snapshot = world.get_capture_snapshot()
  image = create_blank_image(render_width, render_height, background_color)
  for each hazard in snapshot.hazards:
    draw_rect(image, hazard.bounds, hazard_debug_color)
  draw_player_marker(image, snapshot.player_position)
  save_image(image, path)
```

在固定场景条件下从自动化测试框架调用。

```text
# test harness pseudocode
capture_state_summaries(game):
  game.reset(seed_for_low_density)
  step_until_low_density_condition(game)
  game.capture_debug_frame("logs/screens/scene_a.png")

  game.reset(seed_for_high_density)
  step_until_high_density_condition(game)
  game.capture_debug_frame("logs/screens/scene_b.png")

  game.reset(seed_for_near_failure)
  step_until_near_failure_condition(game)
  game.capture_debug_frame("logs/screens/scene_c.png")
```

回退规则：

- 如果 `capture_debug_frame` 未实现，视为失败（测试不通过），而非使用纯色占位图
- 将场景 A/B/C 的种子和帧条件固定为常量，使对比轴在改进后保持稳定

## 6. 评估标准

### 6.1 主要指标

| 探索比率 | 评估 | 含义 |
| :--- | :--- | :--- |
| <= 1.0 | 不通过 | 单调输入为最优 |
| 1.0 - 1.5 | 需要改进 | 技巧差异较弱 |
| > 1.5 | 通过 | 技巧性操作得到了奖励 |

### 6.2 辅助指标

| 指标 | 良好状态 | 问题状态 |
| :--- | :--- | :--- |
| 死亡多样性 | 分散在多个原因中 | 集中在单一原因 |
| 生成公平性 | 最小间隔可反应 | 连续即死间隔 |
| 得分路径 | 两条或以上得分路径 | 仅固定动作 |
| 输入主导性 | 探索性更优 | 狂按/长按始终获胜 |

### 6.3 强制体验门槛

如果以下任一项为"否"，即使探索比率很高也应判定为不通过。

| 门槛 | 通过条件 |
| :--- | :--- |
| 得分因果关系 | 得分与事件因果关系绑定，而非原始输入事实 |
| 失败因果关系 | 失败与游戏世界内危险绑定，而非不行动的元惩罚 |
| 人工合理性检查 | 至少 2 分钟人工游玩未增加不公平感 |

## 7. 反模式

### ❌ 仅调参数

```text
enemy_speed *= 0.8
spawn_interval += 0.2
```

### ❌ 仅加条件分支

```text
if too_hard:
  make_easier()
```

### ❌ 随机性蔓延

```text
spawn_position.y += random_range(-80, 80)
```

### ❌ 仅 UI 补偿

- 仅添加 HUD 文字而未解决根本问题
- 用文字说明掩盖反馈缺陷

### ❌ KPI 篡改

```text
# Awarding points for raw input facts (prohibited)
if input_pressed:
  score += 1

# Instant game over for non-movement fact alone (prohibited)
if idle_time > 1.5:
  trigger_game_over()
```

## 8. 推荐变更集模板

```markdown
## Problem Analysis

### Problem 1: <name>
- Symptom:
- Root cause:
- Impact:

## Improvement Proposal

### Improvement 1: <name>
- Target script:
- Structural change:
- Why it should work:

## Expected Effect
- Exploratory ratio: <before> -> <after target>
- Secondary metrics:
```

## 9. 改进前后验证模板

```markdown
| Metric | Before | After |
|:---|:---|:---|
| monotonous.max_score |  |  |
| exploratory.best.score |  |  |
| exploratory_ratio |  |  |
| death diversity |  |  |
| spawn fairness |  |  |
```

每次改进都创建此对比表，最多循环 3 次后停止。
