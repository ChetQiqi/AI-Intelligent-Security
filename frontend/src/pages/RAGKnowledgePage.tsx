import { useEffect, useState } from 'react';
import {
  Database,
  FileText,
  MessageSquareText,
  Search,
  ShieldCheck,
  Trash2,
  Upload,
} from 'lucide-react';
import {
  deleteKnowledgeDocument,
  listKnowledgeDocuments,
  queryKnowledgeBase,
  uploadKnowledgeDocument,
} from '../api/securityAnalytics';
import PageState from '../components/PageState';
import type { Language } from '../locales';
import type { KnowledgeDocument, RAGQueryResponse } from '../types/api';
import { formatDateTime } from '../utils/format';
import { parseRAGAnswer } from './ragAnswerFormat';
import {
  documentTypeDescriptions,
  documentTypeOptions,
  inferDocumentType,
  type RAGDocumentType,
} from './ragDocumentType';
import { formatRAGOperationError } from './ragKnowledgeMessages';

interface RAGKnowledgePageProps {
  language?: Language;
}

const copy = {
  zh: {
    kicker: 'RAG KNOWLEDGE BASE',
    title: '安防知识库',
    subtitle: '上传制度、人员档案、摄像头说明、访客规定和应急流程，让 AI 基于组织知识回答。',
    documentType: '文档类型',
    upload: '上传并向量化',
    uploading: '处理中...',
    ask: '询问知识库',
    placeholder: '例如：陌生人频繁出现在东门应该怎么处理？',
    query: '检索回答',
    querying: '检索中...',
    documents: '知识库文档',
    chunks: '片段',
    created: '入库时间',
    noDocs: '暂无知识库文档',
    answer: '知识库回答',
    noAnswer: '上传文档并提问后，这里会显示 RAG 回答。',
    sources: '引用来源',
    score: '相似度',
    safety: '检索增强回答仅基于已入库文档生成，适合安防流程问答和处置建议。',
    uploadHint: '选择 Markdown、TXT、PDF 或 DOCX 文件后点击上传。未配置外部模型时，系统会使用本地演示模式完成入库。',
    uploadSuccess: '文档已上传并完成向量化。',
    selectFile: '请先选择一个知识库文件。',
    recommendation: '系统建议',
    typeGuide: '类型说明',
  },
  en: {
    kicker: 'RAG KNOWLEDGE BASE',
    title: 'Security Knowledge Base',
    subtitle:
      'Upload procedures, personnel files, camera manuals, visitor policies, and emergency workflows for grounded answers.',
    documentType: 'Document type',
    upload: 'Upload and Index',
    uploading: 'Processing...',
    ask: 'Ask the Knowledge Base',
    placeholder: 'e.g., What should we do if unknown persons frequently appear at the east gate?',
    query: 'Retrieve Answer',
    querying: 'Retrieving...',
    documents: 'Knowledge Documents',
    chunks: 'chunks',
    created: 'Created',
    noDocs: 'No knowledge documents yet',
    answer: 'Knowledge Answer',
    noAnswer: 'Upload documents and ask a question to see the RAG answer here.',
    sources: 'Sources',
    score: 'Score',
    safety: 'Retrieval-augmented answers are grounded in indexed documents for security procedures and recommendations.',
    uploadHint: 'Select a Markdown, TXT, PDF, or DOCX file. Without external models, local demo mode will index it.',
    uploadSuccess: 'Document uploaded and indexed.',
    selectFile: 'Select a knowledge file first.',
    recommendation: 'Recommendation',
    typeGuide: 'Type guide',
  },
} satisfies Record<Language, Record<string, string>>;

