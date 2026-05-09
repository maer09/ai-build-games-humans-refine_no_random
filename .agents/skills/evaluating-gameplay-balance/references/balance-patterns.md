# 平衡模式目录

本目录与引擎无关。使用这些模式来决定要做哪种规则或系统层面的变更，然后将实现细节转化到项目的引擎和架构中。

## 1. 难度缩放

### 1.1 递减难度增长

当线性增长导致后期游玩不可读或产生不可避免的失败时使用。

模式：

```text
effective_difficulty = sqrt(raw_difficulty)
speed = base_speed * effective_difficulty
spawn_interval = base_interval / effective_difficulty
```

### 1.2 乘法难度分层

当难度应该温和地影响多个系统，而非严厉地影响单一系统时使用。

模式：

```text
movement_pressure = base_movement * layer_a(raw_difficulty)
spawn_pressure = base_spawn * layer_b(raw_difficulty)
reward_pressure = base_reward * layer_c(raw_difficulty)
```

### 1.3 生成间隔下限

当生成速度超过人类反应时间时使用。

模式：

```text
spawn_interval = max(min_reactable_interval, scaled_interval)
```

## 2. 得分

### 2.1 风险驱动得分

奖励需要暴露在危险中、精确时机或受限移动才能完成的事件。

模式：

```text
score = base_event_score + risk_bonus(distance_to_danger, timing_precision, route_cost)
```

### 2.2 得分范围缩减

当巨大数值掩盖平衡问题时，使用较小的分值范围。

模式：

```text
common_success = 1
risky_success = 2 or 3
rare_mastery = 5
```

### 2.3 带重置原因的连击

仅当失败原因可见且可恢复时才使用连击。

模式：

```text
on_success: combo += 1
on_visible_miss_or_damage: combo = 0
score += base_score * combo_multiplier(combo)
```

## 3. 边界与失败

### 3.1 用世界后果替代即死

当边界接触惩罚过重或不够清晰时使用。

模式：

```text
on_boundary_contact:
  push_player_back
  reduce_resource_or_combo
  show_world_feedback
```

### 3.2 移动边界

当安全游玩过于静态时使用。

模式：

```text
safe_region changes position or shape over time
player must reposition before scoring remains possible
```

## 4. 输入响应

### 4.1 输入状态权衡

当长按、狂按或闲置占主导时使用。

模式：

```text
holding: improves one capability, worsens exposure
tapping: creates short opportunity, adds recovery
idle: may be safe briefly, but world state advances
```

### 4.2 上下文输入语义

当同一输入需要在不同阶段中做出判断时使用。

模式：

```text
if phase_a: input changes position
if phase_b: input changes state or timing
both outcomes are visible in the world
```

## 5. 生成与空间公平

### 5.1 安全距离

当危险物生成位置离玩家太近时使用。

模式：

```text
candidate_spawn is accepted only if distance_to_player >= minimum_clearance
fallback: skip or delay spawn rather than force an unfair spawn
```

### 5.2 区域冷却

当某个屏幕区域承受反复压力时使用。

模式：

```text
divide space into cells
track last_spawn_time per cell
exclude cells whose cooldown has not expired
```

### 5.3 自适应对面生成

当生成侧应响应玩家位置时使用。

模式：

```text
spawn from the side that creates travel/readability pressure without instant collision
```

## 6. 状态与领地

### 6.1 状态衰减

当累积优势使游玩变得轻而易举时使用。

模式：

```text
valuable_state decays unless refreshed through risky or skillful events
```

### 6.2 多资源张力

当单一资源解释力过强时使用。

模式：

```text
resource_a supports safety
resource_b supports score
actions shift value between them
```

### 6.3 空间历史化

当之前的行为应影响后续选择时使用。

模式：

```text
player action leaves a world trace
trace changes later movement, scoring, spawn, or hazard behavior
```

## 7. 构建与解谜

### 7.1 放置质量得分

当放置应奖励结构而非原始放置数量时使用。

模式：

```text
score placement by adjacency, alignment, coverage, route creation, or constraint satisfaction
```

### 7.2 带宽限的时间压力

当计时器制造压力但不应该武断地结束游玩时使用。

模式：

```text
deadline approaches
successful play extends or softens the deadline through visible world events
```

## 快速问题对照表

| 问题 | 候选模式 |
| :--- | :--- |
| 单调输入获胜 | 2.1, 4.1, 4.2, 6.1 |
| 死亡感觉不公平 | 3.1, 5.1, 5.2 |
| 难度感觉平淡 | 1.1, 1.2, 3.2 |
| 某个区域被过度使用 | 5.2, 5.3, 6.3 |
| 得分缺乏技巧信号 | 2.1, 2.3, 7.1 |

## 应用检查清单

- 在应用模式之前，先识别根本原因。
- 优先每次只做一处结构性变更。
- 使用相同的单调和探索策略重新测试。
- 拒绝使游戏可读性降低、公平性降低或满足感降低的 KPI 提升。
