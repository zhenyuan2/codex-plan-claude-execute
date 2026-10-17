# codex-plan-claude-execute

**Codex 规划 → Claude Code 实现 → Codex 验收与复核。**

将明确的实现任务交给 Claude Code CLI，保留独立验收、有限重试和完整运行日志。使用 Claude Code 当前配置的默认模型，也可显式指定模型。

本包供 **Codex** 加载，不要安装到 Claude Code 中让它调用自身。

## 环境要求

- macOS 或 Linux，Python 3.8+、Bash。
- 已安装并登录 Claude Code；`claude --version` 可用。执行时需要模型服务网络访问和 Claude 会话目录写入权限。
- Codex；插件安装方式还要求 CLI 提供 `codex plugin` 命令。没有插件命令可用直接安装方式。
- 运行器支持的 Claude 参数以 `scripts/run-claude.sh --help` 为准；不会自动安装依赖或修改登录配置。

## 安装

以下命令均在本仓库根目录执行。两种方式任选一种，避免同一 skill 被重复发现。

### 方式一：直接安装 skill

```bash
python3 install.py
```

默认安装到 `~/.agents/skills/codex-plan-claude-execute/`。已有同名目录时默认拒绝覆盖。更新已有安装：

```bash
python3 install.py --replace
```

旧版本自动备份到 skills 上一级目录的 `.skill-backups/`，安装器会打印具体路径。

也可以安装到项目内，`--dest` 指向完整的 skill 目录：

```bash
python3 install.py --dest /path/to/project/.agents/skills/codex-plan-claude-execute
```

安装只是复制文件，不调用模型、不修改 Codex 配置。

### 方式二：作为本地插件市场安装

```bash
codex plugin marketplace add .
codex plugin add codex-plan-claude-execute@codex-plan-claude-execute-marketplace
codex plugin list
```

这种方式使用仓库的 `.claude-plugin/marketplace.json` 和插件清单。目录名沿用兼容格式；插件的目标宿主仍然是 Codex。

从 GitHub 安装：

```bash
codex plugin marketplace add zhenyuan2/codex-plan-claude-execute
codex plugin add codex-plan-claude-execute@codex-plan-claude-execute-marketplace
```

已有直接安装版本时，请先保留备份并移出 skills 搜索目录，再选择插件安装，避免重复。

## 使用

在 Codex 中输入：

```text
使用 $codex-plan-claude-execute，先分析当前项目并制定计划，
然后交给 Claude Code 实现，最后由 Codex 验证结果。
任务：为现有搜索接口增加分页，并补充相关测试。
```

流程：

1. Codex 读取项目规则和现有修改，生成一份有效计划与验收块。
2. Claude Code 根据计划实现，报告完成、部分完成或阻塞。
3. 运行器执行验收，仅对已完成实现后的验收失败进行有限重试。
4. Codex 检查实际变更、测试和完成标准，给出最终结论。

已有执行授权时不重复要求确认；新增范围或权限需求仍需明确处理。

## 参数与日志

运行器位于 `plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/`。

| 参数 | 含义 |
|---|---|
| `--repo PATH` | 明确执行目录 |
| `--attempts N` | 本次调用最多模型调用次数，默认 3 |
| `--max-turns N` | 每次 Claude 调用轮次上限，默认 60 |
| `--timeout SECONDS` | 模型与验收总运行时间，默认 1800 秒 |
| `--max-budget USD` | 本次调用内累计 CLI 报告费用预算，可选 |
| `--model NAME` | 指定 Claude 模型，可选 |
| `--allowed-tool RULE` | 额外自动授权规则，可重复指定 |

`--max-budget` 依赖 Claude 的 `total_cost_usd`，不是实际账单硬上限。当前按每次调用费用累加；`--resume` 后费用字段语义尚未做真实模型验证，若返回会话累计费用可能提前停止。不适合当作精确财务控制。

默认自动授权文件工具；命令授权按任务添加。工具授权不是系统沙箱，也不自动允许推送、部署等外部操作。

日志在项目 `.plans/runs/<唯一运行目录>/`，含计划快照、Git 基线、逐次模型/验收输出及汇总。退出码 `0` 仅表示自动验收通过，仍需 Codex 复核；`1` 表示停止或失败，`2` 表示参数、环境或协议错误。

## 检查运行入口

```bash
bash plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh --help
```

开发测试文件仅保留在本地，不纳入 Git 或 GitHub 分发。运行 skill 不依赖测试文件。当前已做离线验证，尚未完成真实模型端到端验证。

## 目录

```text
.claude-plugin/marketplace.json
plugins/codex-plan-claude-execute/
  .claude-plugin/plugin.json
  skills/codex-plan-claude-execute/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
install.py
README.md
```

## 卸载

直接安装：确认实际安装位置后，将对应 `codex-plan-claude-execute` 目录移出 skills 目录。

插件安装：

```bash
codex plugin remove codex-plan-claude-execute@codex-plan-claude-execute-marketplace
```

## 参考

- [cc-skill-codex](https://github.com/wywwzjj/cc-skill-codex)：参考其插件市场与 skill 分层结构；本包只包含 Codex → Claude Code 的规划执行流程。
- [OpenAI 插件文档](https://developers.openai.com/codex/plugins/)

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

仓库：https://github.com/zhenyuan2/codex-plan-claude-execute
