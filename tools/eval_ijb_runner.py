#!/usr/bin/env python3
"""
IJB-B / IJB-C 评估 runner。
由 eval_service.py 以子进程方式调用。

backbone 和权重加载复用项目的 FaceEmbeddingModel（backbones.iresnet）。
评估逻辑与 FaceRec_plus/evaluate_IJB.py 完全一致（landmark对齐/flip/归一化等）。

用法：
    python tools/eval_ijb_runner.py <config_json_path>

config.json：
{
    "project_root": "E:/RecognitionSystem",
    "weights_path": "path/to/model.pt",
    "backbone": "iresnet50",
    "image_path": "path/to/IJB_release/IJBB",
    "target": "IJBB",
    "batch_size": 512,
    "use_norm_score": true,
    "use_detector_score": true,
    "use_flip_test": true,
    "result_dir": "path/to/save",
    "output_json": "path/to/result.json"
}
"""

from __future__ import annotations

import json
import os
import sys
import timeit
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: eval_ijb_runner.py <config.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        cfg = json.load(f)

    project_root = cfg["project_root"]
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    import cv2
    import numpy as np
    import pandas as pd
    import sklearn.preprocessing
    import torch
    from skimage import transform as trans
    from sklearn.metrics import auc, roc_curve

    from apps.recognition_system.core.model import FaceEmbeddingModel

    weights_path = cfg["weights_path"]
    backbone_name = cfg["backbone"]
    image_path_root = Path(cfg["image_path"])
    target = cfg["target"]
    assert target in ("IJBB", "IJBC"), f"target 必须为 IJBB 或 IJBC"
    batch_size = int(cfg.get("batch_size", 512))
    use_norm_score = bool(cfg.get("use_norm_score", True))
    use_detector_score = bool(cfg.get("use_detector_score", True))
    use_flip_test = bool(cfg.get("use_flip_test", True))
    result_dir = cfg.get("result_dir") or str(image_path_root.parent)
    output_json = cfg["output_json"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[IJB] 设备: {device}", flush=True)

    # 加载模型（复用 FaceEmbeddingModel，已正确处理 state_dict_backbone / module. 前缀）
    print(f"[IJB] 加载 {backbone_name} 权重: {Path(weights_path).name}", flush=True)
    face_model = FaceEmbeddingModel(
        weights_path=weights_path,
        model_name=backbone_name,
        img_size=112,
        device=device,
    )
    backbone_net = face_model.net
    backbone_net.eval()

    # ----------------------------------------------------------------
    # Embedding 类 —— 与 evaluate_IJB.py 完全一致，设备动态化
    # ----------------------------------------------------------------

    def _emit(phase: str, percent: float, msg: str = ""):
        """输出结构化进度行供 eval_service 解析。"""
        import json as _json
        payload = {"phase": phase, "percent": round(percent, 1), "msg": msg}
        print(f"__PROGRESS__ {_json.dumps(payload, ensure_ascii=False)}", flush=True)
    class Embedding:
        _src = np.array(
            [[30.2946, 51.6963],
             [65.5318, 51.5014],
             [48.0252, 71.7366],
             [33.5493, 92.3655],
             [62.7299, 92.2041]],
            dtype=np.float32,
        )
        _src[:, 0] += 8.0

        def __init__(self, net, batch_size_):
            self.image_size = (112, 112)
            # 多 GPU 才用 DataParallel；单 GPU/CPU 直接使用原始模型，避免不必要的调度开销
            if torch.cuda.device_count() > 1:
                self.model = torch.nn.DataParallel(net)
            else:
                self.model = net
            self.model.eval()
            self.batch_size = batch_size_
            self.src = self.__class__._src

        def get(self, rimg, landmark):
            """landmark 对齐 + BGR→RGB + flip，与原版完全一致。"""
            assert landmark.shape[0] in (5, 68) and landmark.shape[1] == 2
            if landmark.shape[0] == 68:
                lm5 = np.zeros((5, 2), dtype=np.float32)
                lm5[0] = (landmark[36] + landmark[39]) / 2
                lm5[1] = (landmark[42] + landmark[45]) / 2
                lm5[2] = landmark[30]
                lm5[3] = landmark[48]
                lm5[4] = landmark[54]
            else:
                lm5 = landmark
            tform = trans.SimilarityTransform()
            tform.estimate(lm5, self.src)
            M = tform.params[0:2, :]
            img = cv2.warpAffine(rimg, M, (112, 112), borderValue=0.0)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_flip = np.fliplr(img)
            img = np.transpose(img, (2, 0, 1))
            img_flip = np.transpose(img_flip, (2, 0, 1))
            blob = np.zeros((2, 3, 112, 112), dtype=np.uint8)
            blob[0] = img
            blob[1] = img_flip
            return blob

        @torch.no_grad()
        def forward_db(self, batch_data):
            """uint8 [0,255] → [-1,1] 归一化 → 推理 → concat flip，与原版完全一致。"""
            imgs = torch.Tensor(batch_data).to(device)
            imgs.div_(255).sub_(0.5).div_(0.5)
            feat = self.model(imgs)
            feat = feat.reshape([self.batch_size, 2 * feat.shape[1]])
            return feat.cpu().numpy()

    # ----------------------------------------------------------------
    # 辅助函数 —— 与 evaluate_IJB.py 完全一致
    # ----------------------------------------------------------------
    def read_template_media_list(path):
        m = pd.read_csv(path, sep=" ", header=None).values
        return m[:, 1].astype(np.int32), m[:, 2].astype(np.int32)

    def read_template_pair_list(path):
        p = pd.read_csv(path, sep=" ", header=None).values
        return p[:, 0].astype(np.int32), p[:, 1].astype(np.int32), p[:, 2].astype(np.int32)

    def get_image_feature(img_path, files_list):
        n = len(files_list)
        rare_size = n % batch_size
        faceness_scores = []
        batch_idx = 0
        img_feats = np.empty((n, 1024), dtype=np.float32)
        embedding = Embedding(backbone_net, batch_size)
        batch_data = np.empty((2 * batch_size, 3, 112, 112))
        total_batches = n // batch_size + (1 if rare_size else 0)

        print(f"[IJB] 提取特征，共 {n} 张图片...", flush=True)
        _emit("extract_features", 10.0, f"开始提取特征 (共 {n} 张)")

        for img_index, each_line in enumerate(files_list[: n - rare_size]):
            parts = each_line.strip().split(" ")
            img = cv2.imread(os.path.join(img_path, parts[0]))
            lmk = np.array([float(x) for x in parts[1:-1]], dtype=np.float32).reshape(5, 2)
            blob = embedding.get(img, lmk)
            offset = 2 * (img_index - batch_idx * batch_size)
            batch_data[offset] = blob[0]
            batch_data[offset + 1] = blob[1]
            if (img_index + 1) % batch_size == 0:
                img_feats[batch_idx * batch_size: (batch_idx + 1) * batch_size] = \
                    embedding.forward_db(batch_data)
                batch_idx += 1
                pct = 10.0 + 55.0 * batch_idx / total_batches
                _emit("extract_features", pct,
                      f"提取特征 批次 {batch_idx}/{total_batches} ({batch_idx * batch_size}/{n})")
            faceness_scores.append(parts[-1])

        if rare_size > 0:
            emb_rare = Embedding(backbone_net, rare_size)
            bd_rare = np.empty((2 * rare_size, 3, 112, 112))
            for img_index, each_line in enumerate(files_list[n - rare_size:]):
                parts = each_line.strip().split(" ")
                img = cv2.imread(os.path.join(img_path, parts[0]))
                lmk = np.array([float(x) for x in parts[1:-1]], dtype=np.float32).reshape(5, 2)
                blob = emb_rare.get(img, lmk)
                bd_rare[2 * img_index] = blob[0]
                bd_rare[2 * img_index + 1] = blob[1]
                if (img_index + 1) % rare_size == 0:
                    img_feats[n - rare_size:] = emb_rare.forward_db(bd_rare)
                    _emit("extract_features", 65.0, f"提取剩余 {rare_size} 张")
                faceness_scores.append(parts[-1])

        _emit("extract_features", 68.0, "特征提取完成")
        return img_feats, np.array(faceness_scores, dtype=np.float32)

    def image2template_feature(img_feats, templates, medias):
        unique_templates = np.unique(templates)
        total = len(unique_templates)
        template_feats = np.zeros((total, img_feats.shape[1]))
        for i, uqt in enumerate(unique_templates):
            if i % max(1, total // 20) == 0:
                pct = 70.0 + 15.0 * i / total
                _emit("aggregate", pct, f"聚合模板 {i}/{total}")
            ind_t = np.where(templates == uqt)[0]
            face_feats = img_feats[ind_t]
            face_medias = medias[ind_t]
            unique_medias, counts = np.unique(face_medias, return_counts=True)
            media_feats = []
            for u, ct in zip(unique_medias, counts):
                ind_m = np.where(face_medias == u)[0]
                media_feats.append(
                    face_feats[ind_m] if ct == 1
                    else np.mean(face_feats[ind_m], axis=0, keepdims=True)
                )
            template_feats[i] = np.sum(np.array(media_feats), axis=0)
        _emit("aggregate", 85.0, "模板聚合完成")
        return sklearn.preprocessing.normalize(template_feats), unique_templates

    def verification_score(template_norm_feats, unique_templates, p1, p2):
        template2id = np.zeros((max(unique_templates) + 1, 1), dtype=int)
        for i, uqt in enumerate(unique_templates):
            template2id[uqt] = i
        score = np.zeros(len(p1))
        bsz = 100000
        for s in [np.arange(len(p1))[i: i + bsz] for i in range(0, len(p1), bsz)]:
            f1 = template_norm_feats[template2id[p1[s]]]
            f2 = template_norm_feats[template2id[p2[s]]]
            score[s] = np.sum(f1 * f2, -1).flatten()
        return score

    # ----------------------------------------------------------------
    # 主流程
    # ----------------------------------------------------------------
    meta_dir = str(image_path_root / "meta")
    img_path = str(image_path_root / "loose_crop")

    print("[IJB] 读取 meta 文件...", flush=True)
    _emit("init", 3.0, "读取 meta 文件...")
    templates, medias = read_template_media_list(
        os.path.join(meta_dir, f"{target.lower()}_face_tid_mid.txt"))
    p1, p2, label = read_template_pair_list(
        os.path.join(meta_dir, f"{target.lower()}_template_pair_label.txt"))
    with open(os.path.join(meta_dir, f"{target.lower()}_name_5pts_score.txt"), encoding="utf-8") as f:
        files_list = f.readlines()

    t0 = timeit.default_timer()
    _emit("extract_features", 8.0, "开始特征提取...")
    img_feats, faceness_scores = get_image_feature(img_path, files_list)
    print(f"[IJB] 特征提取耗时: {timeit.default_timer() - t0:.1f}s，shape={img_feats.shape}", flush=True)

    _emit("aggregate", 68.0, "处理 flip/norm/detector score...")
    # flip test / norm / detector score —— 与原版完全一致
    if use_flip_test:
        img_input_feats = img_feats[:, :img_feats.shape[1]//2] + img_feats[:, img_feats.shape[1]//2:]
    else:
        img_input_feats = img_feats[:, :img_feats.shape[1]//2]

    if not use_norm_score:
        img_input_feats = img_input_feats / np.sqrt(
            np.sum(img_input_feats ** 2, -1, keepdims=True))

    if use_detector_score:
        img_input_feats = img_input_feats * faceness_scores[:, np.newaxis]

    print("[IJB] 聚合模板特征...", flush=True)
    _emit("aggregate", 70.0, "开始模板聚合...")
    template_norm_feats, unique_templates = image2template_feature(
        img_input_feats, templates, medias)

    print("[IJB] 计算验证分数...", flush=True)
    _emit("score", 87.0, "计算验证分数...")
    score = verification_score(template_norm_feats, unique_templates, p1, p2)

    _emit("roc", 93.0, "计算 ROC / TAR@FAR...")
    # ROC / TAR@FAR —— 与原版完全一致
    fpr_arr, tpr_arr, _ = roc_curve(label, score)
    roc_auc_val = auc(fpr_arr, tpr_arr)
    fpr_arr = np.flipud(fpr_arr)
    tpr_arr = np.flipud(tpr_arr)

    x_labels = [10**-6, 10**-5, 10**-4, 10**-3, 10**-2, 10**-1]
    tpr_values = {}
    for x in x_labels:
        _, idx = min(zip(abs(fpr_arr - x), range(len(fpr_arr))))
        tpr_values[str(x)] = round(float(tpr_arr[idx]) * 100, 4)

    print(f"\n[IJB] {target} AUC: {roc_auc_val * 100:.4f}%", flush=True)
    for far, tv in tpr_values.items():
        print(f"  TAR={tv:.2f}% @ FAR={far}", flush=True)

    # 保存评分文件
    os.makedirs(result_dir, exist_ok=True)
    score_file = os.path.join(result_dir, f"{target.lower()}_{Path(weights_path).stem}.npy")
    np.save(score_file, score)

    output = {
        "type": "ijb_evaluation",
        "model": backbone_name,
        "weights": Path(weights_path).name,
        "target": target,
        "roc_auc": round(float(roc_auc_val) * 100, 4),
        "tpr_values": tpr_values,
        "x_labels": [str(x) for x in x_labels],
        "fpr": fpr_arr[::max(1, len(fpr_arr)//500)].tolist(),
        "tpr": tpr_arr[::max(1, len(tpr_arr)//500)].tolist(),
        "score_file": score_file,
    }

    _emit("done", 100.0, "评估完成")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[IJB] 结果已写入 {output_json}", flush=True)


if __name__ == "__main__":
    main()
