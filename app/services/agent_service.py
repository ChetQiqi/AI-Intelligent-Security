from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.models import Camera, EventType, FaceEvent, KnowledgeChunk, Person
from app.schemas.agent import (
    AgentAnalyzeResponse,
    AgentAnomaly,
    AgentEvidence,
    AgentToolResult,
)
from app.services.rag_service import RAGService
from app.services.stats_service import (
    get_camera_activity,
    get_person_ranking,
    get_stats_summary,
    get_unknown_trend,
)

RISK_LABELS = {
    "low": "低风险",
    "medium": "中风险",
    "high": "高风险",
}


def analyze_security_situation(
    db: Session,
    *,
    question: str,
    days: int,
) -> AgentAnalyzeResponse:
    summary = get_stats_summary(db)
    unknown_trend = get_unknown_trend(db, days=days)
    camera_activity = get_camera_activity(db, days=days)
    person_ranking = get_person_ranking(db, limit=5)

    department = _extract_department(db, question)
    if department and _is_department_recognition_question(question):
        return _analyze_department_recognition(
            db,
            question=question,
            days=days,
            department=department,
            summary=summary,
            unknown_trend=unknown_trend,
            camera_activity=camera_activity,
            person_ranking=person_ranking,
        )

    camera = _extract_camera(db, question)
    if camera and _is_camera_security_question(question):
        return _analyze_camera_security(
            db,
            question=question,
            days=days,
            camera=camera,
            summary=summary,
            unknown_trend=unknown_trend,
            camera_activity=camera_activity,
            person_ranking=person_ranking,
        )

    evidence = _build_evidence(summary, camera_activity, unknown_trend)
    anomalies = _detect_anomalies(evidence, camera_activity)
    findings = _build_findings(summary, camera_activity, unknown_trend)
    knowledge_advice = _query_knowledge_advice(db, findings)

    recommendations = _build_recommendations(summary, camera_activity, knowledge_advice, anomalies)
    risk_level = _classify_risk(anomalies)
    report = _build_report(
        question=question,
        days=days,
        risk_level=risk_level,
        evidence=evidence,
        anomalies=anomalies,
        findings=findings,
        recommendations=recommendations,
        knowledge_advice=knowledge_advice,
    )

    return AgentAnalyzeResponse(
        question=question,
        days=days,
        risk_level=risk_level,
        summary=summary,
        unknown_trend=unknown_trend,
        camera_activity=camera_activity,
        person_ranking=person_ranking,
        evidence=evidence,
        anomalies=anomalies,
        knowledge_advice=knowledge_advice,
        findings=findings,
        recommendations=recommendations,
        tool_results=_build_common_tool_results(
            summary=summary,
            unknown_trend=unknown_trend,
            camera_activity=camera_activity,
            person_ranking=person_ranking,
            knowledge_advice=knowledge_advice,
        ),
        report=report,
    )


def _analyze_department_recognition(
    db: Session,
    *,
    question: str,
    days: int,
    department: str,
    summary,
    unknown_trend,
    camera_activity,
    person_ranking,
) -> AgentAnalyzeResponse:
    stats = _query_department_recognition(db, department=department, days=days)
    anomalies = _detect_department_anomalies(stats)
    risk_level = _classify_risk(anomalies)
    evidence = AgentEvidence(
        recent_events=stats["event_count"],
        recent_unknown_events=0,
        top_camera_name=stats["top_camera_name"],
        top_camera_events=stats["top_camera_events"],
        top_camera_unknown_events=0,
        top_camera_unknown_rate=0.0,
        peak_unknown_date=None,
        peak_unknown_count=0,
    )
    findings = _build_department_findings(department, stats)
    knowledge_advice = _query_department_knowledge_advice(
        db, department=department, findings=findings, anomalies=anomalies
    )
    recommendations = _build_department_recommendations(department, stats, anomalies, knowledge_advice)
    report = _build_department_report(
        question=question,
        days=days,
        department=department,
        risk_level=risk_level,
        stats=stats,
        anomalies=anomalies,
        findings=findings,
        recommendations=recommendations,
        knowledge_advice=knowledge_advice,
    )
    tool_results = _build_common_tool_results(
        summary=summary,
        unknown_trend=unknown_trend,
        camera_activity=camera_activity,
        person_ranking=person_ranking,
        knowledge_advice=knowledge_advice,
    )
    tool_results.insert(
        0,
        AgentToolResult(
            name="query_department_recognition",
            description=f"查询{department}人员识别统计",
            data=stats,
        ),
    )

    return AgentAnalyzeResponse(
        question=question,
        days=days,
        risk_level=risk_level,
        summary=summary,
        unknown_trend=unknown_trend,
        camera_activity=camera_activity,
        person_ranking=person_ranking,
        evidence=evidence,
        anomalies=anomalies,
        knowledge_advice=knowledge_advice,
        findings=findings,
        recommendations=recommendations,
        tool_results=tool_results,
        report=report,
    )


