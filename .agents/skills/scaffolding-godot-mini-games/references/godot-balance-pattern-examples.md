# Godot 平衡模式示例

当遥测发现平衡问题并确定了结构性修复方案后，用于应用引擎无关平衡模式的 Godot/GDScript 示例。
本文件是自包含的：在展示 Godot 特定实现之前，先总结了可复用的模式类别。

## 概述

平衡调整分为以下几个类别：

1. **难度缩放** - 游戏参数如何随 `difficulty` 变量变化
2. **得分系统** - 风险/收益和连击机制
3. **边界行为** - 墙壁碰撞和屏幕边缘处理
4. **自我平衡机制** - 自动难度调整
5. **输入响应** - 按钮状态如何影响游戏行为
6. **生成模式** - 敌人和障碍物的放置

下方使用的引擎无关模式术语：

- 递减难度增长：用 `sqrt(difficulty)` 或其他减速曲线替代严格的线性缩放。
- 基于风险的得分：奖励险中求生、精确操作、路线成本或暴露于危险中。
- 可见的失败后果：用穿越、弹回、资源损失或连击损失替代不明确的即死，前提是这样做能保持公平性。
- 输入状态权衡：长按、点按和闲置应各自改善某一方面同时恶化另一方面。
- 生成公平性：拒绝出现在最小安全距离内或反复施压同一区域的危险物。
- 状态与领地压力：衰减累积优势，让玩家操作在世界中留下痕迹以影响后续决策。

## 护栏（应用模式前必读）

在带有 `AGENTS.md` 的仓库中使用时，该文件仍然是项目特定执行规则的信息源。本指南仅提供在这些规则下应用的可复用平衡模式。

快速提醒：

- 用简短的人工游玩验证变更，而非仅靠测试日志。

---

## 1. 难度缩放模式

### `difficulty` 变量约定

| 属性 | 值 |
|:---------|:------|
| 初始值 | `1` |
| 增量 | 每过一分钟 `+1` |
| 典型范围 | `1`–`5`（大多数游戏在 5 分钟内结束） |

本节所有模式都假设采用上述约定。游戏开始时 `difficulty = 1` 意味着 `sqrt(difficulty) = 1`，因此公式会优雅地降级到基础值。

### 模式 1.1：线性转平方根

**问题**：难度增长过快，游戏变得无法游玩。

**诊断**：`telemetry.death_analysis` 显示死亡集中在高难度阶段。

**修改前**：
```gdscript
var speed := 0.5 + difficulty * 0.1
var spawn_rate := 60.0 - difficulty * 3.0
```

**修改后**：
```gdscript
var speed := 0.5 * sqrt(difficulty)
var spawn_rate := 60.0 / sqrt(difficulty)
```

**效果**：减速增长曲线，仍然会变难但会自然趋于平缓。

### 模式 1.2：乘法难度

**问题**：游戏在所有难度级别感觉都一样。

**诊断**：`exploratory_ratio` 在所有阶段都接近 1.0。

**修改前**：
```gdscript
player.position += player.velocity
blade_angle += rotate_speed
```

**修改后**：
```gdscript
player.position += player.velocity * sqrt(difficulty)
blade_angle += rotate_speed * sqrt(difficulty)
```

**效果**：所有参数同步缩放，在增加挑战的同时保持一致的手感。

### 模式 1.3：生成间隔的反向难度

**问题**：生成速率加速不够。

**诊断**：`telemetry.spawn_analysis.average_interval` 在游戏后期过高。

**修改前**：
```gdscript
spawn_timer = 60.0 - difficulty * 3.0  # 在 difficulty 20 时封顶
```

**修改后**：
```gdscript
spawn_timer = 60.0 / difficulty  # 持续递减
```

---

## 2. 得分系统模式

### 模式 2.1：基于风险的得分

**问题**：得分不反映技巧或冒险行为。

**诊断**：`telemetry.scoring_analysis.triggers` 只显示一种得分方式。

**修改前**：
```gdscript
add_score(10)  # 固定分数
```

**修改后**：
```gdscript
add_score(obstacles.size())    # 风险越大 = 奖励越高
add_score(ceili(player.size))  # 目标越大 = 分数越高
add_score(multiplier)          # 连续成功获得奖励
```

