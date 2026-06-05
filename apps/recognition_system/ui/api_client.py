from typing import Iterable, Optional, Tuple

import requests


class ApiClientError(RuntimeError):
    pass


class ApiClient:
    """Streamlit 前端专用 API Client。UI 不直接访问数据库、模型或识别函数。"""

    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        # 本地 API 不能走系统代理，否则 127.0.0.1 可能被代理拦截为 502。
        self.session.trust_env = False
    def set_token(self, token: Optional[str]):
        self.token = token

    def login(self, username: str, password: str):
        return self._request("POST", "/auth/login", json={"username": username, "password": password})

    def register(self, username: str, password: str, role: str = "viewer", email: Optional[str] = None):
        payload = {"username": username, "password": password, "role": role, "email": email}
        return self._request("POST", "/auth/register", json=payload)

    def me(self):
        return self._request("GET", "/auth/me")

    def health(self):
        return self._request("GET", "/health")

    def load_model(self):
        return self._request("POST", "/model/load", timeout=300)

    def switch_model(
        self,
        model_name: str,
        weights_path: Optional[str] = None,
        img_size: Optional[int] = None,
        device: Optional[str] = None,
    ):
        payload = {"model_name": model_name, "weights_path": weights_path, "img_size": img_size, "device": device}
        return self._request("POST", "/model/switch", json=payload, timeout=300)

    def list_model_weights(self):
        return self._request("GET", "/model/weights")

    def model_runtime(self):
        return self._request("GET", "/model/runtime")

    def upload_model(
        self,
        file_name: str,
        content: bytes,
        name: str,
        backbone: str = "iresnet50",
        embedding_size: int = 512,
    ):
        return self._request(
            "POST",
            "/models/upload",
            data={"name": name, "backbone": backbone, "embedding_size": embedding_size},
            files={"file": (file_name, content, "application/octet-stream")},
            timeout=300,
        )

    def list_models(self):
        return self._request("GET", "/models/list")

    def activate_model(self, model_id: int):
        return self._request("POST", f"/models/{model_id}/activate")

    def delete_model(self, model_id: int):
        return self._request("DELETE", f"/models/{model_id}")

    def developer_benchmark(self):
        return self._request("GET", "/developer/benchmark")

    def developer_model_eval(self, topn: int = 10):
        return self._request("POST", "/developer/model-eval", params={"topn": topn})

    # ------------------------------------------------------------------
    # 模型评估任务
    # ------------------------------------------------------------------

    def eval_submit_lfw(
        self,
        weights_path: str,
        backbone: str,
        data_root: str,
        datasets: Optional[list] = None,
        batch_size: int = 512,
    ):
        payload: dict = {
            "weights_path": weights_path,
            "backbone": backbone,
            "data_root": data_root,
            "batch_size": batch_size,
        }
        if datasets is not None:
            payload["datasets"] = datasets
        return self._request("POST", "/developer/eval/lfw", json=payload, timeout=30)

    def eval_submit_ijb(
        self,
        weights_path: str,
        backbone: str,
        image_path: str,
        target: str = "IJBB",
        batch_size: int = 512,
        use_norm_score: bool = True,
        use_detector_score: bool = True,
        use_flip_test: bool = True,
        result_dir: str = "",
    ):
        return self._request(
            "POST",
            "/developer/eval/ijb",
            json={
                "weights_path": weights_path,
                "backbone": backbone,
                "image_path": image_path,
                "target": target,
                "batch_size": batch_size,
                "use_norm_score": use_norm_score,
                "use_detector_score": use_detector_score,
                "use_flip_test": use_flip_test,
                "result_dir": result_dir,
            },
            timeout=30,
        )

    def eval_submit_threshold_sweep(
        self,
        weights_path: str,
        backbone: str,
        image_dir: str,
        db_path: str,
        thresholds: str = "0.30,0.35,0.40,0.45,0.50,0.55,0.60",
        device: str = "auto",
    ):
        return self._request(
            "POST",
            "/developer/eval/threshold-sweep",
            json={
                "weights_path": weights_path,
                "backbone": backbone,
                "image_dir": image_dir,
                "db_path": db_path,
                "thresholds": thresholds,
                "device": device,
            },
            timeout=30,
        )

    def eval_job_status(self, job_id: str):
        return self._request("GET", f"/developer/eval/status/{job_id}", timeout=10)

    def eval_cancel_job(self, job_id: str):
        return self._request("POST", f"/developer/eval/cancel/{job_id}", timeout=10)

    def eval_list_jobs(self):
        return self._request("GET", "/developer/eval/jobs", timeout=10)

    def stats(self):
        return self._request("GET", "/stats")

    def list_identities(self):
        return self._request("GET", "/identity")

    def add_identity(
        self,
        person_id: str,
        files: Iterable[Tuple[str, bytes, str]],
        gender: str = "unspecified",
        birth_date: str = "",
    ):
        upload_files = [
            ("files", (filename, content, mime_type))
            for filename, content, mime_type in files
        ]
        return self._request(
            "POST",
            "/identity/add",
            data={
                "person_id": person_id,
                "gender": gender,
                "birth_date": birth_date,
            },
            files=upload_files,
            timeout=300,
        )

    def delete_identity(self, person_name: str):
        return self._request("DELETE", f"/identity/{person_name}")

    def rename_identity(self, old_name: str, new_name: str):
        return self._request(
            "PUT",
            "/identity/rename",
            json={"old_name": old_name, "new_name": new_name},
        )

    def get_identity_detail(self, person_name: str):
        return self._request("GET", f"/identity/{person_name}/detail")

    def update_identity(
        self,
        person_name: str,
        new_name: str = "",
        gender: str = "",
        birth_date: str = "",
    ):
        payload: dict = {}
        if new_name:
            payload["new_name"] = new_name
        if gender:
            payload["gender"] = gender
        if birth_date:
            payload["birth_date"] = birth_date
        return self._request("PUT", f"/identity/{person_name}", json=payload)

    def recognize_image(self, filename: str, content: bytes, threshold: float = 0.45):
        return self._request(
            "POST",
            "/recognize",
            data={"threshold": threshold},
            files={"file": (filename, content, "application/octet-stream")},
            timeout=300,
        )

    def recognize_video(
        self,
        filename: str,
        content: bytes,
        skip_frames: int,
        threshold: float,
        stable_frames: int,
        mode: str,
        verify_target: Optional[str],
    ):
        data = {
            "skip_frames": skip_frames,
            "threshold": threshold,
            "stable_frames": stable_frames,
            "mode": mode,
        }
        if verify_target:
            data["verify_target"] = verify_target

        return self._request(
            "POST",
            "/recognize/video",
            data=data,
            files={"file": (filename, content, "application/octet-stream")},
            timeout=3600,
        )

    def start_camera(
        self,
        camera_id: int,
        skip_frames: int,
        threshold: float,
        stable_frames: int,
        mode: str,
        verify_target: Optional[str],
    ):
        return self._request(
            "POST",
            "/camera/start",
            json={
                "camera_id": camera_id,
                "skip_frames": skip_frames,
                "threshold": threshold,
                "stable_frames": stable_frames,
                "mode": mode,
                "verify_target": verify_target,
            },
            timeout=300,
        )

    def stop_camera(self):
        return self._request("POST", "/camera/stop")

    def clear_camera(self):
        return self._request("POST", "/camera/clear")

    def camera_status(self):
        return self._request("GET", "/camera/status")

    # ------------------------------------------------------------------
    # AI 肖像生成
    # ------------------------------------------------------------------

    def portrait_styles(self):
        """获取可用的肖像生成风格列表。"""
        return self._request("GET", "/portrait/styles")

    def portrait_persons(self):
        """获取已注册人员及其照片信息。"""
        return self._request("GET", "/portrait/persons")

    def portrait_person_image(self, person_name: str):
        """获取指定人员的原始照片 (base64)。"""
        return self._request("GET", f"/portrait/person/{person_name}/image")

    def portrait_generate(
        self,
        person_name: str,
        image_path: str,
        style: str,
        seed: int = None,
        num_inference_steps: int = None,
        guidance_scale: float = None,
        start_merge_step: int = None,
    ):
        """提交 AI 肖像生成请求。"""
        payload = {
            "person_name": person_name,
            "image_path": image_path,
            "style": style,
        }
        if seed is not None:
            payload["seed"] = seed
        if num_inference_steps is not None:
            payload["num_inference_steps"] = num_inference_steps
        if guidance_scale is not None:
            payload["guidance_scale"] = guidance_scale
        if start_merge_step is not None:
            payload["start_merge_step"] = start_merge_step
        return self._request("POST", "/portrait/generate", json=payload, timeout=600)

    def portrait_unload(self):
        """卸载肖像生成模型。"""
        return self._request("POST", "/portrait/unload")

    def portrait_status(self):
        """查询肖像生成服务状态。"""
        return self._request("GET", "/portrait/status")

    def _request(self, method: str, path: str, timeout: int = 30, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=timeout,
                headers=headers,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiClientError(f"无法连接 API 服务: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except ValueError:
                pass
            raise ApiClientError(str(detail))

        if not response.content:
            return {}
        return response.json()