def _analyze_camera_security(
    db: Session,
    *,
    question: str,
    days: int,
    camera: Camera,
    summary,
    unknown_trend,
    camera_activity,
    person_ranking,
) -> AgentAnalyzeResponse:
    stats = _query_camera_security(db, camera=camera, days=days)
    evidence = AgentEvidence(
        recent_events=stats["event_count"],
        recent_unknown_events=stats["unknown_count"],
        top_camera_name=stats["camera_name"],
        top_camera_events=stats["event_count"],
        top_camera_unknown_events=stats["unknown_count"],
        top_camera_unknown_rate=stats["unknown_rate"],
        peak_unknown_date=stats["peak_unknown_date"],
        peak_unknown_count=stats["peak_unknown_count"],
    )
    anomalies = _detect_camera_anomalies(stats)
    risk_level = _classify_risk(anomalies)
    findings = _build_camera_findings(stats)
    knowledge_advice = _query_camera_knowledge_advice(camera.name, anomalies)
    recommendations = _build_camera_recommendations(stats, anomalies, knowledge_advice)
    report = _build_camera_report(
        question=question,
        days=days,
        risk_level=risk_level,
        stats=stats,
        anomalies=anomalies,
        findings=findings,
        recommendations=recommendations,
        knowledge_advice=knowledge_advice,
    )
    tool_results = _build_common_tool_results(
        summary=summary,
        unknown_trend=unknown_trend,
        camera_activity=camera_activity,
        person_ranking=person_ranking,
        knowledge_advice=knowledge_advice,
    )
    tool_results.insert(
        0,
        AgentToolResult(
            name="query_camera_area_security",
            description=f"查询{camera.name}安防统计",
            data=stats,
        ),
    )
    return AgentAnalyzeResponse(
        question=question,
        days=days,
        risk_level=risk_level,
        summary=summary,
        unknown_trend=unknown_trend,
        camera_activity=camera_activity,
        person_ranking=person_ranking,
        evidence=evidence,
        anomalies=anomalies,
        knowledge_advice=knowledge_advice,
        findings=findings,
        recommendations=recommendations,
        tool_results=tool_results,
        report=report,
    )


def _extract_camera(db: Session, question: str) -> Camera | None:
    cameras = db.scalars(select(Camera).order_by(Camera.name.desc())).all()
    for camera in sorted(cameras, key=lambda item: len(item.name), reverse=True):
        aliases = {camera.name, camera.name.replace("摄像头", ""), camera.code}
        if any(alias and alias in question for alias in aliases):
            return camera
    return None


def _is_camera_security_question(question: str) -> bool:
    return any(keyword in question for keyword in ("安防", "异常", "陌生人", "事件", "情况", "风险"))


def _query_camera_security(db: Session, *, camera: Camera, days: int) -> dict[str, Any]:
    start_at = datetime.now(timezone.utc) - timedelta(days=days)
    base_filters = (
        FaceEvent.camera_id == camera.id,
        FaceEvent.event_time >= start_at,
    )
    event_count = db.scalar(
        select(func.count(FaceEvent.event_id)).where(*base_filters)
    ) or 0
    unknown_count = db.scalar(
        select(func.count(FaceEvent.event_id))
        .where(*base_filters)
        .where(FaceEvent.event_type == EventType.unknown.value)
    ) or 0
    known_count = db.scalar(
        select(func.count(FaceEvent.event_id))
        .where(*base_filters)
        .where(FaceEvent.event_type == EventType.known.value)
    ) or 0
    avg_confidence = db.scalar(
        select(func.avg(FaceEvent.confidence_score)).where(*base_filters)
    )
    last_event_time = db.scalar(
        select(func.max(FaceEvent.event_time)).where(*base_filters)
    )
    low_confidence_count = db.scalar(
        select(func.count(FaceEvent.event_id))
        .where(*base_filters)
        .where(FaceEvent.confidence_score < Decimal("0.60"))
    ) or 0
    day_rows = db.execute(
        select(FaceEvent.event_time)
        .where(*base_filters)
        .where(FaceEvent.event_type == EventType.unknown.value)
    ).all()
    unknown_by_date: dict[str, int] = {}
    for row in day_rows:
        event_date = row.event_time.date().isoformat()
        unknown_by_date[event_date] = unknown_by_date.get(event_date, 0) + 1
    peak_unknown_date = None
    peak_unknown_count = 0
    if unknown_by_date:
        peak_unknown_date, peak_unknown_count = max(
            unknown_by_date.items(), key=lambda item: item[1]
        )
    unknown_rate = round(unknown_count / event_count, 4) if event_count else 0.0
    return {
        "camera_id": camera.id,
        "camera_name": camera.name,
        "camera_status": camera.status,
        "event_count": event_count,
        "known_count": known_count,
        "unknown_count": unknown_count,
        "unknown_rate": unknown_rate,
        "avg_confidence": round(float(avg_confidence), 4) if avg_confidence is not None else None,
        "low_confidence_count": low_confidence_count,
        "last_event_time": _format_datetime(last_event_time),
        "peak_unknown_date": peak_unknown_date,
        "peak_unknown_count": peak_unknown_count,
    }


