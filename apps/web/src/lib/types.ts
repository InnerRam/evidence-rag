export type DocumentItem = {
  id: string;
  filename: string;
  sha256: string;
  size_bytes: number;
  status: "processing" | "available" | "failed";
  page_count: number;
  chunk_count: number;
  embedding_tokens: number;
  processing_ms: number;
  error_message: string | null;
  created_at: string;
  deduplicated?: boolean;
};

export type Citation = {
  id: string;
  document_id: string;
  document: string;
  page: number | null;
  section: string | null;
  score: number;
  snippet: string;
};

export type QueryResponse = {
  query_id: string;
  session_id: string;
  answer: string;
  evidence_sufficient: boolean;
  citations: Citation[];
  metrics: {
    retrieval_ms: number;
    generation_ms: number;
    total_ms: number;
    embedding_tokens: number;
    input_tokens: number;
    output_tokens: number;
    estimated_cost_usd: number | null;
  };
  provider: string;
};

export type PublicConfig = {
  provider: string;
  max_upload_bytes: number;
  allowed_extensions: string[];
  default_top_k: number;
  max_top_k: number;
};
