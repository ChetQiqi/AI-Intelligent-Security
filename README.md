# 🎯 RecognitionSystem — 人脸识别性能评估系统

基于深度学习的**实时摄像头人脸识别性能评估系统**，支持：
- 📷 30 秒摄像头实时人脸检测 + 识别
- ✍️ 手动标注识别结果
- 📊 自动生成性能指标（FPS、延迟、准确率）导出 CSV/JSON
- 🎨 AI 肖像生成（PhotoMaker + SDXL）
- 🔍 自适应阈值的 Open-set 人脸识别评估

---

## 📋 目录

- [环境要求](#-环境要求)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [功能说明](#-功能说明)
- [命令行使用](#-命令行使用)
- [AI 肖像生成（可选）](#-ai-肖像生成可选)
- [常见问题](#-常见问题)
- [论文实验](#-论文实验)

---

## 💻 环境要求

| 项目 | 要求 |
|------|------|
| **Python** | 3.10（推荐） |
| **CUDA** | 12.1+（NVIDIA GPU） |
| **GPU 显存** | ≥8 GB（AI 肖像功能） |
| **RAM** | ≥8 GB |
| **磁盘** | ≥15 GB（含模型权重） |
| **OS** | Windows 10/11、Linux、macOS |

---

## 🚀 快速开始

### 方式 1：一键安装（推荐）

**Windows：**
```batch
setup.bat
```

**Linux / macOS：**
```bash
bash setup.sh
```

### 方式 2：手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 下载模型权重

```bash
# 交互式下载工具
python download_weights.py

# 或创建空数据库
python download_weights.py --db
```

⚠️ **模型权重文件**（~167 MB）需要手动下载放到 `weights/` 目录：
- `weights/model_best.pt` — iResNet50 预训练权重（必需）
- 获取方式：网盘下载 / 自己训练

### 启动系统

```bash
# 启动完整 Web 界面
python run.py

# 或直接启动 Streamlit
streamlit run apps/recognition_system/streamlit_app.py

# 启动 FastAPI 后端（含 React 前端）
python run.py api
```

启动后访问：**http://localhost:8501**（Streamlit）

---

## 📁 项目结构

```
RecognitionSystem/
├── apps/recognition_system/       # 核心应用代码
│   ├── core/                      # 核心识别引擎
│   │   ├── operations.py          # 人脸检测+识别核心逻辑
│   │   ├── feature_db.py          # SQLite 特征数据库
│   │   ├── detector.py            # MTCNN 人脸检测器
│   │   ├── model.py               # iResNet50 识别模型
│   │   ├── matcher.py             # 特征匹配器
│   │   ├── tracker.py             # 人脸跟踪
│   │   ├── adaptive_threshold.py  # 自适应阈值框架 ⭐
│   │   └── metrics.py             # 性能指标计算
│   ├── api/                       # FastAPI 后端
│   ├── auth/                      # JWT 认证
│   ├── models/                    # ORM 数据模型
│   ├── repositories/              # 数据访问层
│   ├── services/                  # 业务逻辑层
│   │   └── portrait_service.py    # AI 肖像生成服务
│   ├── ui/                        # Streamlit 前端组件
│   ├── config.py                  # 系统配置
│   └── streamlit_app.py           # Streamlit 入口
│
├── frontend/                      # React 管理后台
│   ├── src/                       # React 源码
│   ├── package.json               # Node.js 依赖
│   └── vite.config.ts             # Vite 配置
│
├── scripts/                       # 实验与评估脚本
│   ├── extract_casia_features.py  # 从 CASIA-WebFace 提取特征
│   ├── prepare_open_set_optimized.py  # 准备开放集数据
│   └── compare_with_prepared_data.py  # 固定 vs 自适应对比
│
├── tools/                         # 分析工具集
│   ├── check_gpu.py               # GPU 检测
│   ├── check_db.py                # 数据库检查
│   ├── analyze_threshold_roc.py   # ROC 曲线分析
│   └── ...                        # 更多工具
│
├── weights/                       # 模型权重（需手动下载）
│   ├── model_best.pt              # iResNet50 (167 MB) ★ 必需
│   └── hf_cache/                  # HuggingFace 缓存（AI 肖像用，~10 GB）
│
├── benchmark/                     # 人脸数据库（需自行创建）
│   └── YTF_100p.db                # 示例数据库
│
├── run.py                         # 应用入口
├── download_weights.py            # 权重下载工具
├── requirements.txt               # Python 依赖
├── setup.bat                      # Windows 一键安装
├── setup.sh                       # Linux/macOS 一键安装
└── README.md                      # 本文件
```

---

## 📖 功能说明

### 1. 实时摄像头识别

通过 Streamlit Web 界面进行实时人脸检测与识别：

```bash
streamlit run apps/recognition_system/streamlit_app.py
```

功能：
- 30 秒摄像头采集
- 实时人脸检测 + 特征提取 + 身份匹配
- 自动记录性能指标（FPS、延迟）
- 支持手动标注修正
- 导出 CSV/JSON 评估报告

### 2. 人脸数据库管理

```bash
python run.py manager
```

- 注册新人脸（从图片/摄像头采集）
- 查看已注册人员列表
- 删除/更新人脸数据

### 3. 命令行识别

```bash
# 图片识别
python run.py recognize-image --image path/to/photo.jpg

# 摄像头实时识别
python run.py recognize-camera
```

### 4. Open-set 自适应阈值评估（论文创新点 ⭐）

每个已知身份独立计算阈值，比固定全局阈值更灵活：

```
τ_i = μ_i - 2σ_i

其中:
  μ_i = 该身份 genuine 样本的平均相似度
  σ_i = 该身份 genuine 样本的标准差
```

---

## ⌨️ 命令行使用

```bash
python run.py                  # 交互式菜单
python run.py api              # 启动 FastAPI (http://localhost:8000)
python run.py full             # 构建 React + 启动 API
python run.py dev              # API + React 热重载开发模式
python run.py streamlit        # 启动 Streamlit 界面
python run.py manager          # 人脸库管理
python run.py register <目录>  # 批量注册人脸
python run.py recognize-image <图片>  # 识别单张图片
python run.py recognize-camera # 摄像头实时识别
```

---

## 🎨 AI 肖像生成（可选）

使用 PhotoMaker + Stable Diffusion XL 生成不同风格的人像。

### 安装

```bash
# 1. 安装 PhotoMaker
pip install git+https://github.com/TencentARC/PhotoMaker.git

# 2. 安装精确版本的依赖
pip install diffusers==0.29.2 transformers==4.43.0 huggingface_hub==0.36.2

# 3. 下载 SDXL 模型（自动，~10 GB）
python download_weights.py --hf
```

### 支持风格

| 风格 | 说明 |
|------|------|
| 💼 商务照 | 专业商务形象 |
| 🪪 证件照 | 标准证件照 |
| 🏯 古风写真 | 中国古风风格 |
| 🎭 动漫风格 | 二次元动漫 |
| 🤖 赛博朋克 | 未来科幻风 |
| 📸 职业形象照 | 现代职业照 |

### 使用

启动系统后，在 Streamlit 侧边栏选择「AI 肖像生成」→ 选择人员 → 选择风格 → 生成。

⚠️ **要求**：GPU 显存 ≥ 8GB（SDXL fp16 ≈ 6.5GB）

---

## 🔧 配置

编辑 `apps/recognition_system/config.py` 修改系统参数：

```python
@dataclass(frozen=True)
class AppConfig:
    db_path: str = "benchmark/YTF_100p.db"       # 数据库路径
    weights_path: str = "weights/model_best.pt"   # 模型权重路径
    model_name: str = "iresnet50"                 # 识别模型
    detector_backend: str = "mtcnn"               # 检测器（MTCNN / yolo）
    recognition_threshold: float = 0.45           # 识别阈值
    detector_conf_threshold: float = 0.60         # 检测置信度
    device: str = "auto"                          # cuda / cpu / auto
```

也可以通过环境变量覆盖：
```bash
# Windows
set RECOGNITION_DB_PATH=D:\data\my_faces.db
# Linux/macOS
export RECOGNITION_DB_PATH=/data/my_faces.db
```

---

## 🐛 常见问题

### 1. 启动报错 `FileNotFoundError: model_best.pt`

**原因**：模型权重未下载

**解决**：
```bash
python download_weights.py
# 按提示手动下载 model_best.pt 到 weights/ 目录
```

### 2. MTCNN 速度太慢（~4 FPS）

**原因**：MTCNN 使用 TensorFlow 后端，CPU 推理较慢

**解决**：
- 方案 A：降低检测频率，每 2-3 帧处理一次
- 方案 B：替换为 YOLOv8-Face（5-10 倍提速）
- 方案 C：使用 GPU 加速 MTCNN

### 3. CUDA Out of Memory

**原因**：GPU 显存不足

**解决**：
- 使用 CPU 模式：`device = "cpu"` 在 config.py 中
- 降低 batch size
- 关闭 AI 肖像生成模块

### 4. `numpy` 版本冲突

**原因**：NumPy 2.x 不兼容

**解决**：
```bash
pip install "numpy<2.0"
```

### 5. AI 肖像生成报错

**原因**：diffusers / transformers / huggingface_hub 版本不匹配

**解决**：使用精确版本
```bash
pip install diffusers==0.29.2 transformers==4.43.0 huggingface_hub==0.36.2
```

---

## 🎓 论文实验

### 开放集识别评估流程

```bash
# Step 1: 提取 CASIA-WebFace 特征（~30 分钟）
python scripts/extract_casia_features.py \
    --dataset-path /path/to/CASIA-WebFace \
    --num-ids 200

# Step 2: 准备开放集数据（<1 分钟）
python scripts/prepare_open_set_optimized.py \
    --db casia \
    --num-known 100

# Step 3: 运行固定 vs 自适应对比评估（5-10 分钟）
python scripts/compare_with_prepared_data.py

# 查看结果
cat thesis_eval/fixed_vs_adaptive_results.csv
```

### 评估指标

| 指标 | 含义 | 说明 |
|------|------|------|
| **OSR** | Open-Set Recognition Rate | 总体开放集识别率 |
| **KCA** | Known Class Accuracy | 已知人分类准确率 |
| **UDR** | Unknown Detection Rate | 陌生人检测率 |
| **Precision** | — | 拒绝决策精确度 |
| **F1-Score** | — | 综合性能指标 |

### 数据库建议

| 场景 | 数据库 | 人数 | 特点 |
|------|--------|------|------|
| Web 演示 | YTF_100p.db | 103 | 轻量快速 |
| 论文实验 | CASIA_200_features.db | 200 | 多样性好 ⭐ 推荐 |
| 大规模验证 | YTF_allID_50features.db | 1595 | 数据量大 |

---

## 📦 导出与分发

```bash
# 创建干净的代码压缩包（不含大文件和临时文件）
git archive --format=zip --output=RecognitionSystem.zip HEAD

# 或使用 .gitignore 自动排除后打包
zip -r RecognitionSystem.zip . -x "*.pt" "*.pth" "*.db" "node_modules/*"
```

分发时附上：
1. 📦 代码压缩包（本仓库）
2. 🔗 模型权重下载链接（网盘 / HuggingFace）
3. 📄 README.md（本文件）

---

## 📝 许可证

本项目仅用于学术研究和学习目的。

---

## 📞 更多信息

- 项目记忆：[CLAUDE.md](CLAUDE.md)
- 详细结构：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- 后端功能总结：[docs/后端功能总结.md](docs/后端功能总结.md)

---

**项目状态**：✅ 核心功能完成 | **最后更新**：2026-06