def _detect_camera_anomalies(stats: dict[str, Any]) -> list[AgentAnomaly]:
    anomalies: list[AgentAnomaly] = []
    if stats["unknown_count"] >= 10:
        anomalies.append(
            AgentAnomaly(
                rule_type="摄像头陌生人高频出现",
                risk_level="high",
                reason=f"{stats['camera_name']} 最近窗口陌生人事件达到 {stats['unknown_count']} 条。",
                evidence={"unknown_count": stats["unknown_count"]},
                recommendation=f"优先复核 {stats['camera_name']} 的陌生人抓拍、门禁记录和现场巡查记录。",
            )
        )
    elif stats["unknown_count"] > 0:
        anomalies.append(
            AgentAnomaly(
                rule_type="摄像头存在陌生人事件",
                risk_level="medium",
                reason=f"{stats['camera_name']} 最近窗口出现 {stats['unknown_count']} 条陌生人事件。",
                evidence={"unknown_count": stats["unknown_count"]},
                recommendation=f"抽查 {stats['camera_name']} 的陌生人事件，确认是否为访客、误报或未授权通行。",
            )
        )
    if stats["event_count"] >= 5 and stats["unknown_rate"] >= 0.3:
        anomalies.append(
            AgentAnomaly(
                rule_type="摄像头陌生人占比过高",
                risk_level="high" if stats["unknown_rate"] >= 0.6 else "medium",
                reason=f"{stats['camera_name']} 陌生人占比 {stats['unknown_rate']:.1%}。",
                evidence={
                    "event_count": stats["event_count"],
                    "unknown_count": stats["unknown_count"],
                    "unknown_rate": stats["unknown_rate"],
                },
                recommendation=f"检查 {stats['camera_name']} 的访客登记、临时授权和识别画面质量。",
            )
        )
    if stats["event_count"] == 0:
        anomalies.append(
            AgentAnomaly(
                rule_type="摄像头无事件上报",
                risk_level="low",
                reason=f"{stats['camera_name']} 最近窗口没有事件。",
                evidence={"event_count": 0},
                recommendation=f"检查 {stats['camera_name']} 在线状态、识别任务和事件上报链路。",
            )
        )
    return anomalies


def _build_camera_findings(stats: dict[str, Any]) -> list[str]:
    findings = [
        (
            f"{stats['camera_name']}最近统计窗口内共有事件 {stats['event_count']} 条，"
            f"其中已知人员 {stats['known_count']} 条，陌生人 {stats['unknown_count']} 条。"
        )
    ]
    findings.append(f"陌生人占比 {stats['unknown_rate']:.1%}，低置信度事件 {stats['low_confidence_count']} 条。")
    if stats["peak_unknown_date"]:
        findings.append(
            f"陌生人峰值出现在 {stats['peak_unknown_date']}，当天 {stats['peak_unknown_count']} 条。"
        )
    if stats["last_event_time"]:
        findings.append(f"最近一次事件时间为 {stats['last_event_time']}。")
    return findings


def _query_camera_knowledge_advice(camera_name: str, anomalies: list[AgentAnomaly]) -> str:
    if not anomalies:
        return (
            f"{camera_name}本次未命中明显安防异常规则。建议按制度保留巡检和识别记录，"
            "定期复核摄像头在线状态、画面质量、门禁授权和访客登记。"
        )
    return (
        f"{camera_name}已命中安防规则。处置时应先核对该摄像头抓拍、门禁记录和现场巡查记录，"
        "确认陌生人是否为访客、外包人员、误识别或未授权通行；完成身份确认后记录处置结果，"
        "必要时升级给安保负责人复核。"
    )