**使用此模式的游戏**：cling-hop, phaserun, geyser-hop

### 模式 2.2：得分规模缩减

**问题**：分数膨胀过快，数字失去意义。

**诊断**：最终分数达到数百万，难以比较不同回合。

**修改前**：
```gdscript
# 每次动作的分数
var points := {&"large": 10, &"medium": 20, &"small": 30}
```

**修改后**：
```gdscript
# 每次动作的分数
var points := {&"large": 1, &"medium": 2, &"small": 3}
```

**使用此模式的游戏**：splitzig

### 模式 2.3：指数连击得分

**问题**：多杀不够有回报感。

**诊断**：`telemetry.scoring_analysis.scoring_rate` 无论连击与否都很平坦。

**修改前**：
```gdscript
add_score(destroyed_count * base_points)
```

**修改后**：
```gdscript
add_score(destroyed_count * destroyed_count)
```

**使用此模式的游戏**：star-eater

### 模式 2.4：连击倍率系统

**问题**：没有连续成功的激励。

**诊断**：`telemetry.input_analysis.pattern` 显示没有节奏感。

**实现**：
```gdscript
var multiplier := 1

# 成功时
multiplier = mini(multiplier + 1, max_multiplier)
add_score(base_points * multiplier)

# 失败/未命中时
multiplier = maxi(multiplier - 1, 1)
```

**使用此模式的游戏**：geyser-hop, geoerase, inkinh

---

## 3. 边界行为模式

### 模式 3.1：游戏结束改为屏幕穿越

**问题**：死亡集中在屏幕边缘。

**诊断**：`telemetry.death_analysis.position` 集中在边界附近。

**修改前**：
```gdscript
if player.position.x < 5.0 or player.position.x > 95.0:
    end_game()
```

**修改后**：
```gdscript
player.position.x = wrapf(player.position.x, 0.0, 100.0)
```

**使用此模式的游戏**：splitzig

### 模式 3.2：移动边界

**问题**：游戏玩起来静止不动，没有位置挑战。

**诊断**：`telemetry.input_analysis` 显示仅有时序模式。

**修改前**：
```gdscript
var gate_pos := Vector2(50.0, 92.0)  # 固定位置
```

**修改后**：
```gdscript
var gate_pos := Vector2(50.0, 92.0)
var gate_vx := 1.0
# 在 _process 中：
gate_pos.x += gate_vx * sqrt(difficulty)
if gate_pos.x > 90.0 or gate_pos.x < 10.0:
    gate_vx *= -1.0
```

**使用此模式的游戏**：dark_sort

### 模式 3.3：弹回替代死亡

**问题**：墙壁碰撞结束游戏太突然。

**修改前**：
```gdscript
if player.position.x > 90.0:
    end_game()
```

**修改后**：
```gdscript
if player.position.x > 90.0:
    player.position.x = 90.0
    player_vx *= -1.0
```

**使用此模式的游戏**：stompshelter

---

## 4. 自我平衡机制

### 模式 4.1：资源衰减

**问题**：累积优势使游戏变得无聊。

**诊断**：探索性测试通过累积资源轻松获得高分。

**修改前**：
```gdscript
stack_height += points  # 只增不减
```

**修改后**：
```gdscript
stack_height += points
stack_height *= 0.998  # 持续衰减
```

**使用此模式的游戏**：splitzig

### 模式 4.2：成功时冷却缩减

**问题**：好的操作应该获得更多行动机会的奖励。

**实现**：
```gdscript
var base_cooldown := 40.0
# 连击成功时
cooldown = floor(base_cooldown / (1.0 + combo_count * 0.5))
cooldown = maxf(cooldown, min_cooldown)
```

**使用此模式的游戏**：wipe-blade

### 模式 4.3：错失机会的惩罚

**问题**：被动游玩没有后果。

**约束**：惩罚必须绑定到游戏世界中错过的事件，而非"没有按下按钮"。

**诊断**：`telemetry.input_analysis.pattern` 显示"no_input"有效。

