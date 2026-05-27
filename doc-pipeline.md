---
allowed-tools: Bash, Read, Write, Glob, Grep
description: OCR 文字识别 + Markdown 转 Word 文档的完整流程。支持 PaddleOCR API（用户自行注册）和 pandoc 转换。用户输入 /doc-pipeline 启动。
---

# 文档处理流水线（Claude 执行指令）

> **此文件为 Claude Code 技能指令文件，不是给用户阅读的文档。**
> 使用说明请查看 `docs/安装指南.txt`。

将扫描 PDF / 图片通过 OCR 提取文字，再将 Markdown 转为可编辑 Word 文档（含可编辑公式）。

## 用户需求

$ARGUMENTS

---

## 工具链

所有脚本位于 `scripts/` 下（相对于本文件所在目录）。

| 文件 | 用途 |
|---|---|
| `scripts/ocr_api.py` | PaddleOCR API 封装，支持同步/异步模式 |
| `scripts/convert.py` | pandoc md→docx + 字体强制 + 排版规范（keepNext/cantSplit/孤行控制） |
| `scripts/pandoc_reference.docx` | pandoc 输出模板 |
| `scripts/requirements.txt` | pip 依赖 |

**相关 skill**：如需从零生成 Word 文档（而非转换），使用 `/word-gen`。

---

## 执行流程

### Step 0：环境检测（自动执行，不要跳过）

用 Bash 跑以下检查，逐项输出 OK/MISSING。python 和 python3 都试：

```bash
cd ~/.claude/commands/doc-pipeline
echo "=== 环境检查 ==="

# Python
if python3 --version >/dev/null 2>&1 || python --version >/dev/null 2>&1; then
  echo "Python: OK"
else
  echo "Python: MISSING"
fi

# Pandoc（PATH 或常见安装路径）
if pandoc --version >/dev/null 2>&1; then
  echo "Pandoc: OK"
elif [ -f "$LOCALAPPDATA/Pandoc/pandoc.exe" ] 2>/dev/null || [ -f "/usr/local/bin/pandoc" ] 2>/dev/null || [ -f "/opt/homebrew/bin/pandoc" ] 2>/dev/null; then
  echo "Pandoc: OK（未在 PATH，但 convert.py 可自动找到）"
else
  echo "Pandoc: MISSING"
fi

# python-docx
if python3 -c "import docx" >/dev/null 2>&1 || python -c "import docx" >/dev/null 2>&1; then
  echo "python-docx: OK"
else
  echo "python-docx: MISSING"
fi

# lxml
if python3 -c "import lxml" >/dev/null 2>&1 || python -c "import lxml" >/dev/null 2>&1; then
  echo "lxml: OK"
else
  echo "lxml: MISSING"
fi

# requests
if python3 -c "import requests" >/dev/null 2>&1 || python -c "import requests" >/dev/null 2>&1; then
  echo "requests: OK"
else
  echo "requests: MISSING"
fi

# OCR Token: check both env var and source file
if [ -n "$PADDLEOCR_TOKEN" ]; then
  echo "OCR Token: 已配置（环境变量）"
elif grep -qE '"token"[[:space:]]*:[[:space:]]*"[^"]+' scripts/ocr_api.py 2>/dev/null; then
  echo "OCR Token: 已配置（源码）"
else
  echo "OCR Token: 未配置（仅 OCR 功能需要）"
fi

echo "=== 检查完毕 ==="
```

如有 MISSING：
- pip 依赖：自动执行 `pip install python-docx lxml requests`（先告知用户再装）
- pandoc：告知用户手动安装（winget/brew/apt），参考 `docs/安装指南.txt`
- Token：告诉用户去 https://aistudio.baidu.com/paddleocr 获取 API 代码，把整段示例代码发给你，你从中提取 Token 写入 `scripts/ocr_api.py` 的 `CONFIG["token"]`

### Step 1：确认意图

根据 `$ARGUMENTS` 自动判断：
- 含 `.pdf` / `.jpg` / `.png` 等 → **模式 C**（完整流程：OCR → Word）
- 含 `.md` → **模式 B**（仅转换：md → Word）
- 为空或不明确 → 询问用户：
  ```
  A. OCR 识别（图片/PDF → Markdown）
  B. 转换文档（已有 Markdown → Word）
  C. 完整流程（OCR → Word）
  ```

### Step 2：确认路径

- 输入文件/目录：从 `$ARGUMENTS` 提取或询问
- 输出目录：默认 `<输入目录>/docx_output/`
- OCR 中间目录：默认 `<输入目录>/ocr_output/`

### Step 3：执行

```bash
cd ~/.claude/commands/doc-pipeline

# OCR（模式 A/C）— ocr_api.py 接受绝对路径，但 cd 保证脚本内相对路径一致
python scripts/ocr_api.py "<输入文件>" "<OCR输出目录>"

# 转换（模式 B/C）— convert.py 需要 cd 以定位 pandoc_reference.docx 模板
python scripts/convert.py "<md目录>" "<docx输出目录>"
```

> **关于 `cd`**：`ocr_api.py` 的输入输出参数均为绝对路径且自带 `os.path.exists` 检查，不强依赖 cwd；`convert.py` 需要 cd 以找到同目录下的 `pandoc_reference.docx` 模板。因此统一 cd 是最安全的做法。

模式 C 串联：等 OCR 完成 → 自动调用转换。中间不需确认。

### Step 4：完成报告

交付内容：
- 生成文件列表（带完整路径）
- 公式可在 Word 中双击编辑
- 字体配置在 `scripts/convert.py` 的 `FONT_CONFIG`，如用户需要修改则指导编辑
- OCR 配置在 `scripts/ocr_api.py` 的 `CONFIG`，支持环境变量覆盖
