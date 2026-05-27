#!/usr/bin/env python3
"""PaddleOCR API wrapper — 调用 PaddleOCR API 完成 OCR 识别并保存为 Markdown + 图片。

配置:
  - 编辑下方 CONFIG 字典填入 token / url / mode
  - 环境变量 PADDLEOCR_TOKEN / PADDLEOCR_SYNC_URL / PADDLEOCR_ASYNC_URL / PADDLEOCR_MODE 可覆盖 CONFIG

API 模式:
  - sync  — 同步布局解析（layout-parsing），适合单页/小文件
  - async — 异步任务轮询（jobs API），适合多页 PDF
"""
import base64
import json
import os
import sys
import time
from io import BytesIO

import requests

# ============ 用户配置（改这里）============
CONFIG = {
    # API 模式: "sync" 或 "async"
    "mode": "async",

    # 同步模式 API（layout-parsing）
    "sync_url": "https://o1zbrbrcg0x0ybh1.aistudio-app.com/layout-parsing",

    # 异步模式 API（jobs）
    "async_url": "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs",

    # 你的 API Token（从 aistudio.baidu.com/paddleocr 获取）
    "token": "",

    # OCR 模型（异步模式使用）
    "model": "PaddleOCR-VL-1.5",

    # 可选参数
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,

    # 异步轮询超时（秒）
    "poll_warn_at": 300,    # 超过此时间打印警告（默认 5 分钟）
    "poll_max_wait": 1080,  # 超过此时间放弃并报错（默认 18 分钟）
}
# ============================================

# 环境变量覆盖（优先级高于 CONFIG，不侵入源码时使用）
CONFIG["token"] = os.getenv("PADDLEOCR_TOKEN", CONFIG["token"])
CONFIG["sync_url"] = os.getenv("PADDLEOCR_SYNC_URL", CONFIG["sync_url"])
CONFIG["async_url"] = os.getenv("PADDLEOCR_ASYNC_URL", CONFIG["async_url"])
CONFIG["mode"] = os.getenv("PADDLEOCR_MODE", CONFIG["mode"])


class OCRError(Exception):
    """OCR 操作失败。"""
    pass


def check_config():
    """检查配置是否完整。"""
    if not CONFIG["token"]:
        raise OCRError(
            "请先在 ocr_api.py 的 CONFIG 中填入你的 API Token，"
            "或设置环境变量 PADDLEOCR_TOKEN\n"
            "注册地址：https://aistudio.baidu.com/paddleocr"
        )


