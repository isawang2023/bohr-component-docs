# 图标引入颜色保真与修复

颜色验收比较相同主题、语义状态、背景及有效透明度下的源和目标；不能把源画布 Light 的 RGB 硬套到业务 Dark。先读原图标、目标绘制 Paint、容器及完整父链，再修改授权目标。目标状态合法覆盖优先于机械恢复源默认色，须记录规范依据。

## 两道独立检查

1. **语义绑定**：逐个绘制 Paint 记录源与目标 fills/strokes 的变量 ID、名称、别名链和状态。未经批准的 `color/icon/context` → `icon/default` 覆盖失败，即使当前 RGB 相同。错误、链接、禁用及多色资产不能统一改成默认单色。
2. **主题继承**：记录语义容器预期模式、从容器到路径每层的 `explicitVariableModes`，以及最终路径的 `resolvedVariableModes`。绑定正确但 Light 容器内意外锁定 Dark 仍失败；有据的局部主题反转例外要明确记录。

最终颜色必须通过绑定变量在目标路径上的 `resolveForConsumer`（含别名链）求值；同时记录 Paint RGB、Paint opacity、节点与父层 opacity。仅比较变量名称、缓存 RGB 或截图均不足。若差异来自透明度，不擅自改色补偿。

## 最小修复顺序

1. 记录原值、作用范围及源节点保护快照；先确认错误绑定与模式覆盖的具体层级。
2. 只清除造成错色的目标层、对应主题 collection 的局部模式（`clearExplicitVariableModeForCollection`），使其继承正确语义容器。若祖先本身错误，在授权边界内修正祖先；不能用对子节点强写 Light 掩盖错误父链。不得清空全部模式，尤其不能清除 Scale 所需描边模式。
3. 对未经批准的颜色覆盖，按源与目标语义映射恢复每个实际绘制 Paint 的变量绑定。使用 `setBoundVariableForPaint` 返回的新 Paint 后重新赋值 fills/strokes；保留其余 Paint 字段及透明度，不把多色图标全染成一个色。
4. 禁止写死 HEX/RGB、detach、修改共享颜色变量、整树 resetOverrides 或覆盖业务合法状态。源绑定缺失、语义映射不明、嵌套属性不可编辑时记阻断，不伪造完成。
5. 写后读回：绑定与别名、最终模式、解析颜色、有效透明度、描边及几何。切换 Light/Dark、实际存在的语义状态、重复 swap，并覆盖隐藏路径；修色不能破坏 Scale 与实例链。恢复测试初始主题/显隐状态后再截图。

## 已确认失败样本

2026-11-02，测试 InputGroup `28701:12159` 的 search-md 源 `26309:3378` 使用 `color/icon/context`；目标路径被覆盖为 `icon/default`，Wrapper 在 Light 容器中显式 Dark，目标 #E0E0E0 与源当前 Light #1D2129 不同。这是“语义覆盖 + 主题覆盖”两项差异，不是所有 icon/default 都错误，也不能归因于 Scale。历史 ID 仅作回归定位，每次重新读取。

## 专项用例

- C01：Light 容器，context 被改为 default 且 Wrapper Dark：两项均检出；仅清 Dark 不足以完成语义验收。
- C02：同色但语义变量错误：阻断；有据的业务 error/link 覆盖则按业务规范验收，不恢复默认色。
- C03：合法 Dark 容器继承 Dark：不得为匹配源 Light RGB 而强制 Light 或写死颜色。
- C04：清除主题覆盖后，描边24px模式保留，重复swap颜色不回退，Light/Dark切换与隐藏路径均通过。
- C05：绑定和主题正确但父层opacity错误：检出有效透明度差异，不改色补偿。

决策测试每题独立上下文；真实测试在授权隔离副本注入偏差、记录失败、最小修复、复测并恢复。规则判断、真实色值修复、全量产品验收分别报告。
