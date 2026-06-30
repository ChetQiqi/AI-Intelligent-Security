import type { Language } from '../locales';

export function formatRAGOperationError(message: string, language: Language): string {
  if (message.includes('EMBEDDING_')) {
    return language === 'zh'
      ? `${message}。当前项目已支持本地演示模式；如果仍看到此提示，请重启后端服务让新配置生效。正式环境请配置向量化服务。`
      : `${message}. Local demo mode is available; restart the backend if this still appears. Configure an embedding service for production.`;
  }

  if (message.includes('LLM_')) {
    return language === 'zh'
      ? `${message}。当前项目已支持本地演示回答；如果仍看到此提示，请重启后端服务让新配置生效。正式环境请配置 LLM 服务。`
      : `${message}. Local demo answers are available; restart the backend if this still appears. Configure an LLM service for production.`;
  }

  return message;
}
