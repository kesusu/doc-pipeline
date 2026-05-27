#!/usr/bin/env python3
"""Markdown → Word 批量转换工具。

用 pandoc 将 .md 转为 .docx（公式渲染为 Office Math），再强制设置中英文字体。

用法: python convert.py [输入目录] [输出目录]
依赖: pandoc, python-docx, lxml
"""
import os
import sys
import shutil
import platform
import subprocess
import glob as globmod
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ 字体配置（改这里就行）============
FONT_CONFIG = {
    'cn_body': 'SimSun',          # 正文中文字体
    'cn_heading': 'SimHei',       # 标题中文字体
    'latin': 'Times New Roman',   # 英文/数字/公式字体
}
# ============================================

# 脚本所在目录（用于定位模板）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, 'pandoc_reference.docx')


def find_pandoc():
    """查找 pandoc 可执行文件。"""
    # 优先从 PATH 查找（跨平台）
    p = shutil.which('pandoc')
    if p:
        return p

    # 平台特定路径
    system = platform.system()
    if system == 'Windows':
        username = os.getenv('USERNAME', '')
        candidates = [
            rf'C:\Users\{username}\AppData\Local\Pandoc\pandoc.exe',
            r'C:\Program Files\Pandoc\pandoc.exe',
        ]
    elif system == 'Darwin':  # macOS
        candidates = [
            '/usr/local/bin/pandoc',
            '/opt/homebrew/bin/pandoc',
        ]
    else:  # Linux
        candidates = [
            '/usr/bin/pandoc',
            '/usr/local/bin/pandoc',
        ]

    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def pandoc_convert(md_path, docx_path, pandoc_exe, template=None):
    """调用 pandoc 将 md 转为 docx。"""
    cmd = [
        pandoc_exe, md_path,
        '-o', docx_path,
        '--mathml',  # LaTeX → Office Math (可编辑公式)
    ]
    if template and os.path.exists(template):
        cmd.extend(['--reference-doc', template])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  pandoc 错误: {result.stderr.strip()}")
        return False
    return True


def _apply_fonts(rPr, cn_font, en_font):
    """在 rPr 元素上设置字体。"""
    from docx.oxml.ns import qn
    from lxml import etree

    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), en_font)
    rFonts.set(qn('w:hAnsi'), en_font)
    rFonts.set(qn('w:eastAsia'), cn_font)
    rFonts.set(qn('w:cs'), en_font)
    for tag in ('w:eastAsiaTheme', 'w:asciiTheme', 'w:hAnsiTheme', 'w:csTheme'):
        el = rPr.find(qn(tag))
        if el is not None:
            rPr.remove(el)


def force_fonts(docx_path):
    """强制设置 docx 中所有字体（覆盖主题字体）。"""
    from docx import Document
    from docx.oxml.ns import qn
    from lxml import etree

    CN = FONT_CONFIG['cn_body']
    EN = FONT_CONFIG['latin']
    CN_H = FONT_CONFIG['cn_heading']

    doc = Document(docx_path)

    # 处理所有文本 run — 根据所在段落的样式选择字体
    for run_elem in doc.element.body.findall('.//' + qn('w:r')):
        # 检查父段落是否为标题样式
        p_elem = run_elem.getparent()
        cn_font = CN
        if p_elem is not None:
            pPr = p_elem.find(qn('w:pPr'))
            if pPr is not None:
                pStyle = pPr.find(qn('w:pStyle'))
                if pStyle is not None:
                    val = pStyle.get(qn('w:val'), '')
                    if 'Heading' in val:
                        cn_font = CN_H
        rPr = run_elem.find(qn('w:rPr'))
        if rPr is None:
            rPr = etree.SubElement(run_elem, qn('w:rPr'))
        _apply_fonts(rPr, cn_font, EN)

    # 处理所有样式
    for style in doc.styles:
        rPr = style.element.get_or_add_rPr()
        is_heading = 'Heading' in style.name if hasattr(style, 'name') else False
        cn_font = CN_H if is_heading else CN
        _apply_fonts(rPr, cn_font, EN)

    doc.save(docx_path)


