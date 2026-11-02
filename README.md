# 玻尔组件搭建与文档

面向组件库建设与维护人员，提供 `bohr-component-docs` Skill：从 Figma 设计抽取、搭建原子／组合／业务组件，完善状态、属性、命名、图标、变量与组件文档。

## 安装与使用

下载或克隆本仓库，将完整的 `skills/bohr-component-docs/` 目录安装到所用 Agent 的技能目录。Codex 可复制到 `~/.codex/skills/bohr-component-docs/`；覆盖旧版前先备份，并在新会话确认技能可用。其他 Agent 按其技能安装方式操作。

调用示例：

```text
使用 $bohr-component-docs，按玻尔组件库规则搭建指定组件，保留真实实例和变量，验证状态并整理文档。
```

不支持技能安装的工具可读取 [SKILL.md](skills/bohr-component-docs/SKILL.md)，并按任务读取其参考文件。仅复制入口文件会丢失配套规则。

需要生成、抽取、搭建玻尔组件或补齐组件状态时，必须使用本 Skill。希望在其他工作区持续执行此规则，请将本仓库 AGENTS.md 中的调用规则加入该工作区支持的项目指令；安装 Skill 本身不保证每次自动触发。

## 能力与边界

- 组件构建、唯一路径、实例复用、状态与属性验收。
- 玻尔图标来源、功能语义、Scale 缩放与颜色／主题检查。
- 统一组件文档模板、原英文保护与分项验收。
- Figma 操作需要可用工具、文件权限，以及 Skill 指定的 Figma 依赖技能。
- 包结构校验与专项验证不等于完整生成回归、跨 Agent 兼容或组件库正式发布；按实际任务报告未验证项。

## 与设计语言的关系

仅使用已有组件进行选型、组合和业务页面设计，使用独立的 [Bohr-Design](https://github.com/isawang2023/Bohr-Design) 仓库。两套 Skill 分别维护和更新。

本 Skill 从 Bohr-Design 迁入；后续组件 Skill 更新以本仓库为准。已安装副本不会随 GitHub 更新自动同步。
