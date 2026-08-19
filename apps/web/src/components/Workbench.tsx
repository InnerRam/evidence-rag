"use client";

import {
  Alert,
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import ContentCopyOutlinedIcon from "@mui/icons-material/ContentCopyOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import FactCheckOutlinedIcon from "@mui/icons-material/FactCheckOutlined";
import QueryStatsOutlinedIcon from "@mui/icons-material/QueryStatsOutlined";
import ShieldOutlinedIcon from "@mui/icons-material/ShieldOutlined";
import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import { askQuestion, getConfig, getDocuments, uploadDocument } from "@/lib/api";
import type { DocumentItem, PublicConfig, QueryResponse } from "@/lib/types";

const SUGGESTED_QUESTIONS = [
  "¿Cómo se utilizaron la IA y Machine Learning durante 2025?",
  "¿Qué servicios y portales digitales se actualizaron o integraron?",
  "¿Cuántas llamadas atendió el call center en 2025 y para qué?",
  "¿Cómo se gestionan y trazan las solicitudes y los reclamos?",
  "¿Cuántos afiliados y empresas afiliadas se reportaron en 2025?",
  "¿Qué servicios ofrece específicamente Los Héroes Digital?",
];


function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function locationLabel(page: number | null, section: string | null): string {
  if (page) return `Página ${page}`;
  return section ?? "Sección no identificada";
}

export default function Workbench() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [sessionId, setSessionId] = useState<string>();
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loadingPage, setLoadingPage] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [notice, setNotice] = useState<string>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    Promise.all([getDocuments(), getConfig()])
      .then(([loadedDocuments, loadedConfig]) => {
        setDocuments(loadedDocuments);
        setConfig(loadedConfig);
        setTopK(loadedConfig.default_top_k);
      })
      .catch((loadError: Error) => setError(loadError.message))
      .finally(() => setLoadingPage(false));
  }, []);

  const availableDocuments = useMemo(
    () => documents.filter((document) => document.status === "available"),
    [documents],
  );

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setError(undefined);
    setNotice(undefined);
    setUploading(true);
    try {
      const uploaded = await uploadDocument(file);
      setDocuments((current) => [uploaded, ...current.filter((item) => item.id !== uploaded.id)]);
      setNotice(
        uploaded.deduplicated
          ? "El contenido ya estaba indexado; reutilizamos la versión existente."
          : `Documento listo: ${uploaded.chunk_count} fragmentos indexados.`,
      );
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "No fue posible cargar el archivo.");
    } finally {
      setUploading(false);
    }
  }

  async function handleQuestion(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setError(undefined);
    setNotice(undefined);
    setAsking(true);
    try {
      const response = await askQuestion(question.trim(), topK, sessionId);
      setResult(response);
      setSessionId(response.session_id);
    } catch (queryError) {
      setError(queryError instanceof Error ? queryError.message : "No fue posible procesar la pregunta.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <Box component="main" sx={{ minHeight: "100vh", pb: 10 }}>
      <Box component="header" sx={{ borderBottom: "1px solid", borderColor: "divider", bgcolor: "rgba(255,255,255,.72)", backdropFilter: "blur(16px)" }}>
        <Container maxWidth="lg">
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ minHeight: 72 }}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Box sx={{ width: 38, height: 38, borderRadius: 2.5, display: "grid", placeItems: "center", color: "white", bgcolor: "primary.main" }}>
                <FactCheckOutlinedIcon />
              </Box>
              <Box>
                <Typography fontWeight={800} letterSpacing="-.02em">EvidenceRAG</Typography>
                <Typography variant="caption" color="text.secondary">IA aplicada · respuestas verificables</Typography>
              </Box>
            </Stack>
            <Chip
              icon={<CheckCircleOutlineIcon />}
              label={config ? `${config.provider === "mock" ? "Demo local" : "OpenAI"} · operativo` : "Conectando"}
              color={config ? "success" : "default"}
              variant="outlined"
              size="small"
            />
          </Stack>
        </Container>
      </Box>

      <Container maxWidth="lg">
        <Box sx={{ pt: { xs: 6, md: 9 }, pb: 5, maxWidth: 820 }}>
          <Chip label="PORTAFOLIO · IA EMPRESARIAL" color="primary" variant="outlined" size="small" />
          <Typography variant="h1" sx={{ mt: 2.5, fontSize: { xs: "2.7rem", md: "4.6rem" }, lineHeight: .98 }}>
            Pregunta. Verifica. Decide.
          </Typography>
          <Typography sx={{ mt: 2.5, fontSize: { xs: "1rem", md: "1.18rem" }, lineHeight: 1.65, color: "text.secondary", maxWidth: 690 }}>
            Asistente documental verificable para consultar información institucional y regulatoria utilizando únicamente fuentes públicas. Cada respuesta expone fuente, ubicación y fragmento; si el respaldo no alcanza, el sistema lo dice.
          </Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2.5} sx={{ mt: 3.5 }}>
            <Stack direction="row" spacing={1} alignItems="center"><ShieldOutlinedIcon color="primary" fontSize="small" /><Typography variant="body2">Sin datos confidenciales</Typography></Stack>
            <Stack direction="row" spacing={1} alignItems="center"><FactCheckOutlinedIcon color="primary" fontSize="small" /><Typography variant="body2">Citas revisables</Typography></Stack>
            <Stack direction="row" spacing={1} alignItems="center"><QueryStatsOutlinedIcon color="primary" fontSize="small" /><Typography variant="body2">Métricas visibles</Typography></Stack>
          </Stack>
        </Box>

        <Alert severity="info" variant="outlined" sx={{ mb: 3 }}>
          Demostración conceptual no oficial construida exclusivamente con información pública. No corresponde a un producto ni implementación de Caja Los Héroes.
        </Alert>

        {(error || notice) && (
          <Alert severity={error ? "error" : "success"} onClose={() => { setError(undefined); setNotice(undefined); }} sx={{ mb: 3 }}>
            {error ?? notice}
          </Alert>
        )}

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "minmax(0, 0.78fr) minmax(0, 1.42fr)" }, gap: 3, alignItems: "start" }}>
          <Card>
            <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
              <Stack direction="row" justifyContent="space-between" alignItems="start">
                <Box>
                  <Typography variant="overline" color="primary.main" fontWeight={800}>01 · Corpus</Typography>
                  <Typography variant="h3" sx={{ fontSize: "1.45rem", mt: .5 }}>Documentos</Typography>
                </Box>
                <Chip label={`${availableDocuments.length} disponibles`} size="small" />
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1.2 }}>
                PDF o texto público, hasta {formatBytes(config?.max_upload_bytes ?? 10 * 1024 * 1024)}.
              </Typography>

              <Button component="label" fullWidth variant="outlined" startIcon={uploading ? <CircularProgress size={18} /> : <CloudUploadOutlinedIcon />} disabled={uploading} sx={{ mt: 3, py: 1.4, borderStyle: "dashed", borderWidth: 1.5 }}>
                {uploading ? "Procesando documento…" : "Cargar documento"}
                <input hidden type="file" accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown" onChange={handleUpload} />
              </Button>

              <Divider sx={{ my: 3 }} />
              {loadingPage ? (
                <Stack spacing={1.5}><Skeleton height={54} /><Skeleton height={54} /></Stack>
              ) : documents.length === 0 ? (
                <Box sx={{ py: 3, textAlign: "center" }}>
                  <DescriptionOutlinedIcon sx={{ color: "text.disabled", fontSize: 42 }} />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>Aún no hay documentos.</Typography>
                </Box>
              ) : (
                <Stack spacing={1.2}>
                  {documents.slice(0, 8).map((document) => (
                    <Stack key={document.id} direction="row" spacing={1.4} alignItems="center" sx={{ p: 1.4, borderRadius: 2, bgcolor: "rgba(0,111,92,.045)" }}>
                      <DescriptionOutlinedIcon color="primary" fontSize="small" />
                      <Box sx={{ minWidth: 0, flex: 1 }}>
                        <Typography variant="body2" fontWeight={700} noWrap title={document.filename}>{document.filename}</Typography>
                        <Typography variant="caption" color="text.secondary">{document.chunk_count} fragmentos · {formatBytes(document.size_bytes)}</Typography>
                      </Box>
                      <Chip label={document.status === "available" ? "Listo" : document.status} color={document.status === "available" ? "success" : "default"} size="small" variant="outlined" />
                    </Stack>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>

          <Stack spacing={3}>
            <Card>
              <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
                <Typography variant="overline" color="primary.main" fontWeight={800}>02 · Consulta</Typography>
                <Typography variant="h3" sx={{ fontSize: "1.45rem", mt: .5 }}>Pregunta sobre la evidencia</Typography>
                <Box component="form" onSubmit={handleQuestion} sx={{ mt: 2.5 }}>
                  <TextField
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ej.: ¿Cuál es la meta del programa y cuándo debe cumplirse?"
                    multiline
                    minRows={3}
                    fullWidth
                    disabled={asking || availableDocuments.length === 0}
                    inputProps={{ maxLength: 2000 }}
                  />
                  <Box sx={{ mt: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>
                      Preguntas sugeridas
                    </Typography>
                    <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1} sx={{ mt: 1 }}>
                      {SUGGESTED_QUESTIONS.map((suggestion) => (
                        <Button
                          key={suggestion}
                          type="button"
                          variant="outlined"
                          size="small"
                          disabled={asking || availableDocuments.length === 0}
                          onClick={() => setQuestion(suggestion)}
                          sx={{ justifyContent: "flex-start", textAlign: "left" }}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </Stack>
                  </Box>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="space-between" alignItems={{ xs: "stretch", sm: "center" }} sx={{ mt: 2 }}>
                    <FormControl size="small" sx={{ minWidth: 130 }}>
                      <InputLabel id="top-k-label">Fuentes</InputLabel>
                      <Select labelId="top-k-label" label="Fuentes" value={topK} onChange={(event) => setTopK(Number(event.target.value))}>
                        {Array.from({ length: Math.min(config?.max_top_k ?? 10, 10) }, (_, index) => index + 1).map((value) => <MenuItem key={value} value={value}>Top {value}</MenuItem>)}
                      </Select>
                    </FormControl>
                    <Button type="submit" variant="contained" size="large" startIcon={asking ? <CircularProgress color="inherit" size={18} /> : <AutoAwesomeOutlinedIcon />} disabled={asking || !question.trim() || availableDocuments.length === 0}>
                      {asking ? "Buscando evidencia…" : "Responder con evidencia"}
                    </Button>
                  </Stack>
                  {availableDocuments.length === 0 && <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1.5 }}>Carga al menos un documento para habilitar las consultas.</Typography>}
                </Box>
              </CardContent>
            </Card>

            {result && (
              <Card sx={{ borderColor: result.evidence_sufficient ? "rgba(0,111,92,.3)" : "rgba(217,119,6,.35)" }}>
                <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
                    <Chip icon={result.evidence_sufficient ? <CheckCircleOutlineIcon /> : <ShieldOutlinedIcon />} label={result.evidence_sufficient ? "Evidencia suficiente" : "Evidencia insuficiente"} color={result.evidence_sufficient ? "success" : "warning"} />
                    <Tooltip title="Copiar respuesta"><IconButton aria-label="Copiar respuesta" onClick={() => navigator.clipboard.writeText(result.answer)}><ContentCopyOutlinedIcon fontSize="small" /></IconButton></Tooltip>
                  </Stack>
                  <Typography sx={{ mt: 2.5, fontSize: "1.08rem", lineHeight: 1.75 }}>{result.answer}</Typography>

                  <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1} sx={{ mt: 2.5 }}>
                    <Chip size="small" label={`${result.metrics.total_ms.toFixed(0)} ms total`} variant="outlined" />
                    <Chip size="small" label={`${result.metrics.retrieval_ms.toFixed(0)} ms retrieval`} variant="outlined" />
                    <Chip size="small" label={`${result.metrics.input_tokens + result.metrics.output_tokens} tokens LLM`} variant="outlined" />
                    <Chip size="small" label={result.metrics.estimated_cost_usd === null ? "Costo: n/a en demo" : `USD ${result.metrics.estimated_cost_usd.toFixed(6)}`} variant="outlined" />
                  </Stack>

                  {result.citations.length > 0 && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="subtitle2" fontWeight={800} sx={{ mb: 1 }}>Fuentes recuperadas</Typography>
                      {result.citations.map((citation) => (
                        <Accordion key={citation.id} disableGutters elevation={0} sx={{ borderTop: "1px solid", borderColor: "divider", "&:before": { display: "none" } }}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Stack direction="row" spacing={1.2} alignItems="center" sx={{ minWidth: 0, width: "100%" }}>
                              <Chip label={citation.id} color="primary" size="small" />
                              <Box sx={{ minWidth: 0, flex: 1 }}><Typography variant="body2" fontWeight={700} noWrap>{citation.document}</Typography><Typography variant="caption" color="text.secondary">{locationLabel(citation.page, citation.section)} · relevancia {(citation.score * 100).toFixed(1)}%</Typography></Box>
                            </Stack>
                          </AccordionSummary>
                          <AccordionDetails><Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7, borderLeft: "3px solid", borderColor: "primary.light", pl: 2 }}>{citation.snippet}</Typography></AccordionDetails>
                        </Accordion>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Stack>
        </Box>
      </Container>
    </Box>
  );
}
