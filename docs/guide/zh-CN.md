# 快速上手

[English](en.md) · [한국어](ko.md) · [日本語](ja.md) · **简体中文**

从下载到打开 Power BI 报表大约 5 分钟。之后介绍如何用一句话描述需求，让 AI 生成你自己的报表。

## 准备

| | 用途 | 获取方式 |
|---|---|---|
| Windows 10/11 + Power BI Desktop **2.157 或更高** | 必需 | Microsoft Store 免费下载（自动更新）。旧版本会截断部分文字（[#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)） |
| Python 3.10 或更高版本 | 必需 | [python.org](https://www.python.org/downloads/)，安装时勾选 **Add python.exe to PATH** |
| Claude Code | 用自然语言生成报表时 | [claude.com/claude-code](https://claude.com/claude-code) |
| Microsoft PBIR 校验工具 | 可选 | `npm install -g @microsoft/powerbi-report-authoring-cli` |

不需要安装其他东西。脚本只使用 Python 标准库。

## 1. 下载

点击绿色 **Code** 按钮 → **Download ZIP** 并解压。或者：

```bash
git clone https://github.com/Haweee47/powerbi-autopilot.git
```

## 2. 打开一份完成的报表（无需 AI）

双击文件夹中的 **`quickstart.cmd`**。它会用自带的示例数据生成仪表板模板，并在 Power BI Desktop 中打开。

第一次打开时：

1. 黄色提示栏显示“部分表没有数据” → 点击 **立即刷新**
2. 接着如果提示“有尚未应用的更改” → 点击 **应用更改**

想试其他模板、主题或语言，在文件夹中打开终端运行：

```bash
python tools/quickstart.py --purpose matrix --theme midnight
python tools/quickstart.py --all --lang zh-CN
```

| 选项 | 取值 |
|---|---|
| `--purpose` | `dashboard`（仪表板）· `table`（指标表）· `matrix`（矩阵）· `deepdive`（深入分析）· `fulfillment`（履约中心运营） |
| `--theme` | `navy` · `paper` · `midnight` · `aurora` · `coast` · `ledger` · `contrast` |
| `--lang` | `en` · `ko` · `ja` · `zh-CN` |
| `--frame` | `rail`（左侧导航栏）· `top`（顶部菜单栏，正文全宽） |

**公司品牌色。** 用一种颜色生成主题，再把它的 id 传给 `--theme`。蓝、青、紫色系也会用于数据颜色；
红、橙、黄、绿色系只用于左侧导航栏和选中状态，因为报表中的红色已经表示“未达目标”。

```bash
python tools/brand_theme.py --id acme --accent "#0F62FE" --base navy
python tools/build_themes.py
python tools/quickstart.py --purpose dashboard --theme acme
```

结果保存在 `out/` 文件夹，git 会忽略它。折叠筛选器、可视化和数据窗格（»）可以看到完整大小的页面。

## 3. 用一句话生成报表（Claude Code）

```bash
cd powerbi-autopilot
claude
```

然后写下你想要的内容，例如：

> 用 Paper 主题、中文做一个门店 KPI 表。

智能体只会询问你没说明的部分（用途、主题、语言），复制最接近的模板，替换字段和标题，生成 PBIP 并校验。
它遵循的流程见 [`.claude/skills/new-report/SKILL.md`](../../.claude/skills/new-report/SKILL.md)。

## 4. 使用自己的数据

1. 在 Power BI Desktop 中打开现有报表，选择 **文件 → 另存为 → Power BI 项目 (.pbip)**。
   旧版本需先开启 **选项 → 预览功能 → Power BI 项目 (.pbip) 保存选项**。
2. 告诉智能体模型的位置：
   > 用 C:\Reports\Sales\Sales.SemanticModel\definition 的模型做一个仪表板
3. 智能体不会读取整个模型文件，只看一屏摘要。`new_report.py` 会找出模板需要而你的模型没有的全部内容（包括 DAX 里用到的度量值），
   写入 `model-map.json` 并附上参考定义作为提示。智能体只需在这张对照表里填上你的列名和 DAX。示例：[例 05](../../examples/05-own-model/README.md)

数据连接（SQL Server、ODBC、SharePoint Online、文件等）会随模型原样复制，只保存在你的电脑上。凭据不会写入文件。
**ODBC。** ODBC 报表同样按上面的方法另存为 PBIP。连接字符串和 SQL 会原样复制，密码不会写入文件。第一次刷新时选择一次登录方式（默认或自定义、Windows、数据库），Desktop 会记住。在本地 ODBC 驱动上的验证见 [示例 06](../../examples/06-odbc/README.md)；真实数据仓库（Presto、Redshift 等）还没有测试。

**还没有 Power BI 模型？** 可以直接从数据生成模型，之后步骤同上。

```bash
python tools/new_model.py --name Sales --out out/sales-model --csv C:\data\sales        # CSV 文件夹
python tools/new_model.py --name Sales --out out/sales-model --excel C:\data\sales.xlsx  # 每个工作表一张表
python tools/new_model.py --name Sales --out out/sales-model --odbc "<连接字符串>" --table dbo.Orders --table dbo.Stores
```

它读取列名和样本行，类型取自数据源本身，推断键关系，加入日历表，并为每个数值列写一个 SUM 度量值。
推断结果全部打印出来，并写成可编辑的 TMDL。三种数据源的完整示例：[example 07](../../examples/07-own-data/README.md)。
连接字符串中请勿写入密码（使用 DSN 或集成身份验证）。

不要把真实数据提交到仓库或贴到 Issue 里。`out/` 会被 git 忽略，但放在 `examples/` 下的报表会被跟踪。

## 语言

| 语言 | 报表文字 | 数字 | 示例数据值 |
|---|---|---|---|
| English | 完整 | K · M | 英文 |
| 한국어 | 完整 | 만 · 억 | 韩文 |
| 日本語 | 目前大部分为英文 | K · M | 英文 |
| 简体中文 | 目前大部分为英文 | K · M | 英文 |

想让中文版完整？请开一个 [Language support](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=4-language-request.yml) Issue。特别欢迎能帮忙校对的母语使用者。

## 常见问题

| 现象 | 处理方法 |
|---|---|
| 视觉对象是空的 | 点击黄色提示栏的 **立即刷新**，或 **主页 → 刷新** |
| “找不到文件”等数据文件夹错误 | 打开 quickstart 生成在 `out/` 里的报表，而不是 `templates/` 里的（那里的模板是占位路径）。或者在 **转换数据 → 编辑参数 → 데이터폴더** 中填入 `examples\_data\korean-retail\en` 的完整路径 |
| 提示找不到 `python` | 重新安装 Python 并勾选 **Add python.exe to PATH**，或运行 `py tools\quickstart.py` |
| Desktop 无法打开 `.pbip` | 更新 Power BI Desktop |
| 数据窗格中的表名、列名是韩文 | 示例模型是韩国零售数据。页面上的标签已翻译；你自己的模型保留原来的名称 |
| KPI 对比行缺失、文字被截断 | 你的 Power BI Desktop 早于 2.157（**帮助 → 关于**）。如果同时装了安装程序版和 Store 版，双击会打开旧版：请运行 `python tools/quickstart.py --open`，或从开始菜单启动 Desktop 后用 **文件 → 打开**（[#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)） |
| 其他显示问题 | 附上整个窗口的截图[告诉我们](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml) |

## 反馈

每个 Issue 都会被阅读、记录并回复。[反馈如何变成改进](../../CONTRIBUTING.md#how-feedback-becomes-changes)

- [显示有问题](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml)
- [设计意见](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=2-design-feedback.yml)（只打 1–5 分也可以）
- [新模板或新功能](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=3-pilot-request.yml)
- [提问与作品分享](https://github.com/Haweee47/powerbi-autopilot/discussions)
