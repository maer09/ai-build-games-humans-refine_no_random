# AGENTS.md — Godot 小游戏手工设计生成（非随机版）

AI 智能体基于人类指定的标签设计、实现和改进 Godot 4.2+ 小游戏的入口文件。
本版本移除了随机标签选择流程，所有标签由人类直接指定。

## 运行原则（唯一信息源）

- 执行步骤、约束条件和评估标准的唯一信息源就是本 `AGENTS.md` 文件。
- **`.agents/rules/RULES.md`** 包含所有 GDScript 代码必须遵守的编码规范（格式、命名、代码顺序、静态类型），在编写和审查代码时始终生效。
- Skill 参考文档仅作为原则和模式的指南；不要在其中重复程序性定义。
- 当流程发生变更时，更新本文档，并保持引用的指南聚焦于原则和实现模式。

## 体验优先原则（KPI 护栏）

- KPI（如探索比率）是**游戏品质的检测器**，而非优化目标。
- 降低玩家体验的变更必须被拒绝，即使 KPI 数值有所改善。
- 得分必须仅与游戏内事件的因果关系绑定。禁止对原始输入事实直接计分。
- 游戏结束条件必须与游戏世界内的危险/状态崩溃绑定。不要直接惩罚"不行动"本身。
- 禁止针对测试智能体的特殊分支（仅在测试中有利/不利的行为）。

## 指令：当被告知"做一个游戏"时

按顺序执行阶段 1 至 8。
阶段 7 仅生成评估报告（不做实现变更）。实现变更仅允许在阶段 8 根据人类反馈进行。
以下每个阶段列出了所需的文件和命令。

如果根据人类指令修改了游戏，必须完成 Web 导出流程。

---

## 阶段 1：创意输入与标签指定

**本版本与随机版的区别**：不使用 `random_tag_selector.js` 脚本随机选择标签，而是由人类直接提供创意输入。

### 输入模式

人类可以通过以下三种模式之一（或组合）启动游戏设计：

| 模式 | 输入内容 | 标签来源 |
| :--- | :--- | :--- |
| **纯标签** | 直接指定标签组合 | 人类指定 |
| **游戏策划案** | 提供结构化的游戏设计文档 | AI 从策划案推导，人类确认 |
| **游戏点子** | 提供核心概念描述 | AI 从概念推导，人类确认 |

**优先级规则**：当人类同时提供了策划案/点子和标签时，以策划案/点子为主创意源；标签从中推导并补充，冲突时以策划案/点子表达的意图为准。

### 创意输入规格

#### 游戏策划案模式

策划案需包含以下结构化字段（不够结构化时，AI 应提示人类补充缺失字段）：

```markdown
## 游戏策划案

### 核心概念
<!-- 一句话描述游戏的核心体验 -->

### 核心循环
<!-- 玩家在游戏中反复做什么？每轮的输入→反馈→判断流程 -->

### 胜利/失败条件
<!-- 什么条件下游戏结束？赢/输的判定是什么？ -->

### 玩家操作
<!-- 玩家能做什么操作？预期使用多少个按键？ -->

### 视觉风格意向（可选）
<!-- 期望的画面感觉，如"霓虹城市"、"水墨风"、"低多边形"等 -->

### 参考游戏（可选）
<!-- 有哪些现有游戏与本概念类似？ -->
```

#### 游戏点子模式

点子是对游戏概念的简要描述，形式自由但必须传达足够的创意方向。AI 接收到点子后，应将其扩展为上述策划案结构，并向人类确认补充内容。

点子的最低要求：
- 必须包含**核心概念**（一句话描述体验）
- 必须包含**玩家做什么**（至少描述一个核心动作）
- 缺失字段由 AI 基于创意方向提出补充建议，人类确认后填入

### 标签推导

当使用策划案或点子模式时，AI 从创意内容中推导匹配的标签组合：

1. **分析核心循环和玩家操作** → 匹配 3 个机制标签（从 `data/tags/mechanism_tags.csv`）
2. **分析视觉风格意向和氛围** → 匹配 2 个视觉标签（从 `data/tags/visual_tags.csv`）
3. **分析整体结构和节奏** → 匹配 1 个结构标签（从 `data/tags/structure_tags.csv`）
4. **分析操作复杂度** → 推导 `button_types`（1-5）

推导结果必须展示给人类确认。人类可以调整推导出的标签。

### 标签规格（所有模式的统一输出）

