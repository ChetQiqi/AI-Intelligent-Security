import type { Language } from '../locales';
import type { AgentRiskLevel } from '../types/api';

const riskLabels: Record<AgentRiskLevel, Record<Language, string>> = {
  high: { zh: '高风险', en: 'High Risk' },
  medium: { zh: '中风险', en: 'Medium Risk' },
  low: { zh: '低风险', en: 'Low Risk' },
};

const toolLabels: Record<string, Record<Language, string>> = {
  query_stats_summary: { zh: '事件总览统计', en: 'Stats Summary' },
  query_unknown_trend: { zh: '陌生人趋势', en: 'Unknown Trend' },
  query_camera_activity: { zh: '摄像头活跃度', en: 'Camera Activity' },
  query_person_ranking: { zh: '人员出现排行', en: 'Person Ranking' },
  query_knowledge_base: { zh: 'RAG 知识库建议', en: 'RAG Advice' },
};

export function formatRiskLevel(level: AgentRiskLevel, language: Language): string {
  return riskLabels[level][language];
}

export function formatToolName(name: string, language: Language): string {
  return toolLabels[name]?.[language] ?? name;
}