def _build_camera_recommendations(
    stats: dict[str, Any],
    anomalies: list[AgentAnomaly],
    knowledge_advice: str,
) -> list[str]:
    recommendations = [
        f"先查看 {stats['camera_name']} 最近事件列表，核对事件时间、抓拍图和置信度。",
        f"复核 {stats['camera_name']} 对应区域的门禁记录和访客登记。",
    ]
    for anomaly in anomalies:
        if anomaly.recommendation not in recommendations:
            recommendations.append(anomaly.recommendation)
    if knowledge_advice:
        recommendations.append("按制度完成现场确认、处置登记和复盘记录。")
    return recommendations


def _build_camera_report(
    *,
    question: str,
    days: int,
    risk_level: str,
    stats: dict[str, Any],
    anomalies: list[AgentAnomaly],
    findings: list[str],
    recommendations: list[str],
    knowledge_advice: str,
) -> str:
    anomaly_lines = "\n".join(
        f"{index + 1}. [{RISK_LABELS[anomaly.risk_level]}] {anomaly.rule_type}：{anomaly.reason}"
        for index, anomaly in enumerate(anomalies)
    )
    finding_lines = "\n".join(f"{index + 1}. {finding}" for index, finding in enumerate(findings))
    recommendation_lines = "\n".join(
        f"{index + 1}. {recommendation}" for index, recommendation in enumerate(recommendations)
    )
    avg_confidence = (
        f"{stats['avg_confidence']:.1%}" if stats["avg_confidence"] is not None else "暂无"
    )
    peak_unknown = (
        f"{stats['peak_unknown_date']}，{stats['peak_unknown_count']} 条"
        if stats["peak_unknown_date"]
        else "暂无"
    )
    return (
        "## 总体概览\n"
        f"分析问题：{question}\n"
        f"分析对象：{stats['camera_name']}安防情况\n"
        f"统计窗口：最近 {days} 天\n"
        f"风险等级：{RISK_LABELS[risk_level]}\n\n"
        "## 证据数据\n"
        f"1. {stats['camera_name']}事件：{stats['event_count']} 条，已知人员 {stats['known_count']} 条，"
        f"陌生人 {stats['unknown_count']} 条。\n"
        f"2. 陌生人占比：{stats['unknown_rate']:.1%}，平均识别置信度：{avg_confidence}，"
        f"低置信度事件 {stats['low_confidence_count']} 条。\n"
        f"3. 陌生人峰值日期：{peak_unknown}。\n\n"
        "## 异常规则命中\n"
        f"{anomaly_lines or '暂无摄像头安防异常。'}\n\n"
        "## 安防情况\n"
        f"{finding_lines or '暂无事件记录。'}\n\n"
        "## 处理建议\n"
        f"{recommendation_lines or '暂无额外建议。'}\n\n"
        "## 制度依据\n"
        f"{knowledge_advice}"
    )


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _extract_department(db: Session, question: str) -> str | None:
    departments = db.scalars(
        select(Person.department)
        .where(Person.department.is_not(None))
        .distinct()
    ).all()
    for department in sorted((item for item in departments if item), key=len, reverse=True):
        if department in question:
            return department
    return None


def _is_department_recognition_question(question: str) -> bool:
    return any(keyword in question for keyword in ("人员", "识别", "出勤", "出现", "通行"))