无论使用哪种输入模式，阶段 1 的最终输出必须包含以下标准化的标签规格：

- **3 个机制标签**：从 `data/tags/mechanism_tags.csv` 中选取
- **2 个视觉标签**：从 `data/tags/visual_tags.csv` 中选取
- **1 个结构标签**：从 `data/tags/structure_tags.csv` 中选取
- **`button_types`**：1-5 的整数，定义按键类型数量

### 标签选取建议

- 机制标签之间应有足够的张力或对比，避免过于顺理成章的组合。
- 视觉标签应与机制标签形成有趣的整合点，而非简单装饰。
- 结构标签决定了游戏的整体骨架，应与机制标签协同。
- `button_types` 影响操控复杂度：1 = 极简（单按钮），5 = 复杂操作。

### 输入格式

以如下格式在 `docs/README.md` 中记录：

```markdown
## 创意输入

### 输入模式
<!-- 纯标签 / 游戏策划案 / 游戏点子 -->

### 原始输入
<!-- 人类提供的原始策划案或点子内容（纯标签模式可省略） -->

### 标签指定

#### 机制标签（3）
- tag1
- tag2
- tag3

#### 视觉标签（2）
- vtag1
- vtag2

#### 结构标签（1）
- stag1

#### 按键类型
button_types: <1-5>

### 标签推导说明（仅策划案/点子模式）
<!-- 简述如何从创意内容推导出上述标签，以及人类确认或调整了什么 -->
```

**如何对待标签和策划案**：标签是创意种子，策划案是创意蓝图。两者都是设计起点而非严格规格。将矛盾的标签作为创意张力来使用。策划案中的细节可以在后续阶段偏离，但核心意图应被尊重。不要害怕偏离。

**最低验证**：

- [ ] 已确定输入模式（纯标签 / 游戏策划案 / 游戏点子）
- [ ] 如果使用策划案或点子模式：策划案结构化字段已完整，或 AI 已提示人类补充
- [ ] 已从 `data/tags/structure_tags.csv` 中选择 1 个结构标签
- [ ] 已在 `docs/README.md` 中记录 `机制 3 + 视觉 2 + 结构 1`
- [ ] 已在 `README.md` 中记录 `button_types: <1-5>`
- [ ] 如果使用标签推导：推导结果已获人类确认

---

## 阶段 2：游戏设计

**Skill**：`designing-mini-games`
**参考**：`.agents/skills/designing-mini-games/references/mini-game-design-guide.md`

以机制标签为种子设计游戏规则。

1. 自由联想并有意偏离标签
2. 用一句话定义核心体验
3. 设计控制方式（在阶段 1 指定的 `button_types` 范围内）
4. 通过清单验证（`.agents/skills/designing-mini-games/references/mini-game-design-guide.md` §10）

**输出**：`docs/README.md`（核心机制、控制方式、对象规格、新颖性理由、标签记录、状态变量表、权衡说明）

**可见因果关系守则（必需）**：

- 状态变量不能"仅仅为了有个数字"而存在。在添加状态变量之前，必须明确说明现有规则无法表达的某个新决策。
- 每个状态变量必须至少有一个游戏世界内、非 HUD 的因果表现形式（地形/行为/颜色/形状/速度/声音）。
- 如果可以用现有状态表达，优先选择整合（状态精简）而非添加新状态。

---

## 阶段 3：视觉设计

**Skill**：`directing-game-visuals`
**参考**：`.agents/skills/directing-game-visuals/references/visual-design-guide.md`

以视觉标签为种子设计画面。

1. 将标签转化为视觉方向描述
2. 找出与机制的整合点
3. 确定由 3-5 种颜色组成的调色板
4. 设计与标签风格一致的反馈效果
5. 在 `docs/VISUAL_DESIGN.md` 中记录反 AI 通用化规则

- 视觉层级规则（1 个主角 / 1 个危险 / 1 个奖励）
- 模板化符号的上限限制
- 不依赖 UI 文字的反馈设计
- 构图规则（视线引导和中心区域避免拥挤）

6. 通过清单验证（`.agents/skills/directing-game-visuals/references/visual-design-guide.md` §10）

**输出**：`docs/VISUAL_DESIGN.md`（概念、调色板、渲染规格、效果设计）
使用 `.agents/skills/directing-game-visuals/references/visual-design-guide.md` §7.1（`VISUAL_DESIGN.md 必需附录模板`）来生成必需的附录文本。

