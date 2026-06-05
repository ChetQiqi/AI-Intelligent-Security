#!/usr/bin/env python3
"""
模型权重 & 数据库下载工具
========================

用法：
    python download_weights.py              # 交互式菜单
    python download_weights.py --all        # 下载全部
    python download_weights.py --model      # 仅下载识别模型
    python download_weights.py --db         # 仅下载示例数据库

模型来源：
    iResNet50 预训练权重（167 MB）
    需要手动放置到 weights/model_best.pt

由于模型权重文件较大（总计 >10 GB），建议通过以下方式获取：

1. 从网盘下载（推荐）
   链接: [待填写]
   下载后解压到项目根目录

2. 从 HuggingFace 下载
   部分模型可从 HuggingFace 自动下载

3. 使用自己的预训练权重
   将 .pt 文件放到 weights/ 目录即可
"""

import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
WEIGHTS_DIR = PROJECT_ROOT / "weights"
BENCHMARK_DIR = PROJECT_ROOT / "benchmark"


def check_existing() -> dict:
    """检查已有文件"""
    status = {
        "model": (WEIGHTS_DIR / "model_best.pt").exists(),
        "hf_cache": (WEIGHTS_DIR / "hf_cache").exists(),
        "db": (BENCHMARK_DIR / "YTF_100p.db").exists(),
    }
    return status


def print_status(status: dict):
    """打印状态"""
    print("\n" + "=" * 60)
    print("  当前状态 (Current Status)")
    print("=" * 60)
    items = [
        ("识别模型 (model_best.pt)", status["model"]),
        ("HuggingFace 缓存", status["hf_cache"]),
        ("示例数据库 (YTF_100p.db)", status["db"]),
    ]
    for name, ok in items:
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {name}")
    print("=" * 60)


def download_from_huggingface():
    """尝试从 HuggingFace 下载 PhotoMaker 模型"""
    print("\n[INFO] 正在从 HuggingFace 下载 PhotoMaker 模型...")
    print("[INFO] 缓存目录: {}".format(WEIGHTS_DIR / "hf_cache"))

    os.environ["HF_HUB_CACHE"] = str(WEIGHTS_DIR / "hf_cache")

    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            "TencentARC/PhotoMaker",
            cache_dir=str(WEIGHTS_DIR / "hf_cache"),
            resume_download=True,
        )
        print("[OK] PhotoMaker 模型下载完成！")
    except ImportError:
        print("[SKIP] huggingface_hub 未安装，跳过下载")
        print("       安装: pip install huggingface_hub")
    except Exception as e:
        print(f"[WARN] 下载失败: {e}")
        print("       你可以手动下载后放到 weights/hf_cache/")


def create_demo_db():
    """创建空的示例数据库"""
    print("\n[INFO] 创建示例数据库...")
    try:
        from apps.recognition_system.core.feature_db import FeatureDatabase

        db_path = BENCHMARK_DIR / "YTF_100p.db"
        BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

        db = FeatureDatabase(str(db_path))
        db.create_tables()
        db.close()

        print(f"[OK] 空数据库已创建: {db_path}")
        print("   使用 'python run.py manager' 添加人脸")
    except Exception as e:
        print(f"[WARN] 创建数据库失败: {e}")


def print_manual_instructions():
    """打印手动下载说明"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          模型权重获取指南 (Manual Setup)                  ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📦 必需 (Required):                                     ║
║     model_best.pt     → 放到 weights/                    ║
║     (iResNet50, ~167 MB)                                 ║
║                                                          ║
║  📦 可选 (Optional):                                     ║
║     HuggingFace 缓存  → 自动下载到 weights/hf_cache/     ║
║     (AI 肖像生成需要, ~10 GB)                             ║
║                                                          ║
║  📦 数据库:                                              ║
║     YTF_100p.db       → 放到 benchmark/                  ║
║     (或使用 'python download_weights.py --db' 创建空库)   ║
║                                                          ║
║  💡 获取方式:                                            ║
║     1. 网盘下载 (推荐) → 链接: [待填写]                  ║
║     2. 自己训练 → 使用 iResNet50 + MS1MV2                ║
║     3. HuggingFace → 仅 PhotoMaker/SDXL 可自动下载       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(
        description="模型权重 & 数据库下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python download_weights.py              # 交互式菜单
  python download_weights.py --status     # 查看当前状态
  python download_weights.py --hf         # 下载 HuggingFace 模型
  python download_weights.py --db         # 创建空数据库
        """,
    )
    parser.add_argument("--all", action="store_true", help="下载所有可自动下载的内容")
    parser.add_argument("--model", action="store_true", help="下载识别模型")
    parser.add_argument("--hf", action="store_true", help="下载 HuggingFace 模型")
    parser.add_argument("--db", action="store_true", help="创建空的示例数据库")
    parser.add_argument("--status", action="store_true", help="仅查看状态")
    args = parser.parse_args()

    # 确保目录存在
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

    status = check_existing()
    print_status(status)

    if args.status:
        return

    if args.all or args.hf:
        download_from_huggingface()

    if args.all or args.model:
        print("\n[INFO] 识别模型需要手动下载（文件较大）")
        print_manual_instructions()

    if args.all or args.db:
        create_demo_db()

    if not any([args.all, args.model, args.hf, args.db]):
        # 交互式菜单
        print("\n请选择操作:")
        print("  1. 下载 HuggingFace 模型 (PhotoMaker/SDXL)")
        print("  2. 创建空数据库")
        print("  3. 查看手动下载说明")
        print("  0. 退出")

        try:
            choice = input("\n选择 (0-3): ").strip()
            if choice == "1":
                download_from_huggingface()
            elif choice == "2":
                create_demo_db()
            elif choice == "3":
                print_manual_instructions()
            else:
                print("退出")
        except (EOFError, KeyboardInterrupt):
            print("\n退出")


if __name__ == "__main__":
    main()