def _query_department_recognition(db: Session, *, department: str, days: int) -> dict[str, Any]:
    start_at = datetime.now(timezone.utc) - timedelta(days=days)
    registered_count = db.scalar(
        select(func.count()).select_from(Person).where(Person.department == department)
    ) or 0
    base_filters = (
        FaceEvent.event_type == EventType.known.value,
        FaceEvent.event_time >= start_at,
        Person.department == department,
    )
    event_count = db.scalar(
        select(func.count(FaceEvent.event_id))
        .join(Person, Person.id == FaceEvent.person_id)
        .where(*base_filters)
    ) or 0
    recognized_person_count = db.scalar(
        select(func.count(func.distinct(FaceEvent.person_id)))
        .join(Person, Person.id == FaceEvent.person_id)
        .where(*base_filters)
    ) or 0
    avg_confidence = db.scalar(
        select(func.avg(FaceEvent.confidence_score))
        .join(Person, Person.id == FaceEvent.person_id)
        .where(*base_filters)
    )
    low_confidence_count = db.scalar(
        select(func.count(FaceEvent.event_id))
        .join(Person, Person.id == FaceEvent.person_id)
        .where(*base_filters)
        .where(FaceEvent.confidence_score < Decimal("0.60"))
    ) or 0

    top_person_rows = db.execute(
        select(Person.name, func.count(FaceEvent.event_id).label("event_count"))
        .join(FaceEvent, FaceEvent.person_id == Person.id)
        .where(*base_filters)
        .group_by(Person.id, Person.name)
        .order_by(desc("event_count"), Person.name.asc())
        .limit(5)
    ).all()
    top_camera_rows = db.execute(
        select(FaceEvent.camera_name, func.count(FaceEvent.event_id).label("event_count"))
        .join(Person, Person.id == FaceEvent.person_id)
        .where(*base_filters)
        .group_by(FaceEvent.camera_name)
        .order_by(desc("event_count"), FaceEvent.camera_name.asc())
        .limit(5)
    ).all()
    seen_person_ids = (
        select(FaceEvent.person_id)
        .join(Person, Person.id == FaceEvent.person_id)
        .where(*base_filters)
        .distinct()
    )
    missing_names = db.scalars(
        select(Person.name)
        .where(Person.department == department)
        .where(Person.id.not_in(seen_person_ids))
        .order_by(Person.name.asc())
        .limit(5)
    ).all()

    coverage_rate = recognized_person_count / registered_count if registered_count else 0.0
    top_person = top_person_rows[0] if top_person_rows else None
    top_camera = top_camera_rows[0] if top_camera_rows else None
    return {
        "department": department,
        "registered_count": registered_count,
        "event_count": event_count,
        "recognized_person_count": recognized_person_count,
        "coverage_rate": round(coverage_rate, 4),
        "avg_confidence": round(float(avg_confidence), 4) if avg_confidence is not None else None,
        "low_confidence_count": low_confidence_count,
        "top_person_name": top_person.name if top_person else None,
        "top_person_events": top_person.event_count if top_person else 0,
        "top_camera_name": top_camera.camera_name if top_camera else None,
        "top_camera_events": top_camera.event_count if top_camera else 0,
        "top_persons": [
            {"person_name": row.name, "event_count": row.event_count}
            for row in top_person_rows
        ],
        "top_cameras": [
            {"camera_name": row.camera_name, "event_count": row.event_count}
            for row in top_camera_rows
        ],
        "missing_person_names": list(missing_names),
    }


def _detect_department_anomalies(stats: dict[str, Any]) -> list[AgentAnomaly]:
    anomalies: list[AgentAnomaly] = []
    if stats["registered_count"] > 0 and stats["coverage_rate"] < 0.8:
        anomalies.append(
            AgentAnomaly(
                rule_type="部门人员覆盖不足",
                risk_level="medium" if stats["coverage_rate"] >= 0.5 else "high",
                reason=(
                    f"{stats['department']} 最近窗口仅覆盖 "
                    f"{stats['recognized_person_count']}/{stats['registered_count']} 人。"
                ),
                evidence={
                    "recognized_person_count": stats["recognized_person_count"],
                    "registered_count": stats["registered_count"],
                    "coverage_rate": stats["coverage_rate"],
                },
                recommendation="核对未出现人员是否请假、外出或底库信息缺失。",
            )
        )
    if stats["event_count"] > 0 and stats["low_confidence_count"] / stats["event_count"] >= 0.2:
        anomalies.append(
            AgentAnomaly(
                rule_type="低置信度识别偏多",
                risk_level="medium",
                reason=(
                    f"低置信度识别 {stats['low_confidence_count']} 条，"
                    f"占部门识别事件 {stats['low_confidence_count'] / stats['event_count']:.1%}。"
                ),
                evidence={
                    "event_count": stats["event_count"],
                    "low_confidence_count": stats["low_confidence_count"],
                },
                recommendation="复核低置信度人员底库照片，检查摄像头光照和角度。",
            )
        )
    return anomalies


def _build_department_findings(department: str, stats: dict[str, Any]) -> list[str]:
    findings = [
        (
            f"{department}最近统计窗口内共有识别事件 {stats['event_count']} 条，"
            f"覆盖 {stats['recognized_person_count']}/{stats['registered_count']} 人。"
        )
    ]
    if stats["top_person_name"]:
        findings.append(
            f"出现次数最多的人员是 {stats['top_person_name']}，共 {stats['top_person_events']} 条识别事件。"
        )
    if stats["top_camera_name"]:
        findings.append(
            f"识别事件最多的摄像头是 {stats['top_camera_name']}，共 {stats['top_camera_events']} 条。"
        )
    if stats["missing_person_names"]:
        findings.append(f"最近窗口未识别到：{'、'.join(stats['missing_person_names'])}。")
    return findings


def _build_department_recommendations(
    department: str,
    stats: dict[str, Any],
    anomalies: list[AgentAnomaly],
    knowledge_advice: str,
) -> list[str]:
    recommendations = [
        f"先核对{department}人员名单，确认最近 {stats['recognized_person_count']} 名已识别人员是否符合预期。",
        "对出现次数异常高或长期未出现的人员进行人工复核。",
    ]
    for anomaly in anomalies:
        if anomaly.recommendation not in recommendations:
            recommendations.append(anomaly.recommendation)
    if stats["top_camera_name"]:
        recommendations.append(f"重点查看 {stats['top_camera_name']} 的识别画面质量和通行记录。")
    if knowledge_advice:
        recommendations.append("结合 RAG 知识库中的门禁、访客和复盘流程完成记录。")
    return recommendations