## 阶段 4：声音设计

**Skill**：`creating-godot-procedural-audio`
**参考**：`.agents/skills/creating-godot-procedural-audio/references/sound-design-guide.md`

以视觉标签作为输入来定义 SFX 方向。不要单独选择声音标签。
所有 SFX 必须使用 Godot 的 `AudioStreamGenerator` 程序化生成；不使用外部音频文件。

1. 从视觉标签推导声音风格（`.agents/skills/creating-godot-procedural-audio/references/sound-design-guide.md` §3 映射表）
2. 用一句话定义声音概念
3. 选择波形调色板（1-2 种基础波形 + 调制方法）
4. 为每个游戏事件设计 SFX（`.agents/skills/creating-godot-procedural-audio/references/sound-design-guide.md` §4）
5. 定义动态参数（连击/速度/难度联动）
6. 对于持续音效，指定启动条件、停止条件和停止时的释放（允许混响尾音）
7. 通过清单验证（`.agents/skills/creating-godot-procedural-audio/references/sound-design-guide.md` §8）
8. 锁定 `得分 / 危险 / 伤害 / 状态变化` 的事件到音色映射，在单个游戏内保持一致
9. 每个游戏的音色设计要有所变化（波形、音高范围、包络、调制、节奏）

**输出**：`docs/SOUND_DESIGN.md`（概念、波形调色板、逐事件规格、动态参数）

---

## 阶段 5：Godot 实现

**Skills**：`scaffolding-godot-mini-games`、`running-headless-godot`（实现前加载）

基于阶段 2/3/4 的设计文档创建 Godot 项目。
初始化必须从模板开始。

```bash
PROJECT_DIR=.
mkdir -p "$PROJECT_DIR"
cp -R .agents/skills/scaffolding-godot-mini-games/assets/godot-base/. "$PROJECT_DIR"/
mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/build/web"
```

模板默认分辨率为 `960x540`。如需更改分辨率，需同时更新 `project.godot`、`web/custom_shell.html` 和 `export_presets.cfg`。

模板范围记录在 `.agents/skills/scaffolding-godot-mini-games/assets/godot-base/TEMPLATE_SCOPE.md` 中。

### 实现约束

- GDScript（Godot 4.2+）
- **必须使用静态类型**：所有变量、函数参数和返回值必须声明类型；代码必须无警告地通过 Godot 的编译（`strict` 模式）
- 仅使用 Godot 内置节点（不使用外部插件）
- 必须支持 `--headless` 运行
- 在字体正式采用之前，仅使用 `ThemeDB` 回退实现（不预捆绑字体）

### 实现策略（用于迭代改进）

- 按职责拆分为多个脚本，不要写成一个巨大的脚本。
- 保持 `main.gd` 仅作为编排器（更新顺序和依赖接线）。
- 职责划分示例：
  1. **游戏状态**（得分/进度/倍率/胜负）
  2. **玩家控制**（输入/移动/动作）
  3. **世界实体/环境**（非玩家动态/环境变化）
  4. **UI/HUD**（显示/通知/转场）
  5. **特效/音频**（视觉 FX/程序化声音）
- 在改进过程中，尽可能只编辑目标职责对应的脚本；尽量减少跨职责修改。

### 交付物结构

```text
./
├── project.godot
├── main.tscn
├── main.gd
├── README.md                     # 项目根索引，简要说明
├── docs/
│   ├── README.md                 # 游戏设计文档（核心机制、标签记录）
│   ├── VISUAL_DESIGN.md          # 视觉设计文档（概念、调色板、效果）
│   ├── TYPOGRAPHY_DECISION.md    # 排版决策文档
│   ├── SOUND_DESIGN.md           # 声音设计文档（概念、波形调色板、SFX规格）
│   └── THIRD_PARTY_LICENSES.md   # 第三方许可证汇总
├── assets/
│   └── fonts/                    # bundle only adopted fonts (minimal)
├── licenses/                     # original font license texts
├── tools/
│   └── tests/
│       └── run_tests.gd
├── logs/
│   ├── test.log
│   ├── test.json
│   └── improvement_report.md
└── scripts/                      # as needed
```

### 交付物可追溯性规则

不要将所有文档合并到一个文件中；使用 `docs/README.md` 作为主要设计文档索引。
`docs/README.md` 必须至少包含以下相对链接：

