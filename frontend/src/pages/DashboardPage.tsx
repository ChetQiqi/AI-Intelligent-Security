import { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  BarChart3,
  Camera,
  Database,
  Globe2,
  Lock,
  Radio,
  Search,
  ShieldAlert,
  UserRound,
  Users,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  getCameraActivity,
  getCameraRanking,
  getHealth,
  getPersonRanking,
  getStatsSummary,
  getUnknownTrend,
} from '../api/securityAnalytics';
import PageState from '../components/PageState';
import type {
  CameraActivityItem,
  CameraRankingItem,
  HealthResponse,
  PersonRankingItem,
  StatsSummary,
  UnknownTrendItem,
} from '../types/api';
import type { Language } from '../locales';

interface DashboardPageProps {
  language?: Language;
}

const text = {
  zh: {
    title: 'SENTINEL COMMAND',
    subtitle: '智能安防驾驶舱',
    search: '搜索人员、摄像头或事件...',
    totalEvents: '事件总数',
    unknownEvents: '陌生人事件',
    recentEvents: '近 7 天事件',
    todayPeople: '今日识别人数',
    live: '实时多摄像头流',
    liveHint: 'Live 区域暂留空位，后续接入摄像头画面或事件截图。',
    gridView: '网格视图 2x2',
    liveHd: 'LIVE 待接入',
    cameraSlot: '摄像头空位',
    waiting: '等待视频源',
    anomaly: '关键异常',
    priority: '优先级 1',
    anomalyTitle: 'RAG AGENT ID: AX-9',
    anomalyBody: '检测到陌生人事件增长，需要结合摄像头活跃度与人员排行进一步分析。',
    lockdown: '锁定区域',
    dismiss: '忽略',
    personLogs: '人员出现排行',
    cameraActivity: '摄像头活跃度',
    cameraRanking: '摄像头事件排行',
    unknownTrend: '陌生人趋势',
    globalMap: '全局事件定位',
    onlineNode: '在线节点',
    activeThreat: '活跃风险',
    backend: '后端',
    database: '数据库',
    eventCount: '事件数',
    unknownCount: '陌生人',
    lastEvent: '最后事件',
    noEvent: '暂无事件',
    departmentFallback: '未设置部门',
    emptyRanking: '暂无人员识别事件',
    emptyCamera: '暂无摄像头数据',
  },
  en: {
    title: 'SENTINEL COMMAND',
    subtitle: 'AI Security Command Dashboard',
    search: 'Search people, cameras, or incidents...',
    totalEvents: 'Total Events',
    unknownEvents: 'Unknown Events',
    recentEvents: 'Last 7 Days',
    todayPeople: 'People Today',
    live: 'Live Multi-camera Stream',
    liveHint: 'Live area is reserved for camera streams or event snapshots.',
    gridView: 'Grid View 2x2',
    liveHd: 'LIVE Pending',
    cameraSlot: 'Camera Slot',
    waiting: 'Waiting for video source',
    anomaly: 'Critical Anomalies',
    priority: 'Priority 1',
    anomalyTitle: 'RAG AGENT ID: AX-9',
    anomalyBody:
      'Unknown-person activity requires correlation with camera activity and personnel rankings.',
    lockdown: 'Lockdown Zone',
    dismiss: 'Dismiss',
    personLogs: 'Personnel Ranking',
    cameraActivity: 'Camera Activity',
    cameraRanking: 'Camera Event Ranking',
    unknownTrend: 'Unknown Trend',
    globalMap: 'Global Incident Pinpointing',
    onlineNode: 'Online Node',
    activeThreat: 'Active Threat',
    backend: 'Backend',
    database: 'Database',
    eventCount: 'Events',
    unknownCount: 'Unknown',
    lastEvent: 'Last Event',
    noEvent: 'No events',
    departmentFallback: 'No department',
    emptyRanking: 'No known-person events',
    emptyCamera: 'No camera data',
  },
} satisfies Record<Language, Record<string, string>>;

