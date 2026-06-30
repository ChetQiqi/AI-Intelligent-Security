import { useMemo, useState } from 'react';
import {
  AlertTriangle,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Code2,
  Copy,
  Database,
  Download,
  Edit3,
  Play,
  Search,
  Sparkles,
  TerminalSquare,
} from 'lucide-react';
import { queryNL2SQL } from '../api/securityAnalytics';
import PageState from '../components/PageState';
import type { Language } from '../locales';
import type { NL2SQLResponse } from '../types/api';
import { stringifyCell } from '../utils/format';

interface NL2SQLPageProps {
  language?: Language;
}

const copy = {
  zh: {
    title: '用自然语言查询你的安防数据',
    subtitle: 'NL2SQL PostgreSQL 引擎。用中文查询人员、摄像头、识别事件和陌生人趋势。',
    placeholder: '例如：最近7天陌生人最多的是哪个摄像头？',
    execute: '执行查询',
    processing: '处理中',
    shortcut: 'CTRL + K',
    recommended: '推荐问题：',
    examples: [
      '最近7天一共有多少条识别事件？',
      '最近7天陌生人出现了多少次？',
      '最近30天哪个摄像头事件最多？',
      '张三最近90天出现了多少次？',
      '最近一周每天的陌生人数量是多少？',
    ],
    chartTitle: '查询分析',
    chartHint: '结果可视化预览',
    tableTitle: '原始查询结果',
    filter: '筛选结果...',
    rows: '行结果',
    empty: '查询没有返回数据',
    sqlTitle: '生成 SQL (PostgreSQL)',
    copySql: '复制 SQL',
    editManual: '手动编辑',
    insightTitle: 'AI 查询结论',
    noInsight: '执行查询后会在这里显示中文结论。',
    anomalyTitle: '安全提示',
    anomalyText: '当前 SQL 已经过只读校验、危险关键字拦截和表白名单限制。',
    report: '生成深度分析报告',
    terminal: '系统终端',
    visualActive: '交互式数据可视化区域',
    detail: '详情',
  },
  en: {
    title: 'Ask Your Data Anything',
    subtitle: 'Natural Language to PostgreSQL Engine. Query security events, cameras, people, and unknown-person trends.',
    placeholder: "e.g., 'Which camera had the most unknown events in the last 7 days?'",
    execute: 'Execute',
    processing: 'Processing',
    shortcut: 'CTRL + K',
    recommended: 'Recommended:',
    examples: [
      'How many recognition events happened in the last 7 days?',
      'How many unknown-person events happened in the last 7 days?',
      'Which camera had the most events in the last 30 days?',
      'How many times did Zhang San appear in the last 90 days?',
      'Show daily unknown-person counts for the last week.',
    ],
    chartTitle: 'Query Analysis',
    chartHint: 'Interactive data visualization active',
    tableTitle: 'Raw Query Results',
    filter: 'Filter results...',
    rows: 'rows',
    empty: 'No rows returned',
    sqlTitle: 'Generated SQL (PostgreSQL)',
    copySql: 'Copy SQL',
    editManual: 'Edit Manually',
    insightTitle: 'AI Query Insight',
    noInsight: 'Run a query to see the natural-language answer here.',
    anomalyTitle: 'Safety Notice',
    anomalyText: 'Generated SQL is protected by read-only validation, dangerous keyword blocking, and table allow-listing.',
    report: 'Generate Deep Investigation Report',
    terminal: 'System Terminal',
    visualActive: 'Interactive data visualization active',
    detail: 'Detail',
  },
} satisfies Record<Language, Record<string, string | string[]>>;

function getNumericBars(rows: Array<Record<string, unknown>>) {
  const first = rows[0];
  if (!first) return [];
  const numberKey = Object.keys(first).find((key) =>
    rows.some((row) => typeof row[key] === 'number'),
  );
  if (!numberKey) return [];
  const labelKey = Object.keys(first).find((key) => key !== numberKey) ?? numberKey;
  const values = rows
    .slice(0, 8)
    .map((row) => ({
      label: stringifyCell(row[labelKey]),
      value: Number(row[numberKey] ?? 0),
    }))
    .filter((item) => Number.isFinite(item.value));
  const max = Math.max(...values.map((item) => item.value), 1);
  return values.map((item) => ({ ...item, height: Math.max(12, (item.value / max) * 88) }));
}