- `docs/VISUAL_DESIGN.md`
- `docs/TYPOGRAPHY_DECISION.md`
- `docs/SOUND_DESIGN.md`
- `docs/THIRD_PARTY_LICENSES.md`
- `logs/test.json`
- `logs/improvement_report.md`

### Godot Headless 规则

- **GODOT 的可执行文件路径在环境变量 GODOT_PATH 中，可以在 PowerShell 中通过 `$env:GODOT_PATH` 引用。**
- 始终使用 `--headless --path <PROJECT_DIR>`
- 使用 `mkdir -p logs && ... 2>&1 | tee logs/<name>.log` 捕获日志
- 不要直接以文本方式编辑 `.tscn`（使用 `--headless --script`）
- 在沙箱/CI/WSL 环境中，将 `XDG_DATA_HOME`、`XDG_CONFIG_HOME`、`XDG_CACHE_HOME` 设置为 `<PROJECT_DIR>` 下的绝对路径

### Web 导出分辨率和 Canvas 布局

- 将游戏内渲染分辨率（固定）与页面布局（居中放置）分离。
- 根据游戏选择渲染分辨率（例如：`960x540`；可根据项目需求更改）。
- 将 `project.godot` 中的 `window/size/viewport_width` 和 `window/size/viewport_height` 与选定的渲染分辨率匹配。
- 在 `export_presets.cfg` 中，默认设置 `html/canvas_resize_policy=0` 并显式管理 canvas 缓冲区大小。
- 如果在 `export_presets.cfg` 中使用 `export_filter="all_resources"`，`exclude_filter` 中至少包含：`build/web/*`、`.godot/*`、`.tmp-godot-data/*`、`.tmp-godot-config/*`、`.tmp-godot-cache/*`、`logs/*`、`tools/tests/*`。
- 使用项目本地 XDG 目录进行导出时，Godot 会在项目本地的 `XDG_DATA_HOME` 下搜索导出模板；如果模板安装在常规用户数据目录下，需要在导出前将复制项目的 `export_presets.cfg` 中的 `custom_template/debug` 和 `custom_template/release` 设置为模板的绝对路径。
- 在运行 `--export-release` 之前创建 Web 导出输出目录（例如 `mkdir -p build/web`）；Godot 不会可靠地创建缺失的父目录。
- 必须使用 `html/custom_html_shell` 并将 `res://web/custom_shell.html` 视为唯一权威来源。
- `web/custom_shell.html` 必须：
  - 显式设置 `<canvas id="canvas" width="..." height="...">`
  - 在启动前将相同值重新赋给 `canvas.width` / `canvas.height`
  - 通过居中的 `body` 布局居中 canvas
- 不要直接编辑 `build/web/index.html`（它会在重新导出时被覆盖）。

### 排版实现

**Skill**：`styling-web-game-typography`

应用 `.agents/skills/styling-web-game-typography/references/typography-implementation-guide.md` 中的规则：

- 使用 `Theme` 集中管理字体/颜色/大小（尽量减少逐节点覆盖）
- 将显示角色拆分为 `Heading / Info / Numeric / Emphasis`
- HUD 限制为信息展示；强调样式仅用于事件（不要持续闪烁/发光）
- 数值 HUD 使用等宽字体
- 通过描边/阴影确保在嘈杂背景上的可读性
- 完整的字体采用流程（对比/采用/捆绑/许可证整合）在阶段 8 完成
- 不要捆绑未采用的候选字体
- 在 `THIRD_PARTY_LICENSES.md` 和 `licenses/` 中记录许可证信息

---

## 阶段 6：测试与评估

通过手动游玩和/或 headless 执行来评估已实现的游戏。

### 6a：运行时验证

```bash
PROJECT_DIR="$(pwd)" && \
mkdir -p "$PROJECT_DIR"/.godot-xdg/data "$PROJECT_DIR"/.godot-xdg/config "$PROJECT_DIR"/.godot-xdg/cache "$PROJECT_DIR"/logs && \
XDG_DATA_HOME="$PROJECT_DIR/.godot-xdg/data" \
XDG_CONFIG_HOME="$PROJECT_DIR/.godot-xdg/config" \
XDG_CACHE_HOME="$PROJECT_DIR/.godot-xdg/cache" \
godot --headless --path "$PROJECT_DIR" --script res://tools/tests/run_tests.gd 2>&1 | tee "$PROJECT_DIR/logs/test.log"
```

如果创建 `run_tests.gd`，至少包含：

