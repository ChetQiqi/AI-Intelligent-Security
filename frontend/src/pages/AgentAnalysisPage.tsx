import { useState } from 'react';
import { Bot, FileText, Play, ShieldAlert } from 'lucide-react';
import { analyzeWithAgent } from '../api/securityAnalytics';
import type { Language } from '../locales';
import type { AgentAnalyzeResponse } from '../types/api';
import { formatRiskLevel } from './agentAnalysisFormat';
import { parseRAGAnswer } from './ragAnswerFormat';

interface AgentAnalysisPageProps {
  language?: Language;
}

const copy = {
  zh: {
    kicker: 'AGENT TOOL CALLING',
    title: 'Agent 分析助手',
    subtitle: '让 Agent 自动调用统计、趋势、摄像头、人员排行和知识库工具，生成安防态势报告。',
    question: '分析问题',
    days: '统计窗口',
    run: '开始分析',
    running: '分析中...',
    placeholder: '例如：帮我分析最近一周的异常安防情况。',
    tools: '工具调用',
    findings: '异常发现',
    recommendations: '处理建议',
    report: '分析报告',
    empty: '输入问题并点击开始分析后，这里会显示 Agent 报告。',
    events: '近窗事件',
    unknown: '陌生人累计',
    people: '今日识别人员',
  },
  en: {
    kicker: 'AGENT TOOL CALLING',
    title: 'Agent Analysis Assistant',
    subtitle: 'Let the agent call stats, trends, camera, person ranking, and knowledge tools to produce a security report.',
    question: 'Question',
    days: 'Window',
    run: 'Analyze',
    running: 'Analyzing...',
    placeholder: 'e.g., Analyze abnormal security activity in the last week.',
    tools: 'Tool Calls',
    findings: 'Findings',
    recommendations: 'Recommendations',
    report: 'Report',
    empty: 'Enter a question and run the agent to see the report.',
    events: 'Recent Events',
    unknown: 'Unknown Total',
    people: 'Known Today',
  },
} satisfies Record<Language, Record<string, string>>;

export default function AgentAnalysisPage({ language = 'zh' }: AgentAnalysisPageProps) {
  const t = copy[language];
  const [question, setQuestion] = useState(t.placeholder);
  const [days, setDays] = useState(7);
  const [result, setResult] = useState<AgentAnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reportBlocks = result ? parseRAGAnswer(result.report) : [];

  const runAgent = () => {
    const trimmed = question.trim();
    if (!trimmed) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    analyzeWithAgent({ question: trimmed, days }, controller.signal)
      .then(setResult)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  return (
    <div className="agent-page">
      <section className="agent-hero">
        <div>
          <p>{t.kicker}</p>
          <h1>{t.title}</h1>
          <span>{t.subtitle}</span>
        </div>
        <Bot className="h-12 w-12" />
      </section>

      <section className="agent-console">
        <label>
          <span>{t.question}</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={t.placeholder}
            rows={4}
          />
        </label>
        <label>
          <span>{t.days}</span>
          <select value={days} onChange={(event) => setDays(Number(event.target.value))}>
            <option value={7}>7 days</option>
            <option value={14}>14 days</option>
            <option value={30}>30 days</option>
          </select>
        </label>
        <button type="button" onClick={runAgent} disabled={loading}>
          <Play className="h-4 w-4" />
          {loading ? t.running : t.run}
        </button>
      </section>

      {error && <div className="agent-error">{error}</div>}

      {result ? (
        <section className="agent-grid">
          <article className={`agent-risk-card agent-risk-${result.risk_level}`}>
            <ShieldAlert className="h-7 w-7" />
            <div>
              <span>Risk Level</span>
              <strong>{formatRiskLevel(result.risk_level, language)}</strong>
            </div>
          </article>
          <article className="agent-metric-card">
            <span>{t.events}</span>
            <strong>{result.summary.recent_events.toLocaleString()}</strong>
          </article>
          <article className="agent-metric-card">
            <span>{t.unknown}</span>
            <strong>{result.summary.unknown_events.toLocaleString()}</strong>
          </article>
          <article className="agent-metric-card">
            <span>{t.people}</span>
            <strong>{result.summary.today_known_persons.toLocaleString()}</strong>
          </article>
          <article className="agent-panel agent-report-panel agent-report-panel-wide">
            <header>
              <FileText className="h-5 w-5" />
              <h2>{t.report}</h2>
            </header>
            <div className="agent-report-content">
              {reportBlocks.map((block, index) => {
                if (block.type === 'heading') return <h3 key={index}>{block.content}</h3>;
                if (block.type === 'ordered-item') return <p key={index}>• {block.content}</p>;
                if (block.type === 'unordered-item') return <p key={index}>• {block.content}</p>;
                return <p key={index}>{block.content}</p>;
              })}
            </div>
          </article>
        </section>
      ) : (
        <div className="agent-empty">{t.empty}</div>
      )}
    </div>
  );
}
