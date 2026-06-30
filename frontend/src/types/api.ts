export interface HealthResponse {
  status: string;
  database: string;
}

export type EventType = 'known' | 'unknown';

export interface UnknownEventDetail {
  id: number;
  track_id: string | null;
  first_seen_at: string;
  last_seen_at: string;
  occurrence_count: number;
  notes: string | null;
  created_at: string;
}

export interface FaceEvent {
  event_id: string;
  person_id: number | null;
  person_name: string | null;
  camera_id: number | null;
  camera_name: string;
  event_time: string;
  confidence_score: number | string;
  event_type: EventType;
  snapshot_path: string | null;
  created_at: string;
  unknown: UnknownEventDetail | null;
}

export interface EventPage {
  items: FaceEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface StatsSummary {
  total_events: number;
  unknown_events: number;
  recent_events: number;
  today_known_persons: number;
}

export interface CameraRankingItem {
  camera_id: number | null;
  camera_name: string;
  event_count: number;
}

export interface CameraRankingResponse {
  items: CameraRankingItem[];
}

export interface CameraActivityItem {
  camera_id: number;
  camera_name: string;
  status: string;
  event_count: number;
  unknown_count: number;
  last_event_time: string | null;
}

export interface CameraActivityResponse {
  items: CameraActivityItem[];
}

export interface PersonRankingItem {
  person_id: number;
  person_name: string;
  department: string | null;
  event_count: number;
}

export interface PersonRankingResponse {
  items: PersonRankingItem[];
}

export interface UnknownTrendItem {
  date: string;
  unknown_count: number;
}

export interface UnknownTrendResponse {
  items: UnknownTrendItem[];
}

export interface NL2SQLRequest {
  question: string;
}

export interface NL2SQLResponse {
  question: string;
  sql: string;
  rows: Array<Record<string, unknown>>;
  answer: string;
}

export interface KnowledgeDocument {
  id: number;
  filename: string;
  document_type: string;
  content_type: string | null;
  status: string;
  chunk_count: number;
  created_at: string;
}

export interface KnowledgeDocumentListResponse {
  items: KnowledgeDocument[];
}

export interface RAGQueryRequest {
  question: string;
  top_k?: number;
}

export interface RAGSource {
  document_id: number;
  filename: string;
  document_type: string;
  chunk_id: number;
  chunk_index: number;
  content: string;
  score: number;
}

export interface RAGQueryResponse {
  question: string;
  answer: string;
  sources: RAGSource[];
}

export type AgentRiskLevel = 'low' | 'medium' | 'high';

export interface AgentAnalyzeRequest {
  question: string;
  days?: number;
}

export interface AgentToolResult {
  name: string;
  description: string;
  data: Record<string, unknown>;
}

export interface AgentEvidence {
  recent_events: number;
  recent_unknown_events: number;
  top_camera_name: string | null;
  top_camera_events: number;
  top_camera_unknown_events: number;
  top_camera_unknown_rate: number;
  peak_unknown_date: string | null;
  peak_unknown_count: number;
}

export interface AgentAnomaly {
  rule_type: string;
  risk_level: AgentRiskLevel;
  reason: string;
  evidence: Record<string, unknown>;
  recommendation: string;
}

export interface AgentAnalyzeResponse {
  question: string;
  days: number;
  risk_level: AgentRiskLevel;
  summary: StatsSummary;
  unknown_trend: UnknownTrendResponse;
  camera_activity: CameraActivityResponse;
  person_ranking: PersonRankingResponse;
  evidence: AgentEvidence;
  anomalies: AgentAnomaly[];
  knowledge_advice: string;
  findings: string[];
  recommendations: string[];
  tool_results: AgentToolResult[];
  report: string;
}
