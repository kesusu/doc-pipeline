# doc-pipeline — 扫描PDF转可编辑Word，LaTeX公式双击可改

[English](README.md) | Claude Code 技能：OCR 文字识别 + 文档转换

**扫描 PDF / 图片 → 可编辑 Word，公式双击即可修改。** 一条命令，完整流水线。

> 教材数字化、试卷转 Word、课件截图提取文字。基于 PaddleOCR + pandoc。

## 这是什么？

一个 Claude Code 技能，帮你把**扫描件变成可编辑的 Word 文档**，公式保持可双击编辑。

输入 `/doc-pipeline`，Claude 自动完成 OCR 识别 + 文档转换。

## 适用场景

| 场景 | 说明 |
|------|------|
| 教材 PDF 转 Word | 扫描版教材 → 可复制、可编辑的 Word，公式可修改 |
| 试卷转 Word | 考试扫描件 → 可编辑文档，方便重新排版出题 |
| 课件截图提取文字 | 拍照的 PPT/板书 → Markdown 文字，整理笔记 |
| 已有 Markdown 转 Word | 笔记/文档 → 排版规范的 Word，公式自动渲染 |
| 论文扫描件转文字 | 扫描版论文 → 可搜索的文本，方便引用 |
| 期末复习资料整理 | 多份扫描件统一转为可编辑 Word，方便标注和补充 |
| 批量文档数字化 | 一整个文件夹的 .md 一次性转为 Word，字体排版统一 |
| 复习笔记电子化 | 手写笔记拍照 → OCR → Word，复习时可搜索可编辑 |

## 核心功能

- **OCR 文字识别** — 调用 PaddleOCR API，支持扫描 PDF 和图片，异步轮询处理多页文档
- **LaTeX 公式 → 可编辑 Word 公式** — 用 pandoc `--mathml` 转为 Office Math，Word 里双击即可修改
- **Word 排版规范强制执行** — 标题与正文同页（keepNext）、表格行不跨页拆行（cantSplit）、段落孤行控制、表格默认全框线——遵循专业排版规范
- **中文字体精确控制** — 强制宋体正文、黑体标题、Times New Roman 英文，覆盖 Word 主题字体，各平台字体名一应俱全
- **跨平台** — Windows / macOS / Linux，自动查找 pandoc 和 Python
- **三种模式** — 纯 OCR、纯转换、完整流水线（OCR → Word 一步到位）
- **Claude Code 集成** — 输入 `/doc-pipeline` 即可，Claude 处理环境检测、用户交互、错误处理

## 三种模式

| 模式 | 输入 | 输出 |
|------|------|------|
| A — 纯 OCR | 扫描 PDF / 图片 | Markdown 文字 |
| B — 纯转换 | 已有 Markdown 文件 | Word 文档（含可编辑公式） |
| C — 完整流程 | 扫描 PDF / 图片 | Word 文档（一步到位） |

## 前置条件