export default function RAGKnowledgePage({ language = 'zh' }: RAGKnowledgePageProps) {
  const t = copy[language];
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [documentType, setDocumentType] = useState<RAGDocumentType>(documentTypeOptions[0]);
  const [file, setFile] = useState<File | null>(null);
  const [typeRecommendation, setTypeRecommendation] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<RAGQueryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const loadDocuments = () => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    listKnowledgeDocuments(controller.signal)
      .then((data) => setDocuments(data.items))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
    return () => controller.abort();
  };

  useEffect(loadDocuments, []);

  const upload = () => {
    if (!file) return;
    const controller = new AbortController();
    setUploading(true);
    setError(null);
    setUploadError(null);
    setUploadMessage(null);
    uploadKnowledgeDocument({ file, documentType }, controller.signal)
      .then(() => {
        setFile(null);
        setUploadMessage(t.uploadSuccess);
        loadDocuments();
      })
      .catch((err: Error) => {
        const message = formatRAGOperationError(err.message, language);
        setUploadError(message);
        setError(message);
      })
      .finally(() => setUploading(false));
  };

  const ask = () => {
    const trimmed = question.trim();
    if (!trimmed) return;
    const controller = new AbortController();
    setQuerying(true);
    setError(null);
    queryKnowledgeBase({ question: trimmed, top_k: 5 }, controller.signal)
      .then(setResult)
      .catch((err: Error) => setError(formatRAGOperationError(err.message, language)))
      .finally(() => setQuerying(false));
  };

  const remove = (documentId: number) => {
    const controller = new AbortController();
    deleteKnowledgeDocument(documentId, controller.signal)
      .then(loadDocuments)
      .catch((err: Error) => setError(err.message));
  };
  const answerBlocks = result ? parseRAGAnswer(result.answer) : [];

  return (
    <div className="rag-knowledge-page">
      <section className="rag-hero-panel">
        <div>
          <p>{t.kicker}</p>
          <h1>{t.title}</h1>
          <span>{t.subtitle}</span>
        </div>
        <div className="rag-safety-chip">
          <ShieldCheck className="h-5 w-5" />
          {t.safety}
        </div>
      </section>

      <PageState loading={loading} error={error} onRetry={loadDocuments} />

      <section className="rag-grid">
        <article className="rag-panel rag-upload-panel">
          <header>
            <Upload className="h-5 w-5" />
            <h2>{t.upload}</h2>
          </header>
          <label>
            <span>{t.documentType}</span>
            <select
              value={documentType}
              onChange={(event) => {
                setDocumentType(event.target.value as RAGDocumentType);
                setTypeRecommendation(null);
              }}
            >
              {documentTypeOptions.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </label>
          <div className="rag-type-guide">
            <strong>{t.typeGuide}</strong>
            <span>{documentTypeDescriptions[documentType]}</span>
          </div>
          <label className="rag-file-drop">
            <FileText className="h-8 w-8" />
            <span>{file?.name ?? '.txt / .md / .pdf / .docx'}</span>
            <input
              type="file"
              accept=".txt,.md,.pdf,.docx"
              onChange={(event) => {
                const selectedFile = event.target.files?.[0] ?? null;
                setFile(selectedFile);
                if (selectedFile) {
                  const recommendation = inferDocumentType(selectedFile.name);
                  setDocumentType(recommendation.type);
                  setTypeRecommendation(recommendation.reason);
                } else {
                  setTypeRecommendation(null);
                }
                setUploadError(null);
                setUploadMessage(null);
              }}
            />
          </label>
          {typeRecommendation && (
            <div className="rag-type-recommendation">
              <strong>{t.recommendation}</strong>
              <span>{typeRecommendation}</span>
            </div>
          )}
          <div className="rag-upload-status" data-kind={uploadError ? 'error' : uploadMessage ? 'success' : 'hint'}>
            {uploadError ?? uploadMessage ?? (file ? t.uploadHint : t.selectFile)}
          </div>
          <button type="button" disabled={!file || uploading} onClick={upload}>
            {uploading ? t.uploading : t.upload}
          </button>
        </article>

        <article className="rag-panel rag-query-panel">
          <header>
            <MessageSquareText className="h-5 w-5" />
            <h2>{t.ask}</h2>
          </header>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={t.placeholder}
            rows={5}
          />
          <button type="button" disabled={querying} onClick={ask}>
            <Search className="h-4 w-4" />
            {querying ? t.querying : t.query}
          </button>
        </article>

        <article className="rag-panel rag-documents-panel">
          <header>
            <Database className="h-5 w-5" />
            <h2>{t.documents}</h2>
          </header>
          <div className="rag-doc-list">
            {documents.length === 0 && <div className="rag-empty">{t.noDocs}</div>}
            {documents.map((document) => (
              <div className="rag-doc-row" key={document.id}>
                <FileText className="h-5 w-5" />
                <div>
                  <strong>{document.filename}</strong>
                  <span>
                    {document.document_type} · {document.chunk_count} {t.chunks} · {t.created}: {formatDateTime(document.created_at)}
                  </span>
                </div>
                <button type="button" onClick={() => remove(document.id)} aria-label="Delete document">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </article>

        <article className="rag-panel rag-answer-panel">
          <header>
            <ShieldCheck className="h-5 w-5" />
            <h2>{t.answer}</h2>
          </header>
          {result ? (
            <div className="rag-answer-content">
              {answerBlocks.map((block, index) => {
                if (block.type === 'heading') {
                  return <h3 key={`${block.type}-${index}`}>{block.content}</h3>;
                }
                if (block.type === 'ordered-item') {
                  const stepNumber = answerBlocks
                    .slice(0, index + 1)
                    .filter((item) => item.type === 'ordered-item').length;
                  return (
                    <div className="rag-answer-step" key={`${block.type}-${index}`}>
                      <span>{stepNumber}</span>
                      <p>{block.content}</p>
                    </div>
                  );
                }
                if (block.type === 'unordered-item') {
                  return (
                    <div className="rag-answer-bullet" key={`${block.type}-${index}`}>
                      <span />
                      <p>{block.content}</p>
                    </div>
                  );
                }
                return <p key={`${block.type}-${index}`}>{block.content}</p>;
              })}
            </div>
          ) : (
            <p>{t.noAnswer}</p>
          )}
          {result && (
            <div className="rag-source-list">
              <h3>{t.sources}</h3>
              {result.sources.map((source) => (
                <div className="rag-source-card" key={source.chunk_id}>
                  <strong>{source.filename}</strong>
                  <span>
                    {source.document_type} · {t.score}: {source.score.toFixed(3)}
                  </span>
                  <p>{source.content}</p>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </div>
  );
}
