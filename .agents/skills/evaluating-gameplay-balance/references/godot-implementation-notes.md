# Godot 实现笔记

在引擎无关的平衡分析确定要应用的结构性模式之后，使用此参考文档将其转化为 Godot/GDScript 项目中的实现。先用遥测术语做出诊断，再将选定的模式转化为项目中的实际脚本。

## 护栏

- 项目 `AGENTS.md` 是命令、文件布局和验证的权威信息源。
- 用简短的人工游玩以及日志或模拟器得分来验证平衡变更。
- 优先结构性修复而非纯数值调整：先改变风险、反馈、时机窗口、生成规则或世界后果，再考虑仅修改常量。
- 保持公式在游戏开始时可读且稳定。如果 `difficulty` 从 `1` 开始，`sqrt(difficulty)` 能保留基础值。

## 难度缩放

当死亡集中在后期或危险物变得不可读时，使用递减增长。

```gdscript
var effective_difficulty := sqrt(difficulty)
var speed := base_speed * effective_difficulty
var spawn_interval := base_interval / effective_difficulty
```

当生成频率可能低于人类反应时间时，使用下限。

```gdscript
spawn_interval = max(min_reactable_interval, base_interval / sqrt(difficulty))
```

当单个严苛缩放的数值主导游玩时，将难度分配到多个温和的层。

```gdscript
player.position += player.velocity * sqrt(difficulty)
hazard_angle += rotate_speed * sqrt(difficulty)
```

## 得分

奖励可见的风险或精度，而非原始输入次数。

```gdscript
add_score(close_call_bonus)
add_score(active_hazards.size())
add_score(combo_multiplier)
```

当大数值掩盖某个动作是否过度奖励时，使用小分值范围。

```gdscript
var points := {&"safe": 1, &"risky": 2, &"mastery": 5}
```

连击需要可见的重置原因。

```gdscript
multiplier = mini(multiplier + 1, max_multiplier)
add_score(base_points * multiplier)

# On visible miss, damage, or broken rhythm:
multiplier = 1
```

## 边界与失败

当边界死亡在遥测中占主导时，考虑使用可见的世界后果代替即死。

```gdscript
if player.position.x < 0.0 or player.position.x > screen_size.x:
    player.position.x = wrapf(player.position.x, 0.0, screen_size.x)
    multiplier = 1
    show_boundary_feedback()
```

当闲置或静止游玩过强时，使用移动的得分区域或安全区。

```gdscript
gate_pos.x += gate_vx * sqrt(difficulty)
if gate_pos.x > 90.0 or gate_pos.x < 10.0:
    gate_vx *= -1.0
```

## 输入响应

对于单按键或简单输入的游戏，每种输入模式应在改善一个结果的同时恶化另一个。

```gdscript
if Input.is_action_pressed("action"):
    player.scale += Vector2.ONE * grow_rate * delta
    danger_radius += danger_growth * delta
else:
    player.scale = player.scale.move_toward(Vector2.ONE, shrink_rate * delta)
```

避免使长按、狂按或闲置成为全局最优。检查遥测中的长按连续段、重复点击和无输入存活。

## 生成公平

拒绝离玩家太近的生成。跳过或延迟生成通常比强制放置不公平的危险物更好。

```gdscript
func can_spawn(pos: Vector2) -> bool:
    return pos.distance_to(player.position) >= minimum_clearance
```

当某个屏幕区域承受反复压力时，使用区域冷却。

```gdscript
var cell := world_to_cell(candidate_pos)
if time - last_spawn_time_by_cell.get(cell, -INF) >= cell_cooldown:
    spawn_at(candidate_pos)
    last_spawn_time_by_cell[cell] = time
```

## 状态与领地

当累积优势使游玩变得轻而易举时，使用衰减。

```gdscript
resource = max(resource - decay_rate * delta, 0.0)
```

当过去的玩家行为应影响后续选择时，使用世界痕迹。

```gdscript
trail_cells[cell] = trail_lifetime
# Later: trails alter scoring, movement cost, or spawn eligibility.
```

## 验证检查清单

- 模拟器重运行使用与基线相同的种子、策略、帧率和聚合逻辑。
- 遥测能解释变化后的结果，而非仅显示最终得分。
- 人工游玩仍有可读的危险、公平的失败和可见的选择风险的理由。
- 没有添加仅为了帮助或损害测试策略的隐藏规则。
