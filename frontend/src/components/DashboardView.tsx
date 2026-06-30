/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  ArrowRight,
  BarChart3,
  Bolt,
  BrainCircuit,
  CheckCircle2,
  Database,
  Eye,
  Lock,
  LogIn,
  Network,
  Radar,
  Server,
  Shield,
  ShieldCheck,
  TerminalSquare,
  Workflow,
} from 'lucide-react';

interface DashboardViewProps {
  setActiveTab: (tab: string) => void;
  language?: 'zh' | 'en';
}

const copy = {
  zh: {
    nav: ['首页', '核心能力', '解决方案', '文档'],
    login: '进入控制台',
    deploy: '部署 Sentinel',
    status: '系统状态：最优 // 智能警戒已开启',
    heroTitleA: '未来安防',
    heroTitleB: '从此具备智能',
    heroText:
      '面向高风险场景的 AI 安防编排平台，融合事件中心、NL2SQL、RAG、Agent 与多模态分析，把人脸识别事件流转化为可查询、可解释、可行动的安防情报。',
    primaryCta: '进入安防驾驶舱',
    secondaryCta: '进入视频分析',
    telemetry: '实时遥测',
    capabilities: '核心能力',
    architectureTitle: '认知型安防架构',
    nlqTitle: '自然语言查数',
    nlqText:
      '不用手写复杂 SQL。直接用中文查询人员、摄像头、陌生人事件和趋势，系统自动生成安全只读 SQL 并返回结论。',
    nlqPrompt: '最近7天陌生人出现了多少次？',
    multimodalTitle: '多模态事件理解',
    multimodalText:
      '从日志和事件表扩展到图片、摄像头截图和视觉描述，帮助系统理解异常背后的现场上下文。',
    ragTitle: 'RAG 安防知识库',
    ragText:
      '接入制度、应急流程、摄像头说明和人员档案，让 AI 回答基于组织自己的知识，而不是泛泛聊天。',
    zeroHallucination: '基于私有知识检索',
    privateIsolation: '本地数据闭环',
    opTitle: '运行架构',
    opText: '从原始识别事件到智能分析结论，系统按工程化链路组织数据、模型和工具调用。',
    ingest: '数据接入',
    ingestSub: 'PostgreSQL / 摄像头事件',
    core: '智能核心',
    coreSub: 'LLM / RAG / Agent',
    intel: '行动情报',
    intelSub: '异常分析 / 报告生成',
    trustTitle: '默认工程化与安全',
    trustText: '面向论文展示和面试讲解，强调可部署、可解释、可扩展的工程能力。',
    trust: ['只读 SQL 防护', '本地数据存储', '接口化事件中心', '可复现实验'],
    footer: 'AI 安防分析平台。人脸识别事件流驱动的智能安防系统。',
  },
  en: {
    nav: ['Home', 'Features', 'Solutions', 'Documentation'],
    login: 'Operator Login',
    deploy: 'Deploy Sentinel',
    status: 'System status: optimal // vigilance engaged',
    heroTitleA: 'The Future of Vigilance',
    heroTitleB: 'is Intelligent',
    heroText:
      'Enterprise-grade AI security orchestration that turns face-recognition events into queryable, explainable, and actionable intelligence with NL2SQL, RAG, agents, and multimodal analysis.',
    primaryCta: 'Open Command Dashboard',
    secondaryCta: 'Open Video Analysis',
    telemetry: 'Real-time Telemetry',
    capabilities: 'Core Capabilities',
    architectureTitle: 'Cognitive Security Architecture',
    nlqTitle: 'Natural Language Query',
    nlqText:
      'Stop writing complex SQL. Ask security questions in natural language and translate intent into safe read-only database queries.',
    nlqPrompt: 'How many unknown-person events happened in the last 7 days?',
    multimodalTitle: 'Multi-modal Reasoning',
    multimodalText:
      'Move beyond logs into screenshots, event images, and visual summaries so the system understands incident context.',
    ragTitle: 'RAG-Powered Insights',
    ragText:
      'Ground every answer in your procedures, camera documentation, personnel records, and historical incident knowledge.',
    zeroHallucination: 'Private knowledge retrieval',
    privateIsolation: 'Local data loop',
    opTitle: 'Operational Architecture',
    opText:
      'From raw recognition events to actionable intelligence, the platform organizes data, models, and tool calls into one clear pipeline.',
    ingest: 'Data Ingest',
    ingestSub: 'PostgreSQL / Camera Events',
    core: 'Neural Core',
    coreSub: 'LLM / RAG / Agent',
    intel: 'Actionable Intel',
    intelSub: 'Anomaly Analysis / Reports',
    trustTitle: 'Fortified by Default',
    trustText:
      'Designed for thesis demos and engineering interviews with deployable, explainable, extensible system capabilities.',
    trust: ['Read-only SQL Guard', 'Local Data Storage', 'Event Center API', 'Reproducible Evals'],
    footer: 'AI security analytics platform powered by face-recognition event streams.',
  },
} as const;

