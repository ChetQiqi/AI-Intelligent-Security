import axios, { AxiosError } from 'axios';
import type {
  AgentAnalyzeRequest,
  AgentAnalyzeResponse,
  CameraActivityResponse,
  CameraRankingResponse,
  EventPage,
  HealthResponse,
  NL2SQLRequest,
  NL2SQLResponse,
  PersonRankingResponse,
  KnowledgeDocumentListResponse,
  RAGQueryRequest,
  RAGQueryResponse,
  StatsSummary,
  UnknownTrendResponse,
} from '../types/api';

const eventApiClient = axios.create({
  baseURL:
    import.meta.env.VITE_EVENT_API_BASE_URL ??
    'http://127.0.0.1:8001/api/v1',
  timeout: 15000,
});

eventApiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    throw new Error(
      error.response?.data?.detail ??
        error.message ??
        '事件中心请求失败，请确认 8001 服务已启动',
    );
  },
);

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return (await eventApiClient.get<HealthResponse>('/health', { signal })).data;
}

export async function getRecentEvents(
  limit = 50,
  signal?: AbortSignal,
): Promise<EventPage> {
  return (
    await eventApiClient.get<EventPage>('/events/recent', {
      params: { limit, offset: 0 },
      signal,
    })
  ).data;
}

export async function getUnknownEvents(
  limit = 50,
  signal?: AbortSignal,
): Promise<EventPage> {
  return (
    await eventApiClient.get<EventPage>('/events/unknown', {
      params: { limit, offset: 0 },
      signal,
    })
  ).data;
}

export async function getStatsSummary(signal?: AbortSignal): Promise<StatsSummary> {
  return (await eventApiClient.get<StatsSummary>('/stats/summary', { signal })).data;
}

export async function getCameraRanking(
  limit = 5,
  signal?: AbortSignal,
): Promise<CameraRankingResponse> {
  return (
    await eventApiClient.get<CameraRankingResponse>('/stats/cameras/ranking', {
      params: { limit },
      signal,
    })
  ).data;
}

export async function getCameraActivity(
  days = 7,
  signal?: AbortSignal,
): Promise<CameraActivityResponse> {
  return (
    await eventApiClient.get<CameraActivityResponse>('/stats/cameras/activity', {
      params: { days },
      signal,
    })
  ).data;
}

export async function getPersonRanking(
  limit = 5,
  signal?: AbortSignal,
): Promise<PersonRankingResponse> {
  return (
    await eventApiClient.get<PersonRankingResponse>('/stats/persons/ranking', {
      params: { limit },
      signal,
    })
  ).data;
}

export async function getUnknownTrend(
  days = 7,
  signal?: AbortSignal,
): Promise<UnknownTrendResponse> {
  return (
    await eventApiClient.get<UnknownTrendResponse>('/stats/unknown/trend', {
      params: { days },
      signal,
    })
  ).data;
}

export async function queryNL2SQL(
  payload: NL2SQLRequest,
  signal?: AbortSignal,
): Promise<NL2SQLResponse> {
  return (
    await eventApiClient.post<NL2SQLResponse>('/nl2sql/query', payload, { signal })
  ).data;
}

export async function listKnowledgeDocuments(
  signal?: AbortSignal,
): Promise<KnowledgeDocumentListResponse> {
  return (await eventApiClient.get<KnowledgeDocumentListResponse>('/rag/documents', { signal })).data;
}

export async function uploadKnowledgeDocument(
  payload: { file: File; documentType: string },
  signal?: AbortSignal,
) {
  const form = new FormData();
  form.append('file', payload.file);
  form.append('document_type', payload.documentType);
  return (
    await eventApiClient.post('/rag/documents', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      signal,
    })
  ).data;
}

export async function deleteKnowledgeDocument(
  documentId: number,
  signal?: AbortSignal,
): Promise<void> {
  await eventApiClient.delete(`/rag/documents/${documentId}`, { signal });
}

export async function queryKnowledgeBase(
  payload: RAGQueryRequest,
  signal?: AbortSignal,
): Promise<RAGQueryResponse> {
  return (await eventApiClient.post<RAGQueryResponse>('/rag/query', payload, { signal })).data;
}

export async function analyzeWithAgent(
  payload: AgentAnalyzeRequest,
  signal?: AbortSignal,
): Promise<AgentAnalyzeResponse> {
  return (
    await eventApiClient.post<AgentAnalyzeResponse>('/agent/analyze', payload, { signal })
  ).data;
}