**实现**：
```gdscript
# 当间歇泉未被踩踏就离开屏幕时
if not g.stomped and g.position.x < -15.0:
    multiplier = maxi(multiplier - 1, 1)
```

**使用此模式的游戏**：geyser-hop

---

## 5. 输入响应模式

### 模式 5.1：状态相关速度

**问题**：没有通过输入时序表达的技巧。

**诊断**：`telemetry.input_analysis` 显示长按或狂按是最优的。

**修改前**：
```gdscript
laser_angle += laser_speed  # 恒定速度
```

**修改后**：
```gdscript
var speed_mul := 1.0 if is_pressing else 2.0
laser_angle += laser_speed * speed_mul * sqrt(difficulty)
# 不按下时旋转更快，奖励时机把握
```

**使用此模式的游戏**：geoerase, inkinh

### 模式 5.2：长按增长机制

**问题**：长按和点按之间没有风险/收益差异。

**实现**：
```gdscript
if is_pressing:
    player.target_size += growth_rate  # 长按时增长
# 根据大小计分
add_score(ceili(player.size))  # 越大 = 分数越高但也更脆弱
```

**使用此模式的游戏**：phaserun

### 模式 5.3：长按加速危险

**问题**：长按没有 downside。

**约束**：如果此模式会造成不可避免的伤害/死亡循环或移除有意义的恢复选项，则该模式无效。

**实现**：
```gdscript
# 墙壁施压速度取决于输入
var press_rate := 0.2 if is_pressing else 0.05
wall_press += press_rate * sqrt(difficulty)
```

**使用此模式的游戏**：pressbound

---

## 6. 生成模式

### 模式 6.1：安全距离检查

**问题**：生成时出现不公平的即死。

**诊断**：`telemetry.death_analysis.recent_frames` 显示在生成后立即死亡。

**修改前**：
```gdscript
asteroids.append({"pos": Vector2(randf() * 100.0, 0.0)})
```

**修改后**：
```gdscript
var pos := Vector2(randf() * 100.0, 0.0)
if pos.distance_to(player.position) > safe_distance:
    asteroids.append({"pos": pos})
```

**使用此模式的游戏**：star-eater, inkinh

### 模式 6.2：倒计时 vs 帧数生成

**问题**：生成时序过于可预测或过于随机。

**修改前**：
```gdscript
if tick % 60 == 0:
    spawn_enemy()  # 可预测
```

**修改后**：
```gdscript
next_spawn_ticks -= 1
if next_spawn_ticks <= 0:
    spawn_enemy()
    next_spawn_ticks = int(randf_range(base_interval * 0.8, base_interval * 1.2) / sqrt(difficulty))
```

**使用此模式的游戏**：star-eater, phaserun, geyser-hop

### 模式 6.3：自适应生成位置

**问题**：玩家可以在安全点蹲守。

**诊断**：`telemetry.death_analysis.position` 显示玩家停留在某个区域。

**修改前**：
```gdscript
var from_left := randf() < 0.5  # 随机方向
```

**修改后**：
```gdscript
var from_left := player.position.x > 50.0  # 从对面生成
```

**使用此模式的游戏**：cling-hop

### 模式 6.4：基于距离的敌人生成

**问题**：敌人生成与玩家进度无关。

**修改前**：
```gdscript
if tick % 100 == 0:
    spawn_enemy()
```

**修改后**：
```gdscript
next_enemy_dist -= scroll_amount  # 与玩家进度绑定
if next_enemy_dist < 0.0:
    spawn_enemy()
    next_enemy_dist = randf_range(100.0, 200.0) / sqrt(difficulty)
```

**使用此模式的游戏**：stompshelter

---

## 7. 机制添加模式

### 模式 7.1：攻击/防御切换

**问题**：玩家纯粹被动，只能躲避。

**诊断**：`telemetry.input_analysis.pattern` 显示"no_input"或仅有闪避。

**实现**：添加在特定状态下摧毁障碍物的能力。

```gdscript
# 玩家在空中（黄色）时可以摧毁障碍物
# 攀附时（青色）处于无敌状态
var color := Color.CYAN if cling_target != null else Color.YELLOW
# ... 后续在障碍物碰撞中：
if is_clinging:
    end_game()
else:
    # 摧毁障碍物
    play_sfx("power_up")
    spawn_particles(obs.position, 20, 3.0)
    obs.queue_free()
```

