import { ConfigProvider, Segmented } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { useState } from 'react';
import AgentAnalysisPage from '../pages/AgentAnalysisPage';
import DashboardPage from '../pages/DashboardPage';
import NL2SQLPage from '../pages/NL2SQLPage';
import RAGKnowledgePage from '../pages/RAGKnowledgePage';
import RecentEventsPage from '../pages/RecentEventsPage';
import UnknownEventsPage from '../pages/UnknownEventsPage';
import type { Language } from '../locales';

type SecurityRoute = 'dashboard' | 'recent' | 'unknown' | 'nl2sql' | 'rag' | 'agent';

interface SecurityAnalyticsViewProps {
  language?: Language;
}

export default function SecurityAnalyticsView({
  language = 'zh',
}: SecurityAnalyticsViewProps) {
  const [route, setRoute] = useState<SecurityRoute>('dashboard');
  const isChinese = language === 'zh';
  const routeOptions = [
    { label: isChinese ? '驾驶舱总览' : 'Cockpit Overview', value: 'dashboard' },
    { label: isChinese ? '最近事件' : 'Recent Events', value: 'recent' },
    { label: isChinese ? '陌生人事件' : 'Unknown Events', value: 'unknown' },
    { label: isChinese ? 'NL2SQL 查数' : 'NL2SQL Center', value: 'nl2sql' },
    { label: isChinese ? 'RAG 知识库' : 'RAG Knowledge', value: 'rag' },
    { label: isChinese ? 'Agent 分析助手' : 'Agent Assistant', value: 'agent' },
  ];

  const page = {
    dashboard: <DashboardPage language={language} />,
    recent: <RecentEventsPage />,
    unknown: <UnknownEventsPage />,
    nl2sql: <NL2SQLPage language={language} />,
    rag: <RAGKnowledgePage language={language} />,
    agent: <AgentAnalysisPage language={language} />,
  }[route];

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#0891b2',
          colorSuccess: '#22c55e',
          colorWarning: '#f59e0b',
          colorBgBase: '#10131a',
          colorBgContainer: '#191c22',
          colorBgElevated: '#272a31',
          colorText: '#e1e2eb',
          colorTextSecondary: '#c2c6d8',
          colorTextTertiary: '#8c90a1',
          colorBorder: '#424656',
          colorBorderSecondary: 'rgba(140, 144, 161, 0.24)',
          borderRadius: 6,
          fontFamily:
            'Fira Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        },
      }}
    >
      <div
        className={`security-analytics-view ${
          route === 'dashboard' ? 'security-analytics-view-command' : ''
        }`}
      >
        <div className="security-analytics-toolbar">
          <div>
            <p className="security-kicker">PostgreSQL Security Event Center</p>
            <h2>{isChinese ? '安防驾驶舱' : 'Security Cockpit'}</h2>
          </div>
          <Segmented
            options={routeOptions}
            value={route}
            onChange={(value) => setRoute(value as SecurityRoute)}
          />
        </div>
        <div className="security-analytics-content">{page}</div>
      </div>
    </ConfigProvider>
  );
}