export default function NL2SQLPage({ language = 'zh' }: NL2SQLPageProps) {
  const t = copy[language];
  const examples = t.examples as string[];
  const [question, setQuestion] = useState(examples[0]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<NL2SQLResponse | null>(null);

  const bars = useMemo(() => getNumericBars(result?.rows ?? []), [result]);
  const filteredRows = useMemo(() => {
    const rows = result?.rows ?? [];
    const keyword = filter.trim().toLowerCase();
    if (!keyword) return rows;
    return rows.filter((row) =>
      Object.values(row).some((value) => stringifyCell(value).toLowerCase().includes(keyword)),
    );
  }, [filter, result]);
  const columns = useMemo(() => Object.keys(filteredRows[0] ?? {}), [filteredRows]);

  const submit = (nextQuestion = question) => {
    const trimmed = nextQuestion.trim();
    if (!trimmed) return;
    const controller = new AbortController();
    setQuestion(trimmed);
    setLoading(true);
    setError(null);
    queryNL2SQL({ question: trimmed }, controller.signal)
      .then(setResult)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  const copySql = async () => {
    if (result?.sql) {
      await navigator.clipboard?.writeText(result.sql);
    }
  };

  return (
    <div className="nl2sql-command-center">
      <section className="nl2sql-hero">
        <div className="nl2sql-hero-copy">
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>

        <div className="nl2sql-query-shell">
          <Search className="h-7 w-7 text-[#b3c5ff]" />
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'enter') {
                submit();
              }
            }}
            placeholder={t.placeholder as string}
          />
          <kbd>{t.shortcut}</kbd>
          <button type="button" disabled={loading} onClick={() => submit()}>
            {loading ? t.processing : t.execute}
            <Play className={`h-4 w-4 ${loading ? 'animate-pulse' : ''}`} />
          </button>
        </div>

        <div className="nl2sql-chips">
          <span>{t.recommended}</span>
          {examples.map((item) => (
            <button key={item} type="button" onClick={() => submit(item)}>
              {item}
            </button>
          ))}
        </div>
      </section>

      <PageState loading={false} error={error} />

      <section className="nl2sql-results-grid">
        <div className="nl2sql-main-column">
          <article className="nl2sql-panel nl2sql-visual-panel">
            <header>
              <div>
                <BarChart3 className="h-5 w-5 text-[#b3c5ff]" />
                <h2>{t.chartTitle}</h2>
              </div>
              <div className="nl2sql-panel-actions">
                <button type="button"><BarChart3 className="h-4 w-4" /></button>
                <button type="button"><Download className="h-4 w-4" /></button>
              </div>
            </header>
            <div className="nl2sql-chart-stage">
              <div className="nl2sql-chart-grid" />
              {bars.length > 0 ? (
                <div className="nl2sql-bars">
                  {bars.map((bar, index) => (
                    <div className="nl2sql-bar-wrap" key={`${bar.label}-${index}`}>
                      <span>{bar.value}</span>
                      <div
                        className={index === 0 ? 'nl2sql-bar nl2sql-bar-hot' : 'nl2sql-bar'}
                        style={{ height: `${bar.height}%` }}
                      />
                      <em>{bar.label}</em>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="nl2sql-chart-empty">
                  <Database className="h-12 w-12" />
                  <span>{t.visualActive}</span>
                </div>
              )}
            </div>
          </article>

          <article className="nl2sql-panel nl2sql-table-panel">
            <header>
              <div>
                <Database className="h-5 w-5 text-[#b3c5ff]" />
                <h2>{t.tableTitle}</h2>
                <span>{filteredRows.length} {t.rows}</span>
              </div>
              <input
                value={filter}
                onChange={(event) => setFilter(event.target.value)}
                placeholder={t.filter as string}
              />
            </header>
            <div className="nl2sql-table-scroll">
              {filteredRows.length === 0 ? (
                <div className="nl2sql-empty-state">{t.empty}</div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      {columns.map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                      <th>{t.detail}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRows.slice(0, 12).map((row, index) => (
                      <tr key={index}>
                        {columns.map((column) => (
                          <td key={column}>{stringifyCell(row[column])}</td>
                        ))}
                        <td>
                          <button type="button">{t.detail}</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <footer>
              <span>
                {filteredRows.length > 0
                  ? `1-${Math.min(filteredRows.length, 12)} / ${filteredRows.length}`
                  : `0 / 0`}
              </span>
              <div>
                <ChevronLeft className="h-4 w-4" />
                <ChevronRight className="h-4 w-4" />
              </div>
            </footer>
          </article>
        </div>

        <aside className="nl2sql-side-column">
          <article className="nl2sql-panel nl2sql-sql-panel">
            <header>
              <div>
                <Code2 className="h-5 w-5 text-[#b3c5ff]" />
                <h2>{t.sqlTitle}</h2>
              </div>
            </header>
            <pre>{result?.sql ?? 'SELECT ...'}</pre>
            <footer>
              <button type="button" onClick={copySql}>
                <Copy className="h-4 w-4" />
                {t.copySql}
              </button>
              <button type="button">
                <Edit3 className="h-4 w-4" />
                {t.editManual}
              </button>
            </footer>
          </article>

          <article className="nl2sql-panel nl2sql-insight-panel">
            <div className="nl2sql-side-title">
              <Sparkles className="h-5 w-5" />
              <h2>{t.insightTitle}</h2>
            </div>
            <p>{result?.answer ?? t.noInsight}</p>
            <div className="nl2sql-alert-box">
              <strong>
                <AlertTriangle className="h-4 w-4" />
                {t.anomalyTitle}
              </strong>
              <span>{t.anomalyText}</span>
            </div>
            <button type="button">{t.report}</button>
          </article>

          <article className="nl2sql-panel nl2sql-terminal-panel">
            <header>
              <span>{t.terminal}</span>
              <div>
                <i />
                <i />
                <i />
              </div>
            </header>
            <div>
              <p><span>02:14:02</span> <b>[INF]</b> NL2SQL Engine initialized...</p>
              <p><span>02:14:05</span> <b>[ASK]</b> {question}</p>
              <p><span>02:14:06</span> <b>[SQL]</b> PostgreSQL validation pipeline ready</p>
              <p><span>02:14:07</span> <b>[RES]</b> Returned {result?.rows.length ?? 0} records</p>
              <p><span>02:14:10</span> <b>[REN]</b> Rendering result components...</p>
              <p><span>02:14:11</span> <TerminalSquare className="inline h-3 w-3" /> _</p>
            </div>
          </article>
        </aside>
      </section>
    </div>
  );
}