def force_formatting(docx_path):
    """强制排版规范：标题同页、表格不跨页、段落孤行控制。"""
    from docx import Document
    from docx.oxml.ns import qn
    from lxml import etree

    doc = Document(docx_path)

    # 标题 keepNext — 与下段同页
    for para in doc.paragraphs:
        if 'Heading' in para.style.name and para.text.strip():
            pPr = para._p.get_or_add_pPr()
            if pPr.find(qn('w:keepNext')) is None:
                pPr.append(etree.Element(qn('w:keepNext')))

    # 正文孤行控制
    for para in doc.paragraphs:
        if 'Heading' not in para.style.name:
            pPr = para._p.get_or_add_pPr()
            if pPr.find(qn('w:widowControl')) is None:
                etree.SubElement(pPr, qn('w:widowControl'))

    # 表格行 cantSplit — 不跨页拆行
    for table in doc.tables:
        for row in table.rows:
            tr = row._tr
            trPr = tr.get_or_add_trPr()
            if trPr.find(qn('w:cantSplit')) is None:
                trPr.append(etree.Element(qn('w:cantSplit')))

    # 表格默认全框线
    for table in doc.tables:
        tblPr = table._tbl.tblPr
        if tblPr is None:
            tblPr = etree.SubElement(table._tbl, qn('w:tblPr'))
        tblBorders = tblPr.find(qn('w:tblBorders'))
        if tblBorders is None:
            tblBorders = etree.SubElement(tblPr, qn('w:tblBorders'))
        for border_name in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            border = tblBorders.find(qn(f'w:{border_name}'))
            if border is None:
                border = etree.SubElement(tblBorders, qn(f'w:{border_name}'))
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')       # 0.5pt
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), 'auto')

    doc.save(docx_path)


def convert_all(input_dir=".", output_dir=None, template=None):
    """批量转换目录下所有 .md 文件。"""
    # 查找 pandoc
    pandoc_exe = find_pandoc()
    if not pandoc_exe:
        print("错误：找不到 pandoc")
        system = platform.system()
        if system == 'Windows':
            print("安装：winget install JohnMacFarlane.Pandoc")
        elif system == 'Darwin':
            print("安装：brew install pandoc")
        else:
            print("安装：sudo apt install pandoc")
        print("或从 https://github.com/jgm/pandoc/releases 下载")
        sys.exit(1)

    # 查找模板
    if template is None:
        template = DEFAULT_TEMPLATE
    if not os.path.exists(template):
        print(f"提示：未找到模板 {template}，将使用 pandoc 默认样式")
        template = None

    # 验证输入目录
    if not os.path.isdir(input_dir):
        print(f"错误：目录不存在: {input_dir}")
        return

    # 输出目录
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'docx_output')
    os.makedirs(output_dir, exist_ok=True)

    # 查找所有 .md 文件
    md_files = sorted(globmod.glob(os.path.join(input_dir, '*.md')))
    if not md_files:
        print(f"未找到 .md 文件: {input_dir}")
        return

    print(f"找到 {len(md_files)} 个 .md 文件")
    print(f"pandoc: {pandoc_exe}")
    if template:
        print(f"模板: {template}")
    print(f"输出: {output_dir}/")
    print()

    # Step 1: pandoc 转换
    print("=== Step 1: Pandoc 转换 ===")
    ok_count = 0
    for md in md_files:
        name = os.path.splitext(os.path.basename(md))[0]
        docx = os.path.join(output_dir, name + '.docx')
        print(f"  {os.path.basename(md)}", end=' ')
        if pandoc_convert(md, docx, pandoc_exe, template):
            print("OK")
            ok_count += 1
        else:
            print("FAILED")

    print()

    # Step 2: 强制字体
    print("=== Step 2: 强制字体 ===")
    try:
        docx_files = globmod.glob(os.path.join(output_dir, '*.docx'))
        for docx in docx_files:
            try:
                force_fonts(docx)
                print(f"  OK: {os.path.basename(docx)}")
            except Exception as e:
                print(f"  ERR: {os.path.basename(docx)}: {e}")
    except ImportError:
        print("  跳过（需要 python-docx: pip install python-docx lxml）")

    print()

    # Step 3: 强制排版规范
    print("=== Step 3: 排版规范 ===")
    try:
        for docx in docx_files:
            try:
                force_formatting(docx)
                print(f"  OK: {os.path.basename(docx)}")
            except Exception as e:
                print(f"  ERR: {os.path.basename(docx)}: {e}")
    except ImportError:
        print("  跳过（需要 python-docx: pip install python-docx lxml）")

    print()
    print(f"完成！{ok_count}/{len(md_files)} 个文件已转换")
    print(f"输出目录: {output_dir}/")


if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = sys.argv[2] if len(sys.argv) > 2 else None
    convert_all(inp, out)