**使用此模式的游戏**：cling-hop

### 模式 7.2：添加移动控制

**问题**：玩家移动完全自动。

**实现**：
```gdscript
# 原版：固定水平位置
player.position.x += (50.0 - player.position.x) * 0.01

# 修改版：添加玩家控制
var move_mul := 1.0 if is_pressing else 0.1
player.position.x += player_vx * move_mul
if player.position.x > 90.0 or player.position.x < 10.0:
    player_vx *= -1.0
```

**使用此模式的游戏**：stompshelter

## 8. 时序与节奏模式

### 模式 8.1：基于窗口的得分

**问题**：得分不反映时序精确度。

**诊断**：`telemetry.scoring_analysis.triggers` 显示无论时序如何都是固定分数。

**实现**：
```gdscript
var window_center := target_beat_time
var delta_t := absf(input_time - window_center)

if delta_t < perfect_window:
    add_score(base_points * 3)  # Perfect
elif delta_t < good_window:
    add_score(base_points * 1)  # Good
else:
    multiplier = 1  # Miss 重置连击
```

### 模式 8.2：速度递增

**问题**：节奏游戏在不同难度级别感觉都一样。

**实现**：
```gdscript
var bpm := base_bpm + difficulty * 8.0
var beat_interval := 60.0 / bpm
# 在更高难度引入切分音
if difficulty > 3:
    beat_interval *= (1.0 if beat_index % 4 != 3 else 0.75)
```

---

## 9. 状态管理模式

### 模式 9.1：状态衰减压力

**问题**：玩家可以无限期维持安全状态。

**诊断**：`hold_action` 得分等于或超过探索性得分。

**实现**：
```gdscript
# 维持当前状态有递增的成本
state_stability -= delta * (1.0 + state_duration * 0.3)
if state_stability <= 0.0:
    force_state_transition()
```

### 模式 9.2：多资源张力

**问题**：单一资源使最优操作显而易见。

**实现**：
```gdscript
# 两个资源呈反比关系
func consume_action():
    energy -= action_cost
    heat += action_heat
    if heat > overheat_threshold:
        enter_cooldown_state()  # 暂时锁定
    # 得分随过热风险缩放
    add_score(base_points * (1.0 + heat / overheat_threshold))
```

### 模式 9.3：切换状态权衡

**问题**：状态切换（reverse_state）没有有意义的代价。

**实现**：
```gdscript
# 每个状态各有优势和弱点
match current_state:
    State.ALPHA:
        can_collect_alpha_items = true
        vulnerable_to_beta_hazards = true
    State.BETA:
        can_collect_beta_items = true
        vulnerable_to_alpha_hazards = true
# 切换时有短暂的脆弱窗口
if just_switched:
    vulnerable_to_all = true
    switch_cooldown = 0.3
```

---

## 10. 空间与领地模式

### 模式 10.1：覆盖得分

**问题**：没有空间探索的激励。

**诊断**：玩家停留在某个区域。

**实现**：
```gdscript
var visited_cells: Dictionary = {}
const CELL_SIZE := 40.0

func _on_player_moved(pos: Vector2) -> void:
    var cell_key := Vector2i(int(pos.x / CELL_SIZE), int(pos.y / CELL_SIZE))
    if not visited_cells.has(cell_key):
        visited_cells[cell_key] = true
        add_score(coverage_bonus)
```

### 模式 10.2：领地压力

**问题**：涂色/占领的领地是永久的，没有张力。

**实现**：
```gdscript
# 领地随时间衰减，需要重新参与
for cell_key in owned_territory.keys():
    owned_territory[cell_key] -= decay_rate * delta
    if owned_territory[cell_key] <= 0.0:
        owned_territory.erase(cell_key)
# 根据当前持有的领地计分，而非曾经占领过的
add_score(owned_territory.size() * hold_bonus * delta)
```

---

## 11. 建造与解谜模式

### 模式 11.1：放置质量得分

