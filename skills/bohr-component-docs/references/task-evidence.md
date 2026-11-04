# 任务清单与证据记录

用于本次任务执行和本地验收，不插入给设计师阅读的画布正文。只检查授权范围；普通局部修复无需补齐无关页面或重新采集无关线上案例。

## 生成前

保存 `contract.json`：任务范围、三类参照（视觉模板、组件能力/案例、线上来源；不适用说明原因）、参考案例/状态逐项清单和检查项。P/A/B/C/D/C1/C2/E沿用acceptance.md；每组至少一项，局部任务的无关组记不适用及理由。适用组按实际案例/状态展开，不能只留“整体检查通过”一行。每个参考案例和要求的端侧场景至少关联一个检查项。以主组件链、状态、内容区分案例，不按名称或数量替代。

检查项包括：唯一id、group、subject（源节点/状态或场景ID）、applicable、expected、method（equal或review）、evidence_kind。不适用项填写reason。equal用于锁定数值/结构/属性的客观比较；review用于需要判断的视觉、语义和来源对应。D的线上案例项使用raw-online，源库设计项使用raw-design；两者不能互换。其他检查通常使用raw-design。

每条三类参照含role、locator和适用说明；源清单的完整性由实际读取验证，校验器不能替你发现未列的参考案例。线上端侧在scope中分别列明，未检查或受阻仍保留为适用待完成项，不能改成不适用。

## 生成与复验

## 业务场景结构记录

交付Web／桌面业务案例时，contract顶层必须包含 `deliverables: ["business-cases"]` 及非空 `business_scenarios`。纯局部图标修复不声明此交付类型，不要求补建业务页面。每个场景使用下列结构，引用同一contract中的检查项id；不是另写一套自评结果。

```json
{
  "id": "feedback-web",
  "platform": "Web",
  "task": "描述问题并提交反馈",
  "source_check": "feedback-web-source",
  "composition_check": "feedback-web-composition",
  "elements": [
    {"id": "description", "source": "原始观察中的问题描述输入", "check": "feedback-input"},
    {"id": "consent", "source": "原始观察中的日志复选框", "check": "feedback-checkbox"},
    {"id": "submit", "source": "原始观察中的提交按钮", "check": "feedback-submit"}
  ],
  "relations": [
    {"from": "consent", "to": "submit", "check": "feedback-consent-before-submit"}
  ]
}
```

`source_check`引用适用的D/raw-online检查，`composition_check`引用适用的C/raw-design检查；元素及关系引用适用的raw-design检查。每项预期来自锁定的源，report中必须有目标节点、实际读回、证据及当前版本，沿用下文检查机制。整体组合检查的target是完整片段根，actual覆盖必要子节点/关系；元素检查的target是对应控件节点。场景缺失、映射悬空、必要项被标不适用、来源混用均不放行。源码列表未收录的元素、捏造节点或整体检查实为单体，仍须人工对照原始证据拦截；脚本不认证这些事实。

### 结果与版本

保存 `report.json`，引用contract文件的SHA-256，并填写最新产物revision及每项checked_revision。任何修改递增revision；只重新检查受影响项，未受影响项可在完成影响分析后重用，必须写明复用依据并核对文件摘要。不能无依据批量替换revision。

每项结果包括id、target（真实目标节点/文档段落）、actual、status（已通过/未通过/未验证/不适用）、evidence。review通过还需decision，描述如何从证据得出结论。证据项包含path、sha256、kind、locator；路径相对report文件，指向保存的原始返回或观察记录，locator定位其中的节点/操作/字段。在线原始记录须脱敏，保留入口、端侧、日期、操作和前后状态。工具原始输出与整理说明分文件存放；禁止将自写摘要改名为原始证据。

映射以「检查项subject → 结果target」表示；一个源案例可有多个检查项。翻译允许合理增高，业务扩展允许新增案例，不要求页高/总数量完全相等；固定字段依批准参照判断。授权字体例外、模板变更先更新contract并记录授权范围和依据，然后重新验收相关项；不能为了消除错误而悄悄修改预期。

最小结构示意（完整任务还须列齐八组，以下不能直接作为通过报告）：

```json
{
  "scope": "指定组件基础示例；Web与桌面案例分别取源",
  "references": [
    {"role": "visual", "locator": "file/node"},
    {"role": "capability", "locator": "file/node"},
    {"role": "online", "locator": "Web入口及桌面入口"}
  ],
  "checks": [
    {"id": "example-light-composition", "group": "C", "subject": "源案例节点/Light", "applicable": true, "expected": {"composition": "完整组件", "gap": 4}, "method": "equal", "evidence_kind": "raw-design"}
  ]
}
```

```json
{
  "contract_sha256": "contract.json文件的完整SHA-256",
  "revision": "r1",
  "checks": [
    {"id": "example-light-composition", "target": "file/目标节点", "checked_revision": "r1", "actual": {"composition": "完整组件", "gap": 4}, "status": "已通过", "evidence": [{"path": "readback.json", "sha256": "原始文件的完整SHA-256", "kind": "raw-design", "locator": "目标节点及布局字段"}]}
  ]
}
```

## 收尾

```sh
python3 <skill目录>/scripts/check_evidence.py contract.json report.json > check-result.json
```

退出码0仅代表记录校验通过；1表示缺项、差异、未通过/未验证或过期证据；2表示输入无效。记录校验失败时保留已做工作并继续修复可修项；受阻项写恢复条件，最终只报告部分完成。不得删检查项、将受阻项改不适用或伪造原始记录来获得0。

最终报告引用check-result.json及人工验收结论，按acceptance.md判定任务状态。没有宿主级强制拦截；本脚本不能阻止执行者跳过检查，更不能认证工具输出的真实性。脚本通过不等于视觉、业务、发布或宿主加载通过。
