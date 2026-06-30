import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings


DEFAULT_LIMIT = 100
MAX_LIMIT = 500
MAX_SQL_LENGTH = 4000
QUERY_TIMEOUT_MS = 5000
ALLOWED_TABLES = frozenset({"persons", "cameras", "face_events", "unknown_events"})
COMMENT_PATTERN = re.compile(r"(--|/\*|\*/)")
DANGEROUS_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|replace|merge|grant|revoke|"
    r"vacuum|analyze|copy|call|execute|do|set|reset|lock|comment|attach|detach)\b",
    re.IGNORECASE,
)
DANGEROUS_FUNCTION_PATTERN = re.compile(
    r"\b(pg_sleep|dblink|lo_import|lo_export)\s*\(",
    re.IGNORECASE,
)
LIMIT_PATTERN = re.compile(r"\blimit\s+(\d+)\b", re.IGNORECASE)
TABLE_REFERENCE_PATTERN = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][\w.]*|\"[^\"]+\")", re.IGNORECASE)


class SQLSafetyError(ValueError):
    pass


class LLMConfigError(RuntimeError):
    pass


def validate_select_sql(sql: str) -> str:
    normalized = sql.strip()
    if not normalized:
        raise SQLSafetyError("SQL 不能为空")
    if len(normalized) > MAX_SQL_LENGTH:
        raise SQLSafetyError(f"SQL 过长，不能超过 {MAX_SQL_LENGTH} 个字符")
    if COMMENT_PATTERN.search(normalized):
        raise SQLSafetyError("禁止 SQL 注释")
    if normalized.endswith(";"):
        normalized = normalized[:-1].strip()
    if not normalized.lower().startswith("select"):
        raise SQLSafetyError("只允许 SELECT 查询")
    if ";" in normalized:
        raise SQLSafetyError("禁止多语句 SQL")
    if DANGEROUS_SQL_PATTERN.search(normalized):
        raise SQLSafetyError("SQL 包含危险关键字")
    if DANGEROUS_FUNCTION_PATTERN.search(normalized):
        raise SQLSafetyError("SQL 包含危险函数")
    if re.search(r"\bfor\s+update\b", normalized, re.IGNORECASE):
        raise SQLSafetyError("禁止锁定查询")
    _validate_table_whitelist(normalized)
    return normalized


def ensure_select_limit(sql: str, limit: int = DEFAULT_LIMIT) -> str:
    safe_sql = validate_select_sql(sql)
    limit_match = LIMIT_PATTERN.search(safe_sql)
    if limit_match:
        explicit_limit = int(limit_match.group(1))
        if explicit_limit > MAX_LIMIT:
            raise SQLSafetyError(f"LIMIT 不能超过 {MAX_LIMIT}")
        return safe_sql
    return f"{safe_sql} LIMIT {limit}"


def _validate_table_whitelist(sql: str) -> None:
    for match in TABLE_REFERENCE_PATTERN.finditer(sql):
        table_name = _normalize_table_name(match.group(1))
        if table_name not in ALLOWED_TABLES:
            raise SQLSafetyError(f"SQL 访问了非白名单表: {table_name}")


def _normalize_table_name(raw_table_name: str) -> str:
    table_name = raw_table_name.strip('"').lower()
    if "." in table_name:
        table_name = table_name.rsplit(".", 1)[-1]
    return table_name