const telemetryLines = [
  'INITIALIZING NEURAL_CORE_v4.2...',
  'SCANNING PERIMETER_DELTA_09...',
  'ANOMALY CHECK: UNKNOWN_EVENTS_TREND',
  'CROSS-REFERENCING RAG_KNOWLEDGE_BASE...',
  'PGSQL -> NL2SQL PIPELINE: READY',
  'STATUS: THREAT_LEVEL_ZERO',
  'STANDBY FOR NEXT CYCLE...',
  'LATENCY: LOCAL_API_SYNC',
];

export default function DashboardView({
  setActiveTab,
  language = 'zh',
}: DashboardViewProps) {
  const t = copy[language];
  const slideIds = ['sentinel-home-hero', 'sentinel-home-capabilities', 'sentinel-home-architecture', 'sentinel-home-trust'];
  const scrollToSlide = (slideId: string) => {
    document.getElementById(slideId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="sentinel-home">
      <nav className="sentinel-home-nav" aria-label="Sentinel homepage navigation">
        <button
          className="sentinel-home-brand"
          onClick={() => setActiveTab('dashboard')}
          type="button"
        >
          SENTINEL AI
        </button>
        <div className="sentinel-home-links">
          {t.nav.map((item, index) => (
            <button
              key={item}
              className={index === 0 ? 'is-active' : ''}
              onClick={() => scrollToSlide(slideIds[Math.min(index, slideIds.length - 1)])}
              type="button"
            >
              {item}
            </button>
          ))}
        </div>
        <div className="sentinel-home-actions">
          <button type="button" onClick={() => setActiveTab('developer')}>
            {t.login}
          </button>
          <button type="button" onClick={() => setActiveTab('security')}>
            {t.deploy}
          </button>
        </div>
      </nav>

      <main className="sentinel-slide-deck">
        <section id="sentinel-home-hero" className="sentinel-home-hero sentinel-slide">
          <div className="sentinel-home-grid-bg" />
          <div className="sentinel-hero-copy">
            <div className="sentinel-status-line">
              <span />
              <strong>{t.status}</strong>
            </div>
            <h1>
              {t.heroTitleA}
              <span>{t.heroTitleB}</span>
            </h1>
            <p>{t.heroText}</p>
            <div className="sentinel-hero-actions">
              <button type="button" onClick={() => setActiveTab('security')}>
                {t.primaryCta}
                <Bolt className="h-4 w-4" />
              </button>
              <button type="button" onClick={() => setActiveTab('video')}>
                {t.secondaryCta}
                <LogIn className="h-4 w-4" />
              </button>
            </div>
          </div>

          <aside className="sentinel-telemetry-panel">
            <div className="sentinel-panel-heading">
              <span>{t.telemetry}</span>
              <BarChart3 className="h-4 w-4" />
            </div>
            <div className="sentinel-telemetry-lines">
              {telemetryLines.map((line, index) => (
                <div
                  key={line}
                  className={
                    index % 3 === 0
                      ? 'text-primary'
                      : index % 3 === 1
                        ? 'text-muted'
                        : 'text-warning'
                  }
                >
                  <span>[ 14:02:{String(11 + index * 2).padStart(2, '0')} ]</span>
                  {line}
                </div>
              ))}
            </div>
          </aside>
        </section>

        <section id="sentinel-home-capabilities" className="sentinel-home-section sentinel-slide">
          <div className="sentinel-section-title">
            <span>{t.capabilities}</span>
            <h2>{t.architectureTitle}</h2>
          </div>

          <div className="sentinel-bento-grid">
            <article className="sentinel-bento-card sentinel-bento-wide">
              <div className="sentinel-scanline" />
              <Database className="h-12 w-12 text-[#b3c5ff]" />
              <h3>{t.nlqTitle}</h3>
              <p>{t.nlqText}</p>
              <code>{t.nlqPrompt}</code>
              <TerminalSquare className="sentinel-watermark" />
            </article>

            <article className="sentinel-bento-card">
              <Eye className="h-12 w-12 text-[#ffc080]" />
              <h3>{t.multimodalTitle}</h3>
              <p>{t.multimodalText}</p>
              <div className="sentinel-fusion-bars">
                <span />
                <span />
                <span />
              </div>
            </article>

            <article className="sentinel-bento-card sentinel-bento-full">
              <div>
                <BrainCircuit className="h-12 w-12 text-[#dae1ff]" />
                <h3>{t.ragTitle}</h3>
                <p>{t.ragText}</p>
                <ul>
                  <li>
                    <CheckCircle2 className="h-4 w-4" />
                    {t.zeroHallucination}
                  </li>
                  <li>
                    <CheckCircle2 className="h-4 w-4" />
                    {t.privateIsolation}
                  </li>
                </ul>
              </div>
              <div className="sentinel-context-visual">
                <Network className="h-16 w-16" />
                <span>PROCESSING CONTEXT_STREAM...</span>
              </div>
            </article>
          </div>
        </section>

        <section id="sentinel-home-architecture" className="sentinel-home-section sentinel-architecture sentinel-slide">
          <div className="sentinel-section-title">
            <h2>{t.opTitle}</h2>
            <p>{t.opText}</p>
          </div>
          <div className="sentinel-flow">
            {[
              { icon: Server, title: t.ingest, sub: t.ingestSub },
              { icon: Workflow, title: t.core, sub: t.coreSub, primary: true },
              { icon: ShieldCheck, title: t.intel, sub: t.intelSub },
            ].map((node) => {
              const Icon = node.icon;
              return (
                <article className={node.primary ? 'is-primary' : ''} key={node.title}>
                  <span>
                    <Icon className="h-10 w-10" />
                  </span>
                  <h3>{node.title}</h3>
                  <p>{node.sub}</p>
                </article>
              );
            })}
          </div>
        </section>

        <section id="sentinel-home-trust" className="sentinel-home-section sentinel-trust sentinel-slide">
          <div>
            <h2>{t.trustTitle}</h2>
            <p>{t.trustText}</p>
          </div>
          <div className="sentinel-trust-grid">
            {[Shield, Lock, Radar, CheckCircle2].map((Icon, index) => (
              <article key={t.trust[index]}>
                <Icon className="h-8 w-8" />
                <span>{t.trust[index]}</span>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer className="sentinel-home-footer">
        <strong>SENTINEL AI</strong>
        <span>{t.footer}</span>
        <button type="button" onClick={() => setActiveTab('security')}>
          {t.primaryCta}
          <ArrowRight className="h-4 w-4" />
        </button>
      </footer>
    </div>
  );
}
