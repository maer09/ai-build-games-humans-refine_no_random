# 模拟测试框架设计

当项目尚未产出 `log-contract.md` 所要求的平衡遥测数据时使用此参考文档。

测试框架应使游戏运行可对比。它不需要是渲染器、物理引擎或 UI 的完整副本；它需要一个确定性前向模型，能在多种输入策略下运行相同的游戏规则，并在每次运行中发射相同类别的事件。

## 1. 必需组件

在进行平衡分析之前，先构建或找到以下组件。

- **游戏适配器**：游戏循环的薄封装，暴露 `init(seed)`、`step(input, dt)`、`get_score()`、`is_game_over()` 以及可选的 `get_state_snapshot()`。
- **确定性随机源**：所有生成、危险、奖励和 AI 的随机性必须使用由测试框架控制的有种子生成器。
- **公开输入模式**：玩家实际可用的按键、摇杆、触控区域或动作状态，包括范围、中间值、时机语义和相关时的同时输入约束。
- **可见状态模式**：策略可以读取的世界事实，限制在玩家能从屏幕推断的信息范围内，除非运行明确标记为预言机上限。
- **策略可见性映射**：每个策略可以读取的可见状态特征。
- **输入策略**：至少包含闲置/无输入和简单重复动作策略；当操控方案不同时，添加游戏特定的单调策略。
- **探索策略运行器**：随机搜索、启发式搜索、回放搜索或遗传搜索，在固定种子下尝试多种输入序列。
- **事件记录器**：在每次模拟运行中记录死亡、生成、得分和输入事件。
- **报告器**：写入符合 `log-contract.md` 的 JSON 对象；stdout 也可以接受，文件可写入项目常规的 `logs/`、`reports/`、`artifacts/` 或 `test-results/` 目录。

## 2. 适配器契约

保持适配器精简且引擎本地化。

```text
create_adapter(game, seed):
  reset game state
  install seeded RNG
  define public_input_schema
  define visible_state_schema
  return:
    step(input_frame) -> events
    score() -> number
    elapsed() -> seconds
    ended() -> bool
    snapshot() -> optional serializable state
```

对于有实时更新循环的引擎，使用固定帧步进而非挂钟时间。对于依赖渲染的游戏，将规则更新与绘制充分分离，使测试框架可以 headless 推进世界。

如果精确的引擎模拟成本过高，则实现被评估系统的最小忠实前向模型：玩家移动、危险物、奖励、得分、伤害、游戏结束和生成逻辑。

## 3. 输入策略集

策略应该是明确的、可复现的从帧/状态到输入的函数。

推荐基线策略：

- `no_input`：从不按下主操作键。
- `hold_action`：在整个运行期间长按主操作键。
- `spam_action`：以短固定节奏按下/释放。
- `periodic_action`：当时机重要时，以一个或多个较慢节奏按下。
- `random_action`：从有种子的分布中采样输入。
- `exploratory`：搜索输入序列或基于状态的选择，报告最佳运行。

单按键游戏通常需要按下、长按和释放时机。多输入游戏应为每个主导的简单策略定义等效的单调策略，例如始终向左、始终射击、始终加速或最短路径贪心。

不要硬编码了解玩家无法获取的隐藏内部信息的策略，除非目标明确是测试上限。优先使用玩家能从屏幕推断的状态特征。

当操控方案未知时，先写公开输入模式，再从中推导策略：

```text
input_schema:
  move_x: axis -1..1
  move_y: axis -1..1
  primary: boolean
  secondary: boolean
  simultaneous: move axes plus at most one action

monotonous_candidates:
  no_input
  fixed_direction(move_x=1)
  hold_primary
  spam_primary(period=8 ticks)
  greedy_nearest_reward using visible positions
```

对每个策略，记录其可见性：

```text
policy_visibility:
  no_input: []
  fixed_direction: []
  hold_primary: []
  greedy_nearest_reward: [player_position, reward_positions]
  exploratory: [player_position, hazard_positions, reward_positions]
```

## 4. 探索运行器

探索运行器的目的是检测技巧性或多样化的游玩是否能胜过单调策略。

可接受的方法：

- 在多种种子上进行随机输入序列搜索。
- 使用可见状态的启发式方法，如到危险物的距离、奖励位置或资源水平。
- 对输入时机或紧凑动作基因组进行遗传搜索。
- 回放变异：变异之前最佳序列并保留改进。

报告最佳得分、经过时间、种子和变体。改进前后保持相同的搜索预算，使对比有意义。

在报告中记录探索运行器的预算：种子数、变体数、代数、随机样本数、回放变异数、最大帧数和可见状态特征。如果此预算在游戏修复后发生变化，在对比前用新预算重跑基线。

## 5. 遥测事件

先记录原始事件，再聚合为 `log-contract.md` 的格式。

推荐的原始事件格式：

```json
{"tick": 120, "type": "input", "pressed": true, "held": false}
{"tick": 184, "type": "spawn", "kind": "hazard", "x": 92, "y": 38}
{"tick": 240, "type": "score", "amount": 2, "reason": "near_miss", "x": 41, "y": 62}
{"tick": 301, "type": "death", "cause": "collision", "object": "hazard", "x": 47, "y": 65}
```

至少聚合以下内容：

- 死亡聚集、原因、位置分布，以及输入后不久的死亡。
- 生成间隔、位置分布、类型分布，以及与玩家的最小距离（当可用时）。
- 得分触发、分值、得分时机，以及得分是否与原始输入次数相关。
- 输入模式摘要，如长按时长、按下间隔分布和主导的简单模式。

## 6. 输出与发现

此 skill 不要求统一的文件路径。优先使用项目现有的约定。

合理的输出目标：

- stdout JSON，用于 CLI 工具和 CI。
- `logs/balance/*.json`
- `reports/balance/*.json`
- `artifacts/balance/*.json`
- `test-results/balance/*.json`

如果向项目添加新的测试框架，在框架附近记录生成报告的命令和预期输出路径。评估者应能在游戏变更后重新运行相同的命令。

## 7. 不完整的报告

得分、经过时间和 `exploratory_ratio` 是有用的摘要信号，但不足以诊断平衡问题。

如果四个遥测视角中任一缺失：

1. 将报告标记为不足以进行根本原因平衡判断。
2. 保留现有摘要指标作为基线信号。
3. 为缺失的视角添加原始事件记录或聚合。
4. 使用确定性种子重新运行相同的单调和探索策略。
5. 然后才提出结构性游戏修复。

## 8. 失败模式

在以下情况下拒绝或修改测试框架：

- 渲染器和模拟器使用不同的游戏常量。
- 随机性未设置种子。
- 单调和探索运行使用不同的游戏设置。
- 探索运行器获取了玩家无法感知的隐藏信息。
- 公开输入模式或可见状态模式未记录。
- 记录器从输入事实而非游戏内因果事件中给出得分。
- 报告仅包含摘要得分和经过时间，没有死亡/生成/得分/输入的细分。
- 改进前后对比使用了不同的种子、预算、策略或最大帧数且未说明原因。