SCHEMA_PROMPT = """
你是一个只负责生成 PostgreSQL 只读 SQL 的助手。根据用户中文问题，为安全事件中心生成一条 SELECT 查询。

硬性规则：
- 只能输出 JSON，格式为 {"sql": "SELECT ..."}。
- SQL 必须以 SELECT 开头。
- 禁止 INSERT、UPDATE、DELETE、DROP、ALTER、TRUNCATE、CREATE、REPLACE、MERGE、GRANT、REVOKE、COPY、CALL、EXECUTE、DO、SET、LOCK 等写入或管理语句。
- 禁止多语句，禁止分号，禁止 FOR UPDATE。
- 只能查询 persons、cameras、face_events、unknown_events 四张表。
- 禁止 pg_sleep、dblink、lo_import、lo_export 等函数。
- LIMIT 不能超过 500。
- 如果用户没有要求具体条数，请添加 LIMIT 100。
- 时间范围使用 PostgreSQL 写法，例如：event_time >= NOW() - INTERVAL '7 days'。

表结构：

1. persons：人员主数据
- id BIGINT 主键：人员 ID。
- external_id VARCHAR(64)：外部工号/编号，唯一。
- name VARCHAR(100)：人员姓名，常用于按姓名查询，如 p.name = '张三'。
- gender VARCHAR(20)：性别。
- department VARCHAR(100)：部门。
- status VARCHAR(20)：人员状态，常见 active/inactive。
- created_at、updated_at：创建/更新时间。

2. cameras：摄像头主数据
- id BIGINT 主键：摄像头 ID。
- code VARCHAR(64)：摄像头编码，唯一。
- name VARCHAR(100)：摄像头名称。
- location VARCHAR(255)：安装位置。
- latitude、longitude：经纬度。
- status VARCHAR(20)：摄像头状态，常见 online/offline。
- created_at、updated_at：创建/更新时间。

3. face_events：人脸识别事件事实表
- event_id UUID 主键：事件 ID。
- person_id BIGINT：已知人员 ID，可为空，关联 persons.id。
- person_name VARCHAR(100)：事件发生时的人员姓名快照；陌生人事件为空。
- camera_id BIGINT：摄像头 ID，可为空，关联 cameras.id。
- camera_name VARCHAR(100)：事件发生时的摄像头名称快照。
- event_time TIMESTAMPTZ：事件发生时间，时间统计优先使用该字段。
- confidence_score NUMERIC(5,4)：识别置信度，0 到 1。
- event_type VARCHAR(16)：事件类型，known 表示已知人员，unknown 表示陌生人。
- snapshot_path VARCHAR(500)：抓拍图片路径。
- created_at TIMESTAMPTZ：入库时间。

4. unknown_events：陌生人事件扩展表
- id BIGINT 主键。
- event_id UUID：唯一外键，关联 face_events.event_id，一条陌生人扩展对应一条 face_events。
- track_id VARCHAR(100)：陌生人轨迹 ID。
- first_seen_at TIMESTAMPTZ：该轨迹首次出现时间。
- last_seen_at TIMESTAMPTZ：该轨迹最后出现时间。
- occurrence_count INTEGER：该轨迹累计出现次数。
- notes TEXT：备注。
- created_at TIMESTAMPTZ：创建时间。

关联关系和常用查询：
- face_events.person_id = persons.id，用于按人员姓名、部门、状态统计已知人员事件。
- face_events.camera_id = cameras.id，用于按摄像头名称、位置、状态统计事件。
- unknown_events.event_id = face_events.event_id，用于查询陌生人轨迹、首次/最后出现和 occurrence_count。
- 统计陌生人出现次数通常查询 face_events WHERE event_type = 'unknown'；如果问题强调轨迹累计次数，可 SUM(unknown_events.occurrence_count)。
- 统计已知人员出现次数通常查询 face_events WHERE event_type = 'known'，并按 person_id/person_name 聚合。
- “最近7天/30天/90天/一周”都按 face_events.event_time 过滤。
- “哪个摄像头最多”通常 GROUP BY camera_id, camera_name 或关联 cameras 后 GROUP BY cameras.id, cameras.name。
""".strip()