- 单调输入测试（`no_input` / `spam_action` / `hold_action`）
- 探索性输入测试（随机或启发式，多次试验）
- 输出 `exploratory.best.score` 和 `monotonous.max_score`
- 每次运行输出 `logs/test.json`，包含以下必需的最少字段：
  - `monotonous.max_score`
  - `exploratory.best.score`
  - `exploratory_ratio`
  - `telemetry.death_analysis / spawn_analysis / scoring_analysis / input_analysis`
- 缺少必需字段视为测试失败
- 自动更新 `logs/improvement_report.md` 以便进行改进历史对比

### 6b：机制评估（探索比率）

```text
exploratory_ratio = exploratory.best.score / monotonous.max_score
```

| 探索比率        | 评估        | 含义                                       |
| :-------------- | :---------- | :----------------------------------------- |
| <= 1.0          | 不通过      | 单调输入为最优（无技巧可言）                |
| 1.0 - 1.5       | 需要改进    | 技巧体现不够                                |
| > 1.5           | 通过        | 更好的操作方式得到了奖励                     |

命令成功仅视为运行时/架构验证通过。机制的通过/不通过必须根据 `logs/test.json` 中的 `exploratory_ratio` 和以下清单来判断；测试命令可能退出码为 0，但机制评估不通过。

探索比率是必要条件但非充分条件。以降低体验为代价的 KPI 提升会被拒绝。

检查项：

- [ ] 游戏结束条件功能正常
- [ ] 得分按预期累加
- [ ] 难度随时间增加
- [ ] 狂按按键/闲置不是最优策略
- [ ] 技巧性操作得到了奖励
- [ ] 每个新增的状态变量都在代码中实现了非 HUD 的游戏世界因果关系

主观视觉/声音评估和 UI 隐含理解性检查在阶段 8 进行。

---

## 阶段 7：改进评估报告

分析阶段 6 中发现的问题并提出改进候选方案。

- 提出至少 3 个方案（不能只有一个）
- 方案构成：
  - 方案 A：使用改进操作符（见下文）
  - 方案 B：使用与 A 不同的操作符组合
  - 方案 C：不使用这些操作符类型的自由方案（用于对比）
- 对每个方案，说明预期影响、风险和复杂度成本（状态数量/异常规则数量）
- 在 `docs/README.md` 和 `logs/improvement_report.md` 中记录方案
- 阶段 7 完成后，执行 Web 导出并进入阶段 8

### 改进操作符（搜索算法）

- `状态精简`：移除需要解释说明的状态变量，合并到现有状态中
- `整合到世界表征`：将仅存在于 HUD 的信息转移到地形/行为/颜色/声音的因果关系上
- `输入语义反转`：根据上下文/阶段切换相同输入的角色，创造判断情境
- `空间历史化`：将玩家操作结果持久化到环境中，影响后续决策
- `风险收益转移`：减少安全区的稳定得分，将奖励转移到有风险的成功上

每次评估选择 2-3 个操作符，在不同方案中变换组合。

### 违规修复模板

- 如果单调输入为最优：
  - 减少安全的稳定得分
  - 将得分机会转移到只能在风险条件下实现的位置
  - 将预期的探索比率变化记录为预测
- 如果状态变量过多：
  - 移除理由薄弱的已添加状态
  - 合并到现有状态中，同时保留决策结构
  - 明确说明精简后必须保留的决策

### 机制改进

**Skill**：`evaluating-gameplay-balance`
**参考**：`.agents/skills/evaluating-gameplay-balance/references/improvement-analysis.md`、`.agents/skills/evaluating-gameplay-balance/references/balance-patterns.md`

- 识别根本原因（逻辑变更，而非单纯的数值调整）
- 在候选方案中应用/对比 `.agents/skills/evaluating-gameplay-balance/references/balance-patterns.md` 中的模式
- 对于阶段 8 的后续 Godot 实现，在选择引擎无关的模式后参考 `.agents/skills/scaffolding-godot-mini-games/references/godot-balance-pattern-examples.md`
- 将"需要解释说明的状态变量"作为精简目标，整合到世界侧行为中
- 改进报告必须记录："提出了 3 个方案"、"采纳候选理由"和"拒绝理由"
- 仅在人类于阶段 8 选择方案后实施

主观视觉/声音改进不在阶段 7 的范围内。

### 禁止事项