def _build_department_report(
    *,
    question: str,
    days: int,
    department: str,
    risk_level: str,
    stats: dict[str, Any],
    anomalies: list[AgentAnomaly],
    findings: list[str],
    recommendations: list[str],
    knowledge_advice: str,
) -> str:
    anomaly_lines = "\n".join(
        f"{index + 1}. [{RISK_LABELS[anomaly.risk_level]}] {anomaly.rule_type}：{anomaly.reason}"
        for index, anomaly in enumerate(anomalies)
    )
    finding_lines = "\n".join(f"{index + 1}. {finding}" for index, finding in enumerate(findings))
    recommendation_lines = "\n".join(
        f"{index + 1}. {recommendation}" for index, recommendation in enumerate(recommendations)
    )
    avg_confidence = (
        f"{stats['avg_confidence']:.1%}" if stats["avg_confidence"] is not None else "暂无"
    )
    top_person = (
        f"{stats['top_person_name']}，{stats['top_person_events']} 条"
        if stats["top_person_name"]
        else "暂无"
    )
    top_camera = (
        f"{stats['top_camera_name']}，{stats['top_camera_events']} 条"
        if stats["top_camera_name"]
        else "暂无"
    )
    return (
        "## 总体概览\n"
        f"分析问题：{question}\n"
        f"分析对象：{department}人员识别情况\n"
        f"统计窗口：最近 {days} 天\n"
        f"风险等级：{RISK_LABELS[risk_level]}\n\n"
        "## 证据数据\n"
        f"1. {department}识别事件：{stats['event_count']} 条，覆盖 "
        f"{stats['recognized_person_count']}/{stats['registered_count']} 人，覆盖率 {stats['coverage_rate']:.1%}。\n"
        f"2. 平均识别置信度：{avg_confidence}，低置信度事件 {stats['low_confidence_count']} 条。\n"
        f"3. 出现最多人员：{top_person}；识别最多摄像头：{top_camera}。\n\n"
        "## 异常规则命中\n"
        f"{anomaly_lines or '暂无部门识别异常。'}\n\n"
        "## 识别情况\n"
        f"{finding_lines or '暂无识别记录。'}\n\n"
        "## 处理建议\n"
        f"{recommendation_lines or '暂无额外建议。'}\n\n"
        "## 制度依据\n"
        f"{knowledge_advice}"
    )


def _query_department_knowledge_advice(
    db: Session,
    *,
    department: str,
    findings: list[str],
    anomalies: list[AgentAnomaly],
) -> str:
    if not anomalies:
        return (
            f"{department}本次未命中部门识别异常规则。建议按制度保留识别记录，"
            "定期复核人员名单、底库照片、摄像头画面质量和门禁授权状态；"
            "如后续出现覆盖不足、低置信度偏多或长期未识别人员，再升级为专项复核。"
        )

    has_chunks = db.scalar(select(KnowledgeChunk.id).limit(1)) is not None
    if not has_chunks:
        return "知识库暂无可用文档；建议先上传安防制度、门禁规则和应急处置流程。"
    try:
        return RAGService().query(
            db,
            question=(
                f"请只根据安防制度、门禁规则和应急处置流程，给出{department}人员识别问题的制度处置建议。"
                "实际统计和异常规则已经由系统完成，不要自行新增异常结论。"
                "不要把出现次数最多、摄像头事件最多直接判定为异常。"
                f"已命中的规则包括：{'；'.join(anomaly.rule_type for anomaly in anomalies)}。"
                f"已发现的问题包括：{'；'.join(findings[:3])}"
            ),
            top_k=3,
        ).answer
    except Exception as exc:  # pragma: no cover - defensive fallback for external model failures
        return f"知识库暂不可用：{exc}"


def _query_knowledge_advice(db: Session, findings: list[str]) -> str:
    has_chunks = db.scalar(select(KnowledgeChunk.id).limit(1)) is not None
    if not has_chunks:
        return "知识库暂无可用文档；建议先上传安防制度、门禁规则和应急处置流程。"
    try:
        return RAGService().query(
            db,
            question=(
                "请只根据安防制度、门禁规则和应急处置流程，给出制度处置建议。"
                "不要判断具体统计窗口是否有实际数据，实际数据已经由事件数据库统计完成。"
                f"已发现的问题包括：{'；'.join(findings[:3])}"
            ),
            top_k=3,
        ).answer
    except Exception as exc:  # pragma: no cover - defensive fallback for external model failures
        return f"知识库暂不可用：{exc}"


