# 自带程序与外部工具

本目录随 Skill 安装，当前只提供证据记录校验和它的测试；没有直接连接或修改 Figma 的程序。

| 内容 | 职责 | 不证明什么 |
| --- | --- | --- |
| `check_evidence.py` | 核对任务范围、检查项、结果版本及证据引用 | 不认证证据真实、来源穷尽、视觉质量或业务行为 |
| `test_check_evidence.py`、`test_business_evidence.py`、`test_online_execution.py` | 使用测试数据检查校验器逻辑 | 不等于真实 Figma 或线上运行验收 |
| 宿主提供的外部 Figma 工具 | 由 Agent 调用，读取和修改获授权的 Figma 文件 | 安装本 Skill 不会提供连接、权限或自动执行能力 |

可从 Skill 目录执行；从其他工作目录启动时，将下列脚本路径替换成已解析的 Skill 绝对路径，任务路径也用实际绝对路径。路径含空格时按当前执行环境正确传参；不要把示例占位符直接执行。无终端环境按 [受限处理](../references/platform-compatibility.md#缺少能力时) 保存待运行项：

```sh
python3 scripts/check_evidence.py /任务目录/contract.json /任务目录/report.json
python3 -m unittest discover -s scripts -p 'test_*.py'
```

校验器参数与退出状态见 [证据记录](../references/task-evidence.md#收尾)。真实 Figma 操作按 [平台能力核对](../references/platform-compatibility.md#操作规范与能力映射) 加载当前平台的操作规范；有 `figma-use`、`figma-generate-library` 时按任务读取。操作后由 Agent 独立读取最终产物，不能用写入参数冒充读回结果。

Figma 模板和库资产保留在 Figma；本 Skill 保存使用要求与来源指引。任务记录保留在工作区，不写进程序或安装副本。本次结构整理没有新增自动修图标、自动补状态或自动验收能力；后续工具需按真实失败案例另行验证。