**问题**：任何放置得分都相同。

**实现**：
```gdscript
func score_placement(piece_pos: Vector2, existing_pieces: Array) -> int:
    var adjacency_bonus := 0
    var alignment_bonus := 0
    for p in existing_pieces:
        if p.pos.distance_to(piece_pos) < snap_distance:
            adjacency_bonus += 1
        if is_aligned(p, piece_pos):
            alignment_bonus += 2
    return base_points + adjacency_bonus * 3 + alignment_bonus * 5
```

### 模式 11.2：带有宽限的时间压力

**问题**：建造没有紧迫感。

**实现**：
```gdscript
# 截止时间逼近，但好的操作可以延长时间
var time_remaining := base_time
func on_successful_build():
    time_remaining += time_extension  # 奖励延长截止时间
func _process(delta):
    time_remaining -= delta * (1.0 + difficulty * 0.15)
    if time_remaining <= 0.0:
        end_round()
```

---

## 快速参考：问题 → 模式

| 问题 | 模式 |
|:--------|:--------|
| 屏幕边缘死亡 | 3.1 屏幕穿越 或 3.3 弹回 |
| 高难度死亡 | 1.1 sqrt() 转换 |
| 没有技巧表达 | 5.1 状态相关速度 |
| 狂按是最优 | 4.3 错失惩罚, 5.3 长按危险 |
| 长按是最优 | 5.1 状态速度, 2.1 风险得分 |
| 不操作是最优 | 4.3 错失惩罚, 7.2 移动控制 |
| 生成时即死 | 6.1 安全距离 |
| 分数膨胀 | 2.2 得分缩减 |
| 没有连击激励 | 2.4 倍率系统 |
| 静止的游戏玩法 | 3.2 移动边界, 6.3 自适应生成 |
| 时序不重要 | 8.1 窗口得分 |
| 节奏感觉静态 | 8.2 速度递增 |
| 安全状态是永久的 | 9.1 状态衰减, 9.3 切换权衡 |
| 单一资源使玩法无聊 | 9.2 多资源张力 |
| 没有空间探索激励 | 10.1 覆盖得分 |
| 领地没有张力 | 10.2 领地压力 |
| 所有放置等同 | 11.1 放置质量 |
| 建造没有紧迫感 | 11.2 带宽限的时间压力 |

---

## 实现清单

应用平衡模式时：

1. **先运行可复现的平衡测试**以识别问题
2. **查阅上方的问题 → 模式表**
3. **每次只应用一个模式**
4. **重新运行 headless 测试**以验证改进
5. **进行 2 分钟的人工游玩合理性检查**
6. **如果 `exploratory_ratio` 仍 ≤ 1.5**，仅在合理性检查通过后应用更多模式

### 遥测分析关注领域

```text
// 来自 logs/test.json → telemetry:

// 1. 死亡分析
telemetry.death_analysis.position       // 死亡发生的位置
telemetry.death_analysis.recent_frames  // 死亡前发生了什么

// 2. 输入分析
telemetry.input_analysis.pattern        // "spam", "hold_heavy", "no_input", "varied"
telemetry.input_analysis.total_presses  // 一轮中有多少次输入

// 3. 得分分析
telemetry.scoring_analysis.triggers     // 什么触发了得分
telemetry.scoring_analysis.scoring_rate // 得分随时间的分布

// 4. 生成分析
telemetry.spawn_analysis.spatial_distribution // 生成位置
telemetry.spawn_analysis.average_interval     // 生成频率
```

---

## 示例：完整的平衡调整流程

假设某游戏的 `exploratory_ratio` = 0.8：

1. **检查输入模式**："spam" → 应用模式 5.1（状态相关速度）
2. **重新测试**：`exploratory_ratio` = 1.1
3. **检查死亡位置**：集中在边缘 → 应用模式 3.1（屏幕穿越）
4. **重新测试**：`exploratory_ratio` = 1.3
5. **检查得分**：单一来源 → 应用模式 2.4（连击倍率）
6. **重新测试**：`exploratory_ratio` = 1.8 ✓

这种系统化的方法通过迭代模式应用，在保持游戏体验的同时帮助改善平衡性。
