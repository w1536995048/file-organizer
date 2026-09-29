#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文件整理工具 file-organizer

扫描指定目录，按文件类型自动分类归档，支持试运行模式与操作日志（可撤销）。

用法：
    python organizer.py ~/Downloads --dry-run      # 先预览，不实际移动
    python organizer.py ~/Downloads                # 正式整理
    python organizer.py ~/Downloads --by-date      # 再按日期分子目录
    python organizer.py --undo                     # 撤销上一次整理
"""

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path

# 文件类型映射：类别 -> 后缀列表
CATEGORIES = {
    "图片": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".heic"},
    "视频": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
    "音频": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "文档": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
             ".txt", ".md", ".csv", ".rtf"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "程序": {".exe", ".msi", ".dmg", ".apk", ".app"},
    "代码": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs", ".html", ".css"},
}

LOG_FILE = Path.home() / ".file_organizer_log.csv"


def category_of(path: Path) -> str:
    """返回文件所属分类，未知类型归入'其他'。"""
    suffix = path.suffix.lower()
    for name, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return name
    return "其他"


def unique_dest(dest_dir: Path, filename: str) -> Path:
    """目标已存在同名文件时自动加序号，避免覆盖。"""
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem, suffix = Path(filename).stem, Path(filename).suffix
    i = 1
    while True:
        candidate = dest_dir / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def organize(target: Path, dry_run: bool = False, by_date: bool = False):
    """整理目标目录下的一级文件（不递归子目录）。"""
    if not target.is_dir():
        print(f"错误：{target} 不是有效目录")
        return

    moves = []  # (源, 目标)
    for item in sorted(target.iterdir()):
        if not item.is_file() or item.name.startswith("."):
            continue
        cat = category_of(item)
        dest_dir = target / cat
        if by_date:
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            dest_dir = dest_dir / mtime.strftime("%Y-%m")
        dest = unique_dest(dest_dir, item.name)
        moves.append((item, dest))

    if not moves:
        print("没有需要整理的文件。")
        return

    # 打印预览
    print(f"{'[试运行] ' if dry_run else ''}共 {len(moves)} 个文件：")
    for src, dest in moves:
        print(f"  {src.name}  ->  {dest.parent.name}/{dest.name}")

    if dry_run:
        print("\n试运行模式，未实际移动。如确认请去掉 --dry-run。")
        return

    # 执行并记录日志（用于撤销）
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for src, dest in moves:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            writer.writerow([datetime.now().isoformat(), str(dest), str(src)])
    print(f"\n整理完成，操作已记录（{LOG_FILE}），可用 --undo 撤销。")


def undo():
    """撤销最近一次整理操作。"""
    if not LOG_FILE.exists():
        print("没有可撤销的操作记录。")
        return
    rows = list(csv.reader(open(LOG_FILE, encoding="utf-8")))
    if not rows:
        print("没有可撤销的操作记录。")
        return

    last_time = rows[-1][0][:19]  # 按秒级时间戳分组
    batch = [r for r in rows if r[0][:19] == last_time]
    for _, dest, src in batch:
        dest_p, src_p = Path(dest), Path(src)
        if dest_p.exists():
            src_p.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest_p), str(unique_dest(src_p.parent, src_p.name)))
            print(f"  已还原：{dest_p.name}")
    # 从日志中移除已撤销批次
    remaining = [r for r in rows if r[0][:19] != last_time]
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(remaining)
    print(f"已撤销 {len(batch)} 个文件的移动。")


def main():
    parser = argparse.ArgumentParser(description="智能文件整理工具")
    parser.add_argument("directory", nargs="?", help="要整理的目录")
    parser.add_argument("--dry-run", action="store_true", help="试运行，只预览不移动")
    parser.add_argument("--by-date", action="store_true", help="分类下再按年月分子目录")
    parser.add_argument("--undo", action="store_true", help="撤销上一次整理")
    args = parser.parse_args()

    if args.undo:
        undo()
    elif args.directory:
        organize(Path(args.directory).expanduser(), args.dry_run, args.by_date)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