- 仅做数值调整（如 `speed *= 0.8`）
- 仅添加条件分支（如 `if too_hard: make_easier()`）
- 增加随机性
- 声称通过仅添加状态变量来提升深度
- 将仅改变颜色视为充分的反 AI 通用化措施
- 将添加 HUD 文字视为充分的反馈修复
- 对输入事实直接计分（如活跃度奖励）
- 直接对不行动实施失败的元惩罚（如因闲置/停滞而即死）
- 仅为了通过测试指标而添加的隐藏规则（专用于自动播放的分支）

---

## 阶段 8：人机协作改进

可选阶段，人类查看/游玩 Web 导出版本，通过与 AI 智能体的对话迭代改进。

### 目标

- 用真实体验品质（手感/可读性/声音印象/节奏）补充 headless 指标
- 通过引入人类反馈，减少设计意图与实际游玩体验之间的偏差

### 最低操作规则

- 记录人类游玩观察的简短笔记并将请求传递给 AI
- AI 实现请求并每次重新运行阶段 6 测试
- 测试后始终更新阶段 7 评估报告
- 修改后执行 Web 导出
- 迭代对话可以持续所需的任意轮次
- 完整的排版执行（字体对比/采用/捆绑/许可证记录）通常应在此阶段完成
- 排版实现遵循 `.agents/skills/styling-web-game-typography/references/typography-implementation-guide.md`，并更新 `docs/TYPOGRAPHY_DECISION.md`、`docs/THIRD_PARTY_LICENSES.md` 和 `licenses/`

### 记录（推荐）

- 在 `logs/improvement_report.md` 中添加"人类反馈"章节，记录原因和变更内容

---

## 最终报告

在阶段 7 完成时，必须输出以下报告。
因为阶段 7 仅做评估，改进后列中允许填写"未实现 / 不适用"。
如果在阶段 8 进行了实现，使用重新运行的阶段 6 结果更新此报告。

```markdown
# Game Generation Report: <GAME_NAME>

## Selected Tags

### Mechanics Tags

- tag1, tag2, tag3

### Visual Tags

- vtag1, vtag2

### Structure Tags

- stag1

## Test Results

| Metric            | Initial | After Improvement |
| :---------------- | :------ | :---------------- |
| Exploratory Ratio | X.Xx    | Y.Yx              |

Note: Visual/sound/AI-genericness evaluations are added only if Phase 8 is executed.

## Improvements

### Mechanics Improvement

1. <What changed and why>

### Visual Improvement

1. <What changed and why>

### Sound Improvement

1. <What changed and why>
```

---

## 文件列表

| 文件                                        | 用途                                       | 引用阶段         |
| :------------------------------------------ | :----------------------------------------- | :--------------- |
| `data/tags/mechanism_tags.csv`              | 机制标签参考目录                            | 阶段 1           |
| `data/tags/visual_tags.csv`                 | 视觉标签参考目录                            | 阶段 1           |
| `data/tags/structure_tags.csv`              | 结构标签参考目录                            | 阶段 1           |
| `.agents/skills/designing-mini-games/`      | 机制设计 skill 和参考文档                   | 阶段 2           |
| `.agents/skills/directing-game-visuals/`    | 视觉设计 skill 和参考文档                   | 阶段 3           |
| `.agents/skills/creating-godot-procedural-audio/` | 程序化音频 skill、参考文档和资源        | 阶段 4           |
| `.agents/skills/scaffolding-godot-mini-games/` | 新游戏初始化模板 skill                    | 阶段 5           |
| `.agents/skills/running-headless-godot/`    | Godot headless 操作 skill                   | 阶段 5-6         |
| `.agents/skills/styling-web-game-typography/` | 排版实现/许可证 skill                     | 阶段 5/8         |
| `.agents/skills/evaluating-gameplay-balance/` | 平衡分析和改进 skill                     | 阶段 7           |

### 与随机版的差异

- **阶段 1**：移除了 `random_tag_selector.js` 和 `obvious_pairs.json` 依赖。支持三种创意输入模式（纯标签 / 游戏策划案 / 游戏点子），标签可由人类直接指定或由 AI 从策划案/点子中推导后经人类确认。
- **无 `scripts/` 目录**：不需要 `random_tag_selector.js` 脚本。
- **无 `data/tags/obvious_pairs.json`**：不需要非显而易见组合的验证。
- **文件列表**：移除了 `scripts/random_tag_selector.js` 和 `data/tags/obvious_pairs.json` 的引用。
- 其余阶段 2-8 保持不变。