def detect_file_type(file_path):
    """根据扩展名判断文件类型。"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.pdf',):
        return 0  # PDF
    elif ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'):
        return 1  # Image
    else:
        print(f"警告：未知文件类型 {ext}，按 PDF 处理")
        return 0


def ocr_sync(file_path, output_dir="output"):
    """同步模式：layout-parsing API。"""
    check_config()

    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("ascii")

    file_type = detect_file_type(file_path)

    headers = {
        "Authorization": f"token {CONFIG['token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "file": file_data,
        "fileType": file_type,
        "useDocOrientationClassify": CONFIG["useDocOrientationClassify"],
        "useDocUnwarping": CONFIG["useDocUnwarping"],
        "useChartRecognition": CONFIG["useChartRecognition"],
    }

    print(f"[同步模式] 正在识别: {file_path}")
    for attempt in range(3):
        try:
            response = requests.post(CONFIG["sync_url"], json=payload, headers=headers, timeout=30)
            break
        except requests.ConnectionError:
            if attempt < 2:
                print(f"  网络连接失败，2秒后重试 ({attempt+1}/3)...")
                time.sleep(2)
            else:
                raise OCRError("网络连接失败，请检查网络连接")
        except requests.Timeout:
            if attempt < 2:
                print(f"  请求超时，2秒后重试 ({attempt+1}/3)...")
                time.sleep(2)
            else:
                raise OCRError("请求超时，服务可能繁忙，请稍后重试")

    if response.status_code != 200:
        raise OCRError(f"同步 API 错误 {response.status_code}: {response.text}")

    result = response.json()["result"]
    return save_results(result, output_dir)


def ocr_async(file_path, output_dir="output"):
    """异步模式：jobs API（支持 URL 和本地文件）。"""
    check_config()

    headers = {"Authorization": f"bearer {CONFIG['token']}"}
    optional = {
        "useDocOrientationClassify": CONFIG["useDocOrientationClassify"],
        "useDocUnwarping": CONFIG["useDocUnwarping"],
        "useChartRecognition": CONFIG["useChartRecognition"],
    }

    print(f"[异步模式] 正在提交任务: {file_path}")

    is_url = file_path.startswith("http")
    file_data = None
    if not is_url:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        with open(file_path, "rb") as f:
            file_data = f.read()

    for attempt in range(3):
        try:
            if is_url:
                headers["Content-Type"] = "application/json"
                payload = {
                    "fileUrl": file_path,
                    "model": CONFIG["model"],
                    "optionalPayload": optional
                }
                resp = requests.post(CONFIG["async_url"], json=payload,
                                     headers=headers, timeout=30)
            else:
                data = {
                    "model": CONFIG["model"],
                    "optionalPayload": json.dumps(optional)
                }
                resp = requests.post(CONFIG["async_url"], headers=headers,
                                     data=data, files={"file": BytesIO(file_data)},
                                     timeout=30)
            break
        except requests.ConnectionError:
            if attempt < 2:
                print(f"  网络连接失败，2秒后重试 ({attempt+1}/3)...")
                time.sleep(2)
            else:
                raise OCRError("网络连接失败，请检查网络连接")
        except requests.Timeout:
            if attempt < 2:
                print(f"  请求超时，2秒后重试 ({attempt+1}/3)...")
                time.sleep(2)
            else:
                raise OCRError("请求超时，服务可能繁忙，请稍后重试")

    if resp.status_code != 200:
        raise OCRError(f"异步 API 提交失败 {resp.status_code}: {resp.text}")

    job_id = resp.json()["data"]["jobId"]
    print(f"任务已提交，Job ID: {job_id}")
    print("正在轮询结果...")

    # 轮询任务状态
    jsonl_url = ""
    poll_start = time.time()
    warned = False
    while True:
        elapsed = time.time() - poll_start

        # 超时检查
        if elapsed >= CONFIG["poll_max_wait"]:
            mins = int(CONFIG["poll_max_wait"] // 60)
            raise OCRError(
                f"OCR 任务超时（已等待 {mins} 分钟）。"
                "可能是 API 服务繁忙，建议稍后重试或换用其他 OCR API。"
            )
        if not warned and elapsed >= CONFIG["poll_warn_at"]:
            mins = int(elapsed // 60)
            print(f"  ⚠ 已等待 {mins} 分钟，如持续无响应可按 Ctrl+C 中断后重试")
            warned = True

        job_resp = requests.get(f"{CONFIG['async_url']}/{job_id}", headers=headers, timeout=30)
        if job_resp.status_code != 200:
            raise OCRError(f"轮询任务状态失败 {job_resp.status_code}: {job_resp.text}")
        data = job_resp.json()["data"]
        state = data["state"]

        if state == "pending":
            print("  状态：等待中...")
        elif state == "running":
            try:
                prog = data["extractProgress"]
                print(f"  状态：处理中... {prog['extractedPages']}/{prog['totalPages']} 页")
            except KeyError:
                print("  状态：处理中...")
        elif state == "done":
            prog = data["extractProgress"]
            print(f"  完成！共处理 {prog['extractedPages']} 页")
            jsonl_url = data["resultUrl"]["jsonUrl"]
            break
        elif state == "failed":
            raise OCRError(f"OCR 任务失败: {data.get('errorMsg', '未知错误')}")

        time.sleep(5)

    # 下载并解析结果
    if jsonl_url:
        jsonl_resp = requests.get(jsonl_url, timeout=30)
        jsonl_resp.raise_for_status()
        lines = jsonl_resp.text.strip().split('\n')

        total_files = []
        page_num = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            result = json.loads(line)["result"]
            files = save_results(result, output_dir, prefix=f"page_{page_num}")
            total_files.extend(files)
            page_num += 1

        return total_files

    return []


def save_results(result, output_dir, prefix="doc"):
    """保存 OCR 结果为 markdown + 图片。"""
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []

    for i, res in enumerate(result.get("layoutParsingResults", [])):
        md_text = res["markdown"]["text"]
        md_filename = os.path.join(output_dir, f"{prefix}_{i}.md")

        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"  Markdown 已保存: {md_filename}")
        saved_files.append(md_filename)

        # 下载 markdown 中引用的图片
        for img_path, img_url in res["markdown"].get("images", {}).items():
            full_path = os.path.join(output_dir, img_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            img_bytes = requests.get(img_url, timeout=30).content
            with open(full_path, "wb") as f:
                f.write(img_bytes)
            print(f"  图片已保存: {full_path}")

        # 下载输出图片
        for img_name, img_url in res.get("outputImages", {}).items():
            img_resp = requests.get(img_url, timeout=30)
            if img_resp.status_code == 200:
                filename = os.path.join(output_dir, f"{img_name}_{i}.jpg")
                with open(filename, "wb") as f:
                    f.write(img_resp.content)
                print(f"  输出图片已保存: {filename}")

    return saved_files


def ocr(file_path, output_dir="output", mode=None):
    """统一入口：根据配置或参数选择模式。"""
    m = mode or CONFIG["mode"]
    if m == "sync":
        return ocr_sync(file_path, output_dir)
    elif m == "async":
        return ocr_async(file_path, output_dir)
    else:
        raise ValueError(f"未知模式 '{m}'，支持 'sync' 和 'async'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ocr_api.py <文件路径或URL> [输出目录] [sync|async]")
        print("")
        print("示例:")
        print("  python ocr_api.py textbook.pdf")
        print("  python ocr_api.py scan.jpg my_output")
        print("  python ocr_api.py https://example.com/doc.pdf output async")
        print("")
        print("配置：编辑 ocr_api.py 顶部 CONFIG 区，或设置环境变量 PADDLEOCR_TOKEN")
        sys.exit(0)

    path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "output"
    mode = sys.argv[3] if len(sys.argv) > 3 else None

    files = ocr(path, out, mode)
    print(f"\n完成！共生成 {len(files)} 个文件")