function formatEventTime(value: string | null, language: Language): string {
  if (!value) return text[language].noEvent;
  return new Intl.DateTimeFormat(language === 'zh' ? 'zh-CN' : 'en-US', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function KpiCard({
  label,
  value,
  tone,
  detail,
}: {
  label: string;
  value: number;
  tone: 'blue' | 'amber' | 'green' | 'red';
  detail: string;
}) {
  return (
    <article className={`sentinel-panel sentinel-kpi sentinel-kpi-${tone}`}>
      <span className="sentinel-kpi-label">{label}</span>
      <div className="sentinel-kpi-value-row">
        <span className="sentinel-kpi-value">{value.toLocaleString()}</span>
        <span className="sentinel-kpi-detail">{detail}</span>
      </div>
    </article>
  );
}

function CameraPlaceholder({ index, title, language }: { index: number; title: string; language: Language }) {
  return (
    <div className="sentinel-camera-slot">
      <div className="sentinel-camera-gridline" />
      <div className="sentinel-camera-slot-header">
        <span>
          CAM-{String(index).padStart(2, '0')}: {title}
        </span>
        <span className="sentinel-live-dot" />
      </div>
      <div className="sentinel-camera-empty">
        <Camera className="h-9 w-9" />
        <span>{text[language].waiting}</span>
      </div>
    </div>
  );
}

export default function DashboardPage({ language = 'zh' }: DashboardPageProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [summary, setSummary] = useState<StatsSummary | null>(null);
  const [ranking, setRanking] = useState<CameraRankingItem[]>([]);
  const [trend, setTrend] = useState<UnknownTrendItem[]>([]);
  const [cameraActivity, setCameraActivity] = useState<CameraActivityItem[]>([]);
  const [personRanking, setPersonRanking] = useState<PersonRankingItem[]>([]);
  const t = text[language];

  const load = () => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    Promise.all([
      getHealth(controller.signal),
      getStatsSummary(controller.signal),
      getCameraRanking(5, controller.signal),
      getUnknownTrend(7, controller.signal),
      getCameraActivity(7, controller.signal),
      getPersonRanking(5, controller.signal),
    ])
      .then(([healthData, summaryData, rankingData, trendData, activityData, personData]) => {
        setHealth(healthData);
        setSummary(summaryData);
        setRanking(rankingData.items);
        setTrend(trendData.items);
        setCameraActivity(activityData.items);
        setPersonRanking(personData.items);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
    return () => controller.abort();
  };

  useEffect(load, []);

  const topCameras = useMemo(() => cameraActivity.slice(0, 4), [cameraActivity]);

  return (
    <div className="sentinel-dashboard">
      <PageState loading={loading} error={error} onRetry={load} />
      {!loading && !error && (
        <>
          <header className="sentinel-command-header">
            <div>
              <p className="sentinel-kicker">PostgreSQL Security Event Center</p>
              <h1>{t.title}</h1>
              <span>{t.subtitle}</span>
            </div>
            <div className="sentinel-search">
              <Search className="h-4 w-4" />
              <input aria-label={t.search} placeholder={t.search} />
            </div>
            <div className="sentinel-status-strip">
              <span>
                <Radio className="h-4 w-4" />
                {t.backend}: {health?.status ?? 'unknown'}
              </span>
              <span>
                <Database className="h-4 w-4" />
                {t.database}: {health?.database ?? 'unknown'}
              </span>
            </div>
          </header>

          <section className="sentinel-kpi-grid">
            <KpiCard label={t.totalEvents} value={summary?.total_events ?? 0} tone="blue" detail="+ live sync" />
            <KpiCard label={t.unknownEvents} value={summary?.unknown_events ?? 0} tone="red" detail="watchlist" />
            <KpiCard label={t.recentEvents} value={summary?.recent_events ?? 0} tone="amber" detail="7 days" />
            <KpiCard label={t.todayPeople} value={summary?.today_known_persons ?? 0} tone="green" detail="today" />
          </section>

          <div className="sentinel-main-grid">
            <section className="sentinel-live-section">
              <div className="sentinel-section-heading">
                <h2>
                  <Camera className="h-5 w-5 text-[#b3c5ff]" />
                  {t.live}
                </h2>
                <div className="sentinel-badges">
                  <span>{t.gridView}</span>
                  <span className="sentinel-badge-live">{t.liveHd}</span>
                </div>
              </div>
              <p className="sentinel-live-hint">{t.liveHint}</p>
              <div className="sentinel-camera-grid">
                {[0, 1, 2, 3].map((_, index) => (
                  <CameraPlaceholder
                    key={index}
                    index={index + 1}
                    language={language}
                    title={topCameras[index]?.camera_name ?? `${t.cameraSlot} ${index + 1}`}
                  />
                ))}
              </div>
            </section>

            <aside className="sentinel-side-column">
              <section className="sentinel-panel sentinel-alert-panel">
                <div className="sentinel-alert-title">
                  <h2>
                    <AlertTriangle className="h-5 w-5" />
                    {t.anomaly}
                  </h2>
                  <span>{t.priority}</span>
                </div>
                <div className="sentinel-alert-card">
                  <div>
                    <strong>{t.anomalyTitle}</strong>
                    <time>{new Date().toLocaleTimeString(language === 'zh' ? 'zh-CN' : 'en-US')}</time>
                  </div>
                  <p>{t.anomalyBody}</p>
                  <div className="sentinel-alert-actions">
                    <button type="button">
                      <Lock className="h-4 w-4" />
                      {t.lockdown}
                    </button>
                    <button type="button">{t.dismiss}</button>
                  </div>
                </div>
              </section>

              <section className="sentinel-panel sentinel-log-panel">
                <div className="sentinel-panel-title">
                  <Users className="h-4 w-4" />
                  {t.personLogs}
                </div>
                <div className="sentinel-person-list">
                  {personRanking.length === 0 && <div className="sentinel-empty">{t.emptyRanking}</div>}
                  {personRanking.map((person) => (
                    <div className="sentinel-person-row" key={person.person_id}>
                      <div className="sentinel-avatar">
                        <UserRound className="h-4 w-4" />
                      </div>
                      <div>
                        <strong>{person.person_name}</strong>
                        <span>{person.department ?? t.departmentFallback}</span>
                      </div>
                      <em>{person.event_count}</em>
                    </div>
                  ))}
                </div>
              </section>
            </aside>
          </div>

          <section className="sentinel-analytics-grid">
            <article className="sentinel-panel sentinel-chart-panel">
              <div className="sentinel-panel-title">
                <BarChart3 className="h-4 w-4" />
                {t.cameraRanking}
              </div>
              <div className="sentinel-chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ranking}>
                    <CartesianGrid stroke="#303642" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="camera_name" tick={{ fill: '#8c90a1', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis allowDecimals={false} tick={{ fill: '#8c90a1', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: '#191c22', border: '1px solid #424656', color: '#e1e2eb' }} />
                    <Bar dataKey="event_count" name={t.eventCount} fill="#0066ff" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </article>

            <article className="sentinel-panel sentinel-chart-panel">
              <div className="sentinel-panel-title">
                <ShieldAlert className="h-4 w-4" />
                {t.unknownTrend}
              </div>
              <div className="sentinel-chart-box">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trend}>
                    <CartesianGrid stroke="#303642" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fill: '#8c90a1', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis allowDecimals={false} tick={{ fill: '#8c90a1', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: '#191c22', border: '1px solid #424656', color: '#e1e2eb' }} />
                    <Line type="monotone" dataKey="unknown_count" name={t.unknownCount} stroke="#ffb4aa" strokeWidth={3} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </article>

            <article className="sentinel-panel sentinel-camera-activity">
              <div className="sentinel-panel-title">
                <Camera className="h-4 w-4" />
                {t.cameraActivity}
              </div>
              <div className="sentinel-activity-table">
                {cameraActivity.length === 0 && <div className="sentinel-empty">{t.emptyCamera}</div>}
                {cameraActivity.map((camera) => (
                  <div className="sentinel-activity-row" key={camera.camera_id}>
                    <div>
                      <strong>{camera.camera_name}</strong>
                      <span>{camera.status}</span>
                    </div>
                    <span>{camera.event_count}</span>
                    <span>{camera.unknown_count}</span>
                    <time>{formatEventTime(camera.last_event_time, language)}</time>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <section className="sentinel-map-panel">
            <div className="sentinel-section-heading">
              <h2>
                <Globe2 className="h-5 w-5 text-[#b3c5ff]" />
                {t.globalMap}
              </h2>
              <div className="sentinel-map-legend">
                <span><i className="bg-[#0066ff]" />{t.onlineNode}</span>
                <span><i className="bg-[#de211c]" />{t.activeThreat}</span>
              </div>
            </div>
            <div className="sentinel-map-canvas">
              <span className="sentinel-map-dot sentinel-map-dot-blue" />
              <span className="sentinel-map-dot sentinel-map-dot-red" />
              <span className="sentinel-map-dot sentinel-map-dot-blue sentinel-map-dot-delay" />
            </div>
          </section>
        </>
      )}
    </div>
  );
}
