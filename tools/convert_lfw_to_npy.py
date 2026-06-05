#!/usr/bin/env python3
"""
将 bcolz 格式的 LFW 风格人脸验证数据集转换为 numpy .npy 格式。

在**有 bcolz 的训练服务器**上运行一次，然后将输出目录复制到 Windows 本地即可。

用法：
    python tools/convert_lfw_to_npy.py \
        --data_root /root/autodl-tmp/simple_sample \
        --out_root  ./lfw_npy \
        --datasets  lfw calfw cplfw agedb_30 cfp_fp vgg2_fp

输出结构（与本系统的格式 B 完全一致）：
    <out_root>/
        lfw.npy             shape=[N, 3, 112, 112]  dtype=uint8
        lfw_list.npy        shape=[N/2]              dtype=bool
        calfw.npy
        calfw_list.npy
        ...

注意：
  - bcolz 数组的通道顺序为 BGR，本脚本保持原始顺序写出（系统推理时会自动处理）。
  - .npy 文件约占 bcolz 目录相同大小，LFW (~12000张) 约 480 MB。
"""

import argparse
import sys
from pathlib import Path

import numpy as np

DEFAULT_DATASETS = ["lfw", "calfw", "cplfw", "agedb_30", "cfp_fp", "vgg2_fp"]


def convert_one(data_root: Path, out_root: Path, name: str) -> bool:
    bcolz_dir = data_root / name
    labels_src = data_root / f"{name}_list.npy"

    if not bcolz_dir.exists():
        print(f"  [SKIP] bcolz 目录不存在: {bcolz_dir}")
        return False
    if not labels_src.exists():
        print(f"  [SKIP] 标签文件不存在: {labels_src}")
        return False

    try:
        import bcolz
    except ImportError:
        print("ERROR: 未安装 bcolz，请先 pip install bcolz")
        sys.exit(1)

    print(f"  [{name}] 读取 bcolz 数组...")
    arr = bcolz.carray(rootdir=str(bcolz_dir), mode="r")[:]   # shape [N, 3, 112, 112]
    # 保留原始 dtype（通常为 float32，值约在 [-1, 1]），不转 uint8，否则会损失精度。

    labels = np.load(str(labels_src))

    out_root.mkdir(parents=True, exist_ok=True)
    npy_out = out_root / f"{name}.npy"
    lbl_out = out_root / f"{name}_list.npy"

    print(f"  [{name}] 保存 {npy_out}  shape={arr.shape}  size={arr.nbytes / 1e6:.1f} MB")
    np.save(str(npy_out), arr)
    np.save(str(lbl_out), labels)
    print(f"  [{name}] 保存 {lbl_out}  shape={labels.shape}")
    return True


def main():
    parser = argparse.ArgumentParser(description="bcolz → numpy 格式转换工具")
    parser.add_argument(
        "--data_root", required=True,
        help="bcolz 数据集根目录（包含 lfw/, lfw_list.npy 等）",
    )
    parser.add_argument(
        "--out_root", default="./lfw_npy",
        help="输出目录（默认 ./lfw_npy）",
    )
    parser.add_argument(
        "--datasets", nargs="+", default=DEFAULT_DATASETS,
        help=f"要转换的数据集名称（默认: {' '.join(DEFAULT_DATASETS)}）",
    )
    args = parser.parse_args()

    data_root = Path(args.data_root)
    out_root = Path(args.out_root)

    print(f"\n数据源: {data_root}")
    print(f"输出目录: {out_root}")
    print(f"数据集: {args.datasets}\n")

    success, skipped = 0, 0
    for name in args.datasets:
        if convert_one(data_root, out_root, name):
            success += 1
        else:
            skipped += 1

    print(f"\n完成: {success} 个数据集转换成功，{skipped} 个跳过。")
    print(f"请将 '{out_root}' 目录复制到 Windows 本地，在评估界面填入该路径即可。")


if __name__ == "__main__":
    main()