| 依赖 | 哪些模式需要 | 安装方法 |
|------|------------|---------|
| Python 3.8+ | 全部 | [python.org](https://python.org) |
| [pandoc](https://github.com/jgm/pandoc/releases) | B、C | `winget install JohnMacFarlane.Pandoc`（Win）/ `brew install pandoc`（Mac）/ `sudo apt install pandoc`（Linux） |
| pip 依赖 | 全部 | `pip install requests python-docx lxml` |
| PaddleOCR API Token | A、C | 免费注册：[aistudio.baidu.com](https://aistudio.baidu.com/paddleocr) |（或其他文字识别OCR亦可）

模式 B（Markdown → Word）**不需要** API Token。

## 安装

```bash
# 1. 克隆或下载本仓库
git clone https://github.com/YOUR_USERNAME/doc-pipeline.git

# 2. 复制到 Claude Code 命令目录
cp doc-pipeline.md ~/.claude/commands/
cp -r doc-pipeline/ ~/.claude/commands/

# 3. 安装 Python 依赖
pip install -r ~/.claude/commands/doc-pipeline/scripts/requirements.txt

# 4. 安装 pandoc（见上方表格）
```

**5. 配置 OCR（仅模式 A/C 需要，模式 B 不需要）**

1. 打开 https://aistudio.baidu.com/paddleocr
2. 点「API」，选择你想用的识别方案（作者用的是 PaddleOCR-VL-1.5）
3. 网站会给你一段示例代码，**整段复制发给 Claude**，它会自动帮你填好配置

用别的 OCR 服务也一样：把你的 API 地址和 Token 发给 Claude，它帮你改。

## 使用方法

在 Claude Code 中输入：

```
/doc-pipeline
```

Claude 会自动检测环境、确认需求、执行转换。

也可以直接指定：

```
/doc-pipeline 把 textbook.pdf 转成 Word
/doc-pipeline 转换 notes 目录下的所有 md
```

### 不依赖 Claude Code 单独使用

Python 脚本可以独立运行：

```bash
# 仅 OCR
python scripts/ocr_api.py 输入文件.pdf 输出目录/

# 仅转换
python scripts/convert.py md目录/ docx输出目录/
```

## 样例

`sample/` 目录下有演示文件：

- `sample/test_formulas.md` — 输入：含 LaTeX 公式、表格、标题的 Markdown
- `sample/test_formulas.docx` — 输出：可编辑公式、全框线表格、正确字体的 Word

这个样例是用 `convert.py` 实际运行生成的——你拿到的效果和这个一样。

## 文件结构

```
~/.claude/commands/
├── doc-pipeline.md              ← 技能入口（Claude 读取的指令文件）
└── doc-pipeline/
    ├── .gitignore               ← 防止密钥/Token 泄露
    ├── README.md                ← 英文文档
    ├── README_CN.md             ← 中文文档（本文件）
    ├── docs/
    │   ├── guide.txt            ← 英文使用指南
    │   └── 安装指南.txt         ← 详细中文使用指南
    ├── sample/
    │   ├── test_formulas.md     ← 演示输入（含公式的 Markdown）
    │   └── test_formulas.docx   ← 演示输出（可编辑 Word）
    └── scripts/
        ├── ocr_api.py           ← OCR 封装（PaddleOCR API）
        ├── convert.py           ← Markdown → Word（3步：pandoc转字→字体→排版规范）
        ├── pandoc_reference.docx← Word 输出模板
        └── requirements.txt     ← pip 依赖
```

## 字体配置

编辑 `scripts/convert.py` 顶部的 `FONT_CONFIG`：

```python
FONT_CONFIG = {
    'cn_body': 'SimSun',          # 正文中文字体
    'cn_heading': 'SimHei',       # 标题中文字体
    'latin': 'Times New Roman',   # 英文/数字/公式字体
}
```

各平台常见中文字体名：
- **Windows**: SimSun（宋体）、SimHei（黑体）、KaiTi（楷体）、Microsoft YaHei（微软雅黑）
- **macOS**: Songti SC（宋体）、Heiti SC（黑体）、Kaiti SC（楷体）
- **Linux**: WenQuanYi Micro Hei（文泉驿微米黑）、Noto Sans CJK SC（思源黑体）

## 环境变量

所有 OCR 配置都可以通过环境变量覆盖，无需修改源码：

| 变量 | 覆盖项 | 默认值 |
|------|--------|--------|
| `PADDLEOCR_TOKEN` | API 认证 | （空，必须配置） |
| `PADDLEOCR_MODE` | `sync` 或 `async` | `async` |
| `PADDLEOCR_SYNC_URL` | 同步 API 地址 | PaddleOCR 官方 |
| `PADDLEOCR_ASYNC_URL` | 异步 API 地址 | PaddleOCR 官方 |

## 安全

- **源码不含 API 密钥。** `CONFIG["token"]` 默认为空字符串。
- **Token 不离开你的电脑。** 通过环境变量或本地编辑配置。
- `.gitignore` 已排除 `.env`、`__pycache__/`、所有输出目录。

## 局限性

- 异步 OCR：多页 PDF 通常需要 1-5 分钟（不同厂商产品速度不同）
- 同步模式：仅限单页/小文件（30 秒超时）
- 可编辑公式需要 Word 2016+
- Linux 用户可能需要手动安装中文字体

## 相关技能

- **[/word-gen](../word-gen.md)** — 用 python-docx 从零生成 Word 文档（表格、报告、结构化数据）
- 两者共享字体配置模式和 Python 环境

## Star

如果这个工具帮你省下了重新打一本教材的时间，点个 Star 吧 — 你的键盘会感谢你的。

遇到 Bug 或有想法？开 Issue。觉得好用？分享给还在手动打字的同学。

**让更多人少走弯路。**

## License

MIT
