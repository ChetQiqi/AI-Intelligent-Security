import type { HealthResponse } from '../types';
import type { FaceEvent } from '../types/api';

export type MetricKind = 'fps' | 'latency' | 'accuracy';
export type ServiceTone = 'healthy' | 'warning' | 'danger';
export type EvaluationStatus = 'completed' | 'running' | 'failed';

export interface EvaluationRun {
  id: string;
  startedAt: string;
  model: string;
  detector: string;
  fps: number;
  latency: number;
  accuracy: number;
  status: EvaluationStatus;
  note: string;
}

export interface RecentRecognition {
  id: string;
  name: string;
  location: string;
  time: string;
  confidence: string;
  imageUrl: string | null;
  alert: boolean;
}

interface RecentRecognitionOptions {
  now?: Date;
  windowMs?: number;
  limit?: number;
}

const DEFAULT_EVENT_API_BASE = 'http://127.0.0.1:8001/api/v1';

export function resolveEventSnapshotUrl(path: string | null): string | null {
  const normalized = path?.trim();
  if (!normalized) {
    return null;
  }

  if (/^https?:\/\//i.test(normalized) || normalized.startsWith('data:')) {
    return normalized;
  }

  const configuredBase =
    import.meta.env?.VITE_EVENT_API_BASE_URL ?? DEFAULT_EVENT_API_BASE;
  const origin = configuredBase.replace(/\/api\/v1\/?$/, '');
  return `${origin}/${normalized.replace(/^\/+/, '')}`;
}

function formatConfidence(value: number | string): string {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return '--';
  }
  return `${(Math.min(Math.max(numericValue, 0), 1) * 100).toFixed(1)}%`;
}

function formatEventTime(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(new Date(value));
}

export function buildRecentRecognitions(
  events: FaceEvent[],
  options: RecentRecognitionOptions = {},
): RecentRecognition[] {
  const now = options.now ?? new Date();
  const windowMs = options.windowMs ?? 5 * 60 * 1000;
  const limit = options.limit ?? 5;
  const nowMs = now.getTime();

  return events
    .map((event) => ({ event, eventTimeMs: Date.parse(event.event_time) }))
    .filter(
      ({ eventTimeMs }) =>
        Number.isFinite(eventTimeMs) &&
        eventTimeMs <= nowMs &&
        nowMs - eventTimeMs <= windowMs,
    )
    .sort((left, right) => right.eventTimeMs - left.eventTimeMs)
    .slice(0, Math.max(0, limit))
    .map(({ event }) => {
      const isUnknown = event.event_type === 'unknown';
      const knownName =
        event.person_name?.trim() ||
        (event.person_id ? `人员 #${event.person_id}` : '已识别人员');

      return {
        id: event.event_id,
        name: isUnknown ? '未知人员' : knownName,
        location: event.camera_name?.trim() || '未命名摄像头',
        time: formatEventTime(event.event_time),
        confidence: formatConfidence(event.confidence_score),
        imageUrl: resolveEventSnapshotUrl(event.snapshot_path),
        alert: isUnknown,
      };
    });
}

export function formatMetric(value: number, kind: MetricKind): string {
  if (kind === 'accuracy') {
    return `${(value * 100).toFixed(1)}%`;
  }

  if (kind === 'latency') {
    return `${value.toFixed(1)} ms`;
  }

  return `${value.toFixed(1)} FPS`;
}

export function getServiceStatus(
  health: HealthResponse | null
): { label: string; tone: ServiceTone } {
  if (!health || health.status !== 'ok') {
    return { label: '连接失败', tone: 'danger' };
  }

  if (!health.model_loaded) {
    return { label: '模型未加载', tone: 'warning' };
  }

  return { label: '运行正常', tone: 'healthy' };
}

function escapeCsvCell(value: string | number): string {
  const text = String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function buildEvaluationCsv(rows: EvaluationRun[]): string {
  const headers = [
    '评估编号',
    '开始时间',
    '模型',
    '检测器',
    'FPS',
    '平均延迟(ms)',
    '准确率',
    '状态',
    '备注',
  ];

  const body = rows.map((row) =>
    [
      row.id,
      row.startedAt,
      row.model,
      row.detector,
      row.fps.toFixed(1),
      row.latency.toFixed(1),
      `${(row.accuracy * 100).toFixed(1)}%`,
      row.status,
      row.note,
    ]
      .map(escapeCsvCell)
      .join(',')
  );

  return `\uFEFF${[headers.join(','), ...body].join('\r\n')}`;
}