def _build_evidence(summary, camera_activity, unknown_trend) -> AgentEvidence:
    top_camera = camera_activity.items[0] if camera_activity.items else None
    top_camera_events = top_camera.event_count if top_camera else 0
    top_camera_unknown_events = top_camera.unknown_count if top_camera else 0
    top_camera_unknown_rate = (
        round(top_camera_unknown_events / top_camera_events, 4)
        if top_camera_events
        else 0.0
    )
    peak_unknown = max(unknown_trend.items, key=lambda item: item.unknown_count, default=None)
    return AgentEvidence(
        recent_events=summary.recent_events,
        recent_unknown_events=_recent_unknown_count(camera_activity),
        top_camera_name=top_camera.camera_name if top_camera else None,
        top_camera_events=top_camera_events,
        top_camera_unknown_events=top_camera_unknown_events,
        top_camera_unknown_rate=top_camera_unknown_rate,
        peak_unknown_date=peak_unknown.date if peak_unknown else None,
        peak_unknown_count=peak_unknown.unknown_count if peak_unknown else 0,
    )


def _detect_anomalies(evidence: AgentEvidence, camera_activity) -> list[AgentAnomaly]:
    anomalies: list[AgentAnomaly] = []

    if evidence.recent_unknown_events >= 10:
        risk_level = "high" if evidence.recent_unknown_events >= 20 else "medium"
        anomalies.append(
            AgentAnomaly(
                rule_type="陌生人高频出现",
                risk_level=risk_level,
                reason=f"最近统计窗口内陌生人事件达到 {evidence.recent_unknown_events} 条。",
                evidence={"recent_unknown_events": evidence.recent_unknown_events},
                recommendation="优先复核陌生人事件对应的抓拍、门禁记录和现场巡查记录。",
            )
        )

    if (
        evidence.top_camera_events >= 5
        and evidence.top_camera_unknown_rate >= 0.3
        and evidence.top_camera_name
    ):
        anomalies.append(
            AgentAnomaly(
                rule_type="摄像头陌生人占比过高",
                risk_level="high" if evidence.top_camera_unknown_rate >= 0.6 else "medium",
                reason=(
                    f"{evidence.top_camera_name} 最近窗口陌生人占比 "
                    f"{evidence.top_camera_unknown_rate:.1%}。"
                ),
                evidence={
                    "camera_name": evidence.top_camera_name,
                    "event_count": evidence.top_camera_events,
                    "unknown_count": evidence.top_camera_unknown_events,
                    "unknown_rate": evidence.top_camera_unknown_rate,
                },
                recommendation=f"对 {evidence.top_camera_name} 做专项复核，确认是否存在尾随、误识别或异常通行。",
            )
        )

    if evidence.peak_unknown_count >= 10 and evidence.peak_unknown_date:
        anomalies.append(
            AgentAnomaly(
                rule_type="陌生人峰值日",
                risk_level="high" if evidence.peak_unknown_count >= 20 else "medium",
                reason=(
                    f"{evidence.peak_unknown_date} 单日陌生人事件 "
                    f"{evidence.peak_unknown_count} 条。"
                ),
                evidence={
                    "date": evidence.peak_unknown_date,
                    "unknown_count": evidence.peak_unknown_count,
                },
                recommendation="回看峰值日期的视频片段，核对是否与施工、访客或设备误报有关。",
            )
        )

    idle_cameras = [item.camera_name for item in camera_activity.items if item.event_count == 0]
    if idle_cameras:
        anomalies.append(
            AgentAnomaly(
                rule_type="摄像头长期无事件",
                risk_level="low",
                reason=f"存在 {len(idle_cameras)} 个最近窗口无事件摄像头。",
                evidence={"camera_names": idle_cameras[:5]},
                recommendation="检查摄像头在线状态、识别任务配置和事件上报链路。",
            )
        )

    return anomalies


def _build_findings(summary, camera_activity, unknown_trend) -> list[str]:
    findings: list[str] = []
    recent_unknown = _recent_unknown_count(camera_activity)
    if summary.recent_events == 0:
        findings.append("最近统计窗口内没有识别事件，需确认模拟数据或实时接入是否正常。")
    else:
        findings.append(
            f"最近统计窗口内共有 {summary.recent_events} 条事件，其中陌生人事件 {recent_unknown} 条。"
        )

    top_camera = camera_activity.items[0] if camera_activity.items else None
    if top_camera:
        findings.append(
            f"事件最集中的摄像头是 {top_camera.camera_name}，窗口内事件 {top_camera.event_count} 条，陌生人 {top_camera.unknown_count} 条。"
        )

    peak_unknown = max(unknown_trend.items, key=lambda item: item.unknown_count, default=None)
    if peak_unknown and peak_unknown.unknown_count > 0:
        findings.append(
            f"陌生人事件峰值出现在 {peak_unknown.date}，当天 {peak_unknown.unknown_count} 条。"
        )
    return findings