class NL2SQLService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def query(self, db: Session, question: str) -> dict[str, Any]:
        generated_sql = self._generate_sql(question)
        safe_sql = ensure_select_limit(generated_sql)
        rows = self._execute_select(db, safe_sql)
        return {
            "question": question,
            "sql": safe_sql,
            "rows": rows,
            "answer": self._build_answer(question, rows),
        }

    def _generate_sql(self, question: str) -> str:
        base_url = self.settings.llm_base_url.strip()
        api_key = self.settings.llm_api_key.strip()
        model = self.settings.llm_model.strip()
        if not base_url or not api_key or not model:
            raise LLMConfigError("请配置 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL")

        response = httpx.post(
            self._chat_completions_url(base_url),
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SCHEMA_PROMPT},
                    {"role": "user", "content": question},
                ],
                "temperature": 0,
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._extract_sql(content)

    @staticmethod
    def _chat_completions_url(base_url: str) -> str:
        return f"{base_url.rstrip('/')}/chat/completions"

    @staticmethod
    def _extract_sql(content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json|sql)?", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
        try:
            payload = json.loads(cleaned)
            sql = payload.get("sql")
            if isinstance(sql, str):
                return sql
        except json.JSONDecodeError:
            pass
        return cleaned

    @staticmethod
    def _execute_select(db: Session, sql: str) -> list[dict[str, Any]]:
        dialect_name = db.bind.dialect.name if db.bind is not None else ""
        if dialect_name == "postgresql":
            db.execute(text(f"SET LOCAL statement_timeout = {QUERY_TIMEOUT_MS}"))
        result = db.execute(text(sql))
        return [
            {key: _to_jsonable(value) for key, value in row.items()}
            for row in result.mappings().all()
        ]

    @staticmethod
    def _build_answer(question: str, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return f"问题“{question}”的查询没有返回数据。"
        if len(rows) == 1 and len(rows[0]) == 1:
            key, value = next(iter(rows[0].items()))
            return f"查询结果显示，{_label_for_key(key)}为 {_format_answer_value(value)}。"

        trend_answer = _build_trend_answer(rows)
        if trend_answer:
            return trend_answer

        ranking_answer = _build_ranking_answer(rows)
        if ranking_answer:
            return ranking_answer

        first_row = _format_row_summary(rows[0])
        fields = "、".join(rows[0].keys())
        return f"查询返回 {len(rows)} 行结果，字段包括 {fields}。首条记录：{first_row}。"


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def _build_trend_answer(rows: list[dict[str, Any]]) -> str | None:
    if len(rows) < 2:
        return None
    first_row = rows[0]
    time_key = _first_existing_key(first_row, ("date", "day", "event_date", "event_time"))
    metric_key = _first_metric_key(first_row)
    if not time_key or not metric_key:
        return None

    comparable_rows = [row for row in rows if _is_number(row.get(metric_key))]
    if not comparable_rows:
        return None
    max_row = max(comparable_rows, key=lambda row: row[metric_key])
    min_row = min(comparable_rows, key=lambda row: row[metric_key])
    metric_label = _label_for_key(metric_key)
    return (
        f"查询返回 {len(rows)} 个时间点的趋势数据。"
        f"最高值出现在 {_format_answer_value(max_row.get(time_key))}，"
        f"{metric_label}为 {_format_answer_value(max_row.get(metric_key))}；"
        f"最低值出现在 {_format_answer_value(min_row.get(time_key))}，"
        f"{metric_label}为 {_format_answer_value(min_row.get(metric_key))}。"
    )


def _build_ranking_answer(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None
    first_row = rows[0]
    metric_key = _first_metric_key(first_row)
    dimension_key = _first_dimension_key(first_row, exclude={metric_key} if metric_key else set())
    if not metric_key or not dimension_key:
        return None

    metric_label = _label_for_key(metric_key)
    leader = rows[0]
    top_items = "、".join(
        f"{_format_answer_value(row.get(dimension_key))}（{_format_answer_value(row.get(metric_key))}）"
        for row in rows[:5]
    )
    return (
        f"查询返回 {len(rows)} 行排行结果。"
        f"排名第一的是{_format_answer_value(leader.get(dimension_key))}，"
        f"{metric_label}为 {_format_answer_value(leader.get(metric_key))}。"
        f"前 {min(len(rows), 5)} 项为：{top_items}。"
    )


def _first_existing_key(row: dict[str, Any], candidates: tuple[str, ...]) -> str | None:
    for key in candidates:
        if key in row:
            return key
    return None


def _first_metric_key(row: dict[str, Any]) -> str | None:
    for key, value in row.items():
        if _is_number(value) and (
            key.endswith("_count")
            or key.endswith("_total")
            or key in {"count", "total", "event_count", "unknown_count"}
        ):
            return key
    for key, value in row.items():
        if _is_number(value):
            return key
    return None


def _first_dimension_key(row: dict[str, Any], exclude: set[str]) -> str | None:
    preferred_suffixes = ("_name", "name", "department", "location", "date", "day")
    for key, value in row.items():
        if key in exclude:
            continue
        if isinstance(value, str) and (key.endswith(preferred_suffixes) or key in preferred_suffixes):
            return key
    for key, value in row.items():
        if key not in exclude and not _is_number(value):
            return key
    return None


def _format_row_summary(row: dict[str, Any]) -> str:
    return "，".join(
        f"{_label_for_key(key)}为 {_format_answer_value(value)}"
        for key, value in row.items()
    )


def _label_for_key(key: str) -> str:
    labels = {
        "camera_name": "摄像头",
        "person_name": "人员",
        "department": "部门",
        "event_count": "事件数量",
        "unknown_count": "陌生人数量",
        "known_count": "已知人员数量",
        "total_events": "事件总数",
        "count": "数量",
        "total": "总数",
        "date": "日期",
        "day": "日期",
    }
    return labels.get(key, key)


def _format_answer_value(value: Any) -> str:
    if value is None:
        return "空"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)
