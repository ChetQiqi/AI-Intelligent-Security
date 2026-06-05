#!/usr/bin/env python3
"""
LFW-style 验证评估 runner。
由 eval_service.py 以子进程方式调用。

backbone 和权重加载直接复用项目的 FaceEmbeddingModel（backbones.iresnet）。
评估逻辑与 FaceRec_plus/verification.py 完全一致。

用法：
    python tools/eval_lfw_runner.py <config_json_path>

config.json：
{
    "project_root": "E:/RecognitionSystem",
    "weights_path": "path/to/model.pt",
    "backbone": "iresnet50",
    "data_root": "path/to/bcolz_root",
    "datasets": ["lfw", "calfw", "cplfw", "agedb_30", "cfp_fp", "vgg2_fp"],
    "batch_size": 512,
    "output_json": "path/to/result.json"
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: eval_lfw_runner.py <config.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        cfg = json.load(f)

    project_root = cfg["project_root"]
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    import numpy as np
    import torch
    import bcolz

    # 复用项目自身的模型加载（已正确处理 state_dict_backbone 和 module. 前缀）
    from apps.recognition_system.core.model import FaceEmbeddingModel

    weights_path = cfg["weights_path"]
    backbone_name = cfg["backbone"]
    data_root = Path(cfg["data_root"])
    datasets: list = cfg["datasets"]
    batch_size: int = int(cfg.get("batch_size", 512))
    output_json = cfg["output_json"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[LFW] 设备: {device}", flush=True)

    # 加载模型
    print(f"[LFW] 加载 {backbone_name} 权重: {Path(weights_path).name}", flush=True)
    face_model = FaceEmbeddingModel(
        weights_path=weights_path,
        model_name=backbone_name,
        img_size=112,
        device=device,
    )
    net = face_model.net  # 原始 nn.Module
    net.eval()

    # 探测 embedding 维度
    with torch.no_grad():
        embedding_size = net(torch.zeros(1, 3, 112, 112).to(face_model.device)).shape[1]
    print(f"[LFW] embedding_size = {embedding_size}", flush=True)

    # ----------------------------------------------------------------
    # 以下与 verification.py 完全一致（一字不差）
    # ----------------------------------------------------------------

    def calculate_features(batch_imgs, backbone, dev):
        return backbone(batch_imgs.to(dev)).cpu()

    def calculate_accuracy(features, is_same, dev):
        m = features.shape[0] // 2
        features1 = torch.tensor(features[0::2]).to(dev)
        features2 = torch.tensor(features[1::2]).to(dev)
        cosine = torch.sum(features1 * features2, dim=1) / (
            torch.norm(features1, dim=1) * torch.norm(features2, dim=1)
        )
        labels = torch.tensor(is_same, dtype=torch.bool).to(dev)

        # 向量化：将所有阈值一次性广播比较，避免 O(m²) Python 循环
        # cosine: (m,)  thresholds: (m,1)  → 广播后 (m, m)，每列是一个阈值下的预测
        thresholds = cosine.unsqueeze(1)                        # (m, 1)
        preds = cosine.unsqueeze(0) > thresholds               # (m, m) bool
        correct = (preds == labels.unsqueeze(0)).float().sum(dim=1)  # (m,)
        best_idx = correct.argmax()
        return cosine[best_idx], correct[best_idx] / m

    def evaluate_dataset(testset: str) -> dict:
        carray_path = data_root / testset
        npy_path = data_root / f"{testset}.npy"
        labels_path = data_root / f"{testset}_list.npy"

        # 优先 bcolz，找不到则尝试 .npy
        if carray_path.exists() and carray_path.is_dir():
            try:
                carray = bcolz.carray(rootdir=str(carray_path), mode="r")
            except Exception as e:
                return {"acc": None, "threshold": None, "num_pairs": 0, "error": str(e)}
        elif npy_path.exists():
            carray = np.load(str(npy_path), mmap_mode="r")
        else:
            return {
                "acc": None, "threshold": None, "num_pairs": 0,
                "error": f"找不到: {carray_path} 或 {npy_path}",
            }

        if not labels_path.exists():
            return {
                "acc": None, "threshold": None, "num_pairs": 0,
                "error": f"标签文件不存在: {labels_path}",
            }

        is_same = np.load(str(labels_path))

        # ---- 与 verification.py::evaluate() 完全一致 ----
        idx = 0
        n = len(carray)
        features = np.zeros([n, embedding_size])
        with torch.no_grad():
            while idx + batch_size <= n:
                # BGR→RGB，直接 torch.tensor，不做任何归一化（与原版完全一致）
                raw = np.array(carray[idx: idx + batch_size])[:, [2, 1, 0], :, :]
                batch = torch.from_numpy(raw)
                features[idx: idx + batch_size] = calculate_features(batch, net, device)
                idx += batch_size
            if idx < n:
                raw = np.array(carray[idx:])[:, [2, 1, 0], :, :]
                tail = calculate_features(torch.from_numpy(raw), net, device)
                features[idx:] = tail[: n - idx]

        th, acc = calculate_accuracy(features, is_same, device)
        acc = acc.item() if isinstance(acc, torch.Tensor) else float(acc)
        th = th.item() if isinstance(th, torch.Tensor) else float(th)

        print(f"  {testset}: acc={acc:.4f}, th={th:.4f}", flush=True)
        return {"acc": round(acc, 4), "threshold": round(th, 4), "num_pairs": n // 2}

    # ----------------------------------------------------------------
    # 遍历所有数据集（附带结构化进度输出供 service 解析）
    # ----------------------------------------------------------------
    def emit_progress(done: int, total: int, current: str, datasets_done: list, partial: dict):
        import json as _json
        payload = {
            "done": done,
            "total": total,
            "current": current,
            "datasets_done": datasets_done,
            "partial": partial,          # 已完成数据集的结果 {name: {acc, threshold}}
            "percent": round(5 + 90 * done / total, 1),
        }
        print(f"__PROGRESS__ {_json.dumps(payload, ensure_ascii=False)}", flush=True)

    results = {}
    total_ds = len(datasets)
    for idx, ds in enumerate(datasets):
        emit_progress(idx, total_ds, ds, list(results.keys()),
                      {k: {"acc": v["acc"], "threshold": v.get("threshold")} for k, v in results.items()})
        print(f"\n[LFW] 评估 {ds} ...", flush=True)
        results[ds] = evaluate_dataset(ds)

    # 完成
    emit_progress(total_ds, total_ds, "", list(results.keys()),
                  {k: {"acc": v["acc"], "threshold": v.get("threshold")} for k, v in results.items()})

    valid_accs = [v["acc"] for v in results.values() if v.get("acc") is not None]
    output = {
        "type": "lfw_verification",
        "datasets": results,
        "mean_accuracy": round(sum(valid_accs) / len(valid_accs), 4) if valid_accs else None,
        "model": backbone_name,
        "weights": Path(weights_path).name,
        "device": device,
        "embedding_size": embedding_size,
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[LFW] 完成。均值准确率: {output['mean_accuracy']}", flush=True)


if __name__ == "__main__":
    main()