def _build_recommendations(
    summary,
    camera_activity,
    knowledge_advice: str,
    anomalies: list[AgentAnomaly],
) -> list[str]:
    recommendations = [
        "优先复核陌生人事件集中的摄像头画面和门禁记录。",
        "对高频异常区域安排现场巡查，并记录处置结论。",
    ]
    if summary.recent_events == 0:
        recommendations.insert(0, "先补充最近 7 天模拟数据或检查实时事件接入。")

    for anomaly in anomalies:
        if anomaly.recommendation not in recommendations:
            recommendations.append(anomaly.recommendation)

    idle_cameras = [item.camera_name for item in camera_activity.items if item.event_count == 0]
    if idle_cameras:
        recommendations.append(f"检查长期无事件摄像头：{'、'.join(idle_cameras[:3])}。")

    if knowledge_advice:
        recommendations.append("结合 RAG 知识库建议执行升级、登记和复盘流程。")
    return recommendations


def _classify_risk(anomalies: list[AgentAnomaly]) -> str:
    if any(anomaly.risk_level == "high" for anomaly in anomalies):
        return "high"
    if any(anomaly.risk_level == "medium" for anomaly in anomalies):
        return "medium"
    return "low"


def _recent_unknown_count(camera_activity) -> int:
    return sum(item.unknown_count for item in camera_activity.items)


def _build_common_tool_results(
    *,
    summary,
    unknown_trend,
    camera_activity,
    person_ranking,
    knowledge_advice: str,
) -> list[AgentToolResult]:
    return [
        AgentToolResult(
            name="query_stats_summary",
            description="查询事件总览统计",
            data=summary.model_dump(),
        ),
        AgentToolResult(
            name="query_unknown_trend",
            description="查询陌生人事件趋势",
            data=unknown_trend.model_dump(),
        ),
        AgentToolResult(
            name="query_camera_activity",
            description="查询摄像头活跃度和陌生人数量",
            data=camera_activity.model_dump(),
        ),
        AgentToolResult(
            name="query_person_ranking",
            description="查询人员出现排行",
            data=person_ranking.model_dump(),
        ),
        AgentToolResult(
            name="query_knowledge_base",
            description="查询安防知识库处置建议",
            data={"answer": knowledge_advice},
        ),
    ]


def _build_report(
    *,
    question: str,
    days: int,
    risk_level: str,
    evidence: AgentEvidence,
    anomalies: list[AgentAnomaly],
    findings: list[str],
    recommendations: list[str],
    knowledge_advice: str,
) -> str:
    finding_lines = "\n".join(f"{index + 1}. {finding}" for index, finding in enumerate(findings))
    anomaly_lines = "\n".join(
        f"{index + 1}. [{RISK_LABELS[anomaly.risk_level]}] {anomaly.rule_type}：{anomaly.reason}"
        for index, anomaly in enumerate(anomalies)
    )
    recommendation_lines = "\n".join(
        f"{index + 1}. {recommendation}"
        for index, recommendation in enumerate(recommendations)
    )
    top_camera_name = evidence.top_camera_name or "暂无"
    peak_unknown = (
        f"{evidence.peak_unknown_date}，{evidence.peak_unknown_count} 条"
        if evidence.peak_unknown_date
        else "暂无"
    )
    return (
        "## 总体概览\n"
        f"分析问题：{question}\n"
        f"统计窗口：最近 {days} 天\n"
        f"风险等级：{RISK_LABELS[risk_level]}\n\n"
        "## 证据数据\n"
        f"1. 最近 {days} 天事件：{evidence.recent_events} 条，陌生人：{evidence.recent_unknown_events} 条。\n"
        f"2. 事件最高摄像头：{top_camera_name}，事件 {evidence.top_camera_events} 条，"
        f"陌生人 {evidence.top_camera_unknown_events} 条，陌生人占比 {evidence.top_camera_unknown_rate:.1%}。\n"
        f"3. 陌生人峰值日期：{peak_unknown}。\n\n"
        "## 异常规则命中\n"
        f"{anomaly_lines or '暂无规则命中。'}\n\n"
        "## 异常发现\n"
        f"{finding_lines or '暂无明显异常。'}\n\n"
        "## 处理建议\n"
        f"{recommendation_lines or '暂无额外建议。'}\n\n"
        "## 制度依据\n"
        f"{knowledge_advice}"
    )
