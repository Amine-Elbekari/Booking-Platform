import React, { useState, useEffect, useRef, useCallback } from 'react';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import {
  Upload, FileText, Sparkles, Send, AlertCircle,
  CheckCircle2, Clock, XCircle, File, CornerDownLeft,
  Trash2, Loader2
} from 'lucide-react';

/* ── Types ─────────────────────────────────────────────────── */
interface Document {
  id: string;
  filename: string;
  status: string;
  created_at: string;
}
interface Source {
  document_id: string;
  filename: string;
  page?: number;
  row?: number;
}
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  isError?: boolean;
}

/* ── Helpers ────────────────────────────────────────────────── */
const SUGGESTED = [
  'What is the cancellation policy?',
  'What time is check-in and check-out?',
  'Are pets allowed?',
  'What are the villa rules?',
];

function statusBadge(status: string) {
  const map: Record<string, { cls: string; icon: React.ReactNode; label: string }> = {
    READY:      { cls: 'badge badge-success', icon: <CheckCircle2 size={11} strokeWidth={2.5} />, label: 'Ready' },
    FAILED:     { cls: 'badge badge-error',   icon: <XCircle      size={11} strokeWidth={2.5} />, label: 'Failed' },
    UPLOADED:   { cls: 'badge badge-warning', icon: <Clock        size={11} strokeWidth={2.5} />, label: 'Uploaded' },
    EXTRACTING: { cls: 'badge badge-warning', icon: <Clock        size={11} strokeWidth={2.5} />, label: 'Extracting' },
    CHUNKING:   { cls: 'badge badge-warning', icon: <Clock        size={11} strokeWidth={2.5} />, label: 'Chunking' },
    EMBEDDING:  { cls: 'badge badge-warning', icon: <Clock        size={11} strokeWidth={2.5} />, label: 'Embedding' },
  };
  const s = map[status] ?? { cls: 'badge badge-neutral', icon: null, label: status };
  return (
    <span className={s.cls} style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
      {s.icon}{s.label}
    </span>
  );
}

/* ── Component ─────────────────────────────────────────────── */
export default function RagDashboard() {
  const [documents,    setDocuments]    = useState<Document[]>([]);
  const [file,         setFile]         = useState<File | null>(null);
  const [isDragging,   setIsDragging]   = useState(false);
  const [isUploading,  setIsUploading]  = useState(false);
  const [messages,     setMessages]     = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAsking,     setIsAsking]     = useState(false);
  const [deletingId,   setDeletingId]   = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const r = await apiClient.get('/rag/documents');
      setDocuments(r.data);
    } catch { /* silent poll */ }
  }, []);

  useEffect(() => {
    fetchDocuments();
    const iv = setInterval(fetchDocuments, 5000);
    return () => clearInterval(iv);
  }, [fetchDocuments]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAsking]);

  /* Drag-and-drop */
  const onDragOver = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(true); };
  const onDragLeave = () => setIsDragging(false);
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && (dropped.name.endsWith('.pdf') || dropped.name.endsWith('.csv'))) {
      setFile(dropped);
    } else { toast.error('Please drop a PDF or CSV file'); }
  };

  /* Upload */
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    setIsUploading(true);
    try {
      await apiClient.post('/rag/documents', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      toast.success(`${file.name} uploaded!`);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      fetchDocuments();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally { setIsUploading(false); }
  };

  /* Delete */
  const handleDelete = async (docId: string) => {
    setDeletingId(docId);
    try {
      await apiClient.delete(`/rag/documents/${docId}`);
      toast.success('Document deleted');
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete document');
    } finally {
      setDeletingId(null);
      setConfirmDeleteId(null);
    }
  };

  /* Chat */
  const askQuestion = async (question: string) => {
    if (!question.trim() || isAsking) return;
    setInputMessage('');
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setIsAsking(true);
    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }));
      const r = await apiClient.post('/rag/chat', { question, history });
      setMessages(prev => [...prev, { role: 'assistant', content: r.data.answer, sources: r.data.sources }]);
    } catch (err: any) {
      const errorMsg = err.response?.status === 429 
        ? (err.response?.data?.detail || 'The AI assistant has temporarily reached its usage limit. Please try again later.')
        : 'I encountered an error processing your question. Please try again.';
      setMessages(prev => [...prev, {
        role: 'assistant', isError: true,
        content: errorMsg,
      }]);
    } finally { setIsAsking(false); }
  };

  const handleSend = (e: React.FormEvent) => { e.preventDefault(); askQuestion(inputMessage); };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); askQuestion(inputMessage); }
  };

  return (
    <div style={{
      maxWidth: 1280, margin: '0 auto',
      padding: 'clamp(1.5rem, 3vw, 2.5rem) 1.5rem',
      minHeight: 'calc(100vh - 64px)',
      display: 'flex', flexDirection: 'column', gap: '1.75rem',
    }}>
      {/* Page header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '0.375rem' }}>
            <div style={{ width: 34, height: 34, borderRadius: 10, background: 'var(--accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sparkles size={17} color="var(--accent)" strokeWidth={2} />
            </div>
            <h1 style={{ fontSize: '1.5rem' }}>Data AI</h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
            Upload rental documents and ask questions powered by AI.
          </p>
        </div>
        {documents.filter(d => d.status === 'READY').length > 0 && (
          <div className="badge badge-success" style={{ alignSelf: 'flex-start' }}>
            <CheckCircle2 size={12} strokeWidth={2.5} />
            {documents.filter(d => d.status === 'READY').length} document{documents.filter(d => d.status === 'READY').length > 1 ? 's' : ''} ready
          </div>
        )}
      </div>

      {/* Main layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '320px 1fr',
        gap: '1.5rem',
        flex: 1,
        minHeight: 0,
      }} className="rag-grid">

        {/* ── Left: Documents panel ─────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Upload zone */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-primary)' }}>
              Upload document
            </h3>
            <form onSubmit={handleUpload}>
              {/* Drop zone */}
              <label
                onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  gap: '0.5rem', padding: '1.5rem',
                  border: `2px dashed ${isDragging ? 'var(--accent)' : file ? 'var(--success)' : 'var(--border)'}`,
                  borderRadius: 'var(--radius-md)',
                  background: isDragging ? 'var(--accent-light)' : file ? 'var(--success-light)' : 'var(--surface-2)',
                  cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center',
                }}>
                {file ? (
                  <>
                    <CheckCircle2 size={22} color="var(--success)" strokeWidth={2} />
                    <span style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--success)' }}>{file.name}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Ready to upload</span>
                  </>
                ) : (
                  <>
                    <Upload size={20} color={isDragging ? 'var(--accent)' : 'var(--text-muted)'} strokeWidth={2} />
                    <span style={{ fontSize: '0.825rem', fontWeight: 600, color: isDragging ? 'var(--accent)' : 'var(--text-secondary)' }}>
                      Drop file here or <span style={{ color: 'var(--accent)', textDecoration: 'underline' }}>browse</span>
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDF or CSV supported</span>
                  </>
                )}
                <input ref={fileInputRef} type="file" accept=".pdf,.csv" style={{ display: 'none' }}
                  onChange={e => { if (e.target.files?.[0]) setFile(e.target.files[0]); }} />
              </label>

              <button type="submit" disabled={!file || isUploading} className="btn btn-primary btn-full"
                style={{ marginTop: '0.875rem' }}>
                {isUploading ? (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" style={{ animation: 'spin 1s linear infinite' }}>
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.3"/>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
                    </svg>
                    Uploading…
                  </>
                ) : <><Upload size={14} strokeWidth={2.5} /> Upload document</>}
              </button>
            </form>
          </div>

          {/* Document list */}
          <div className="card" style={{ flex: 1, padding: '1.25rem', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--text-primary)' }}>Your documents</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                {documents.length} file{documents.length !== 1 ? 's' : ''}
              </span>
            </div>

            {documents.length === 0 ? (
              <div style={{
                flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                textAlign: 'center', gap: '0.5rem', padding: '2rem 1rem',
              }}>
                <FileText size={28} color="var(--text-muted)" strokeWidth={1.5} style={{ opacity: 0.5 }} />
                <p style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)' }}>No documents yet</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Upload a PDF or CSV to get started</p>
              </div>
            ) : (
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto', flex: 1 }}>
                {documents.map(doc => (
                  <li key={doc.id} style={{
                    display: 'flex', alignItems: 'center', gap: '0.625rem',
                    padding: '0.625rem 0.75rem',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--surface-2)',
                    border: '1px solid var(--border)',
                    transition: 'background 0.15s',
                    minWidth: 0,
                  }}>
                    <div style={{
                      width: 28, height: 28, flexShrink: 0, borderRadius: 6,
                      background: doc.status === 'READY' ? 'var(--success-light)' : doc.status === 'FAILED' ? 'var(--error-light)' : 'var(--accent-light)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <File size={13} color={doc.status === 'READY' ? 'var(--success)' : doc.status === 'FAILED' ? 'var(--error)' : 'var(--accent)'} strokeWidth={2.5} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {doc.filename}
                      </p>
                      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    {statusBadge(doc.status)}
                    
                    {/* Delete logic */}
                    <div style={{ display: 'flex', alignItems: 'center', marginLeft: '0.25rem' }}>
                      {confirmDeleteId === doc.id ? (
                        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                          <button 
                            onClick={() => handleDelete(doc.id)} 
                            disabled={deletingId === doc.id}
                            style={{ background: 'var(--error)', color: '#fff', border: 'none', borderRadius: 4, padding: '4px 8px', fontSize: '0.7rem', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', opacity: deletingId === doc.id ? 0.7 : 1 }}>
                            {deletingId === doc.id && <Loader2 size={10} style={{marginRight: 4, animation: 'spin 1s linear infinite'}} />}
                            Confirm
                          </button>
                          <button 
                            onClick={() => setConfirmDeleteId(null)}
                            disabled={deletingId === doc.id}
                            style={{ background: 'var(--surface-3)', color: 'var(--text-secondary)', border: 'none', borderRadius: 4, padding: '4px 8px', fontSize: '0.7rem', cursor: 'pointer', fontWeight: 600, opacity: deletingId === doc.id ? 0.7 : 1 }}>
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDeleteId(doc.id)}
                          style={{
                            background: 'transparent', border: 'none', color: 'var(--text-muted)',
                            cursor: 'pointer', display: 'flex', padding: '0.375rem', borderRadius: 4, transition: 'all 0.2s'
                          }}
                          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--error)'; (e.currentTarget as HTMLElement).style.background = 'var(--error-light)'; }}
                          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)'; (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
                          title="Delete document"
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* ── Right: Chat panel ─────────────────────────────── */}
        <div className="card" style={{
          display: 'flex', flexDirection: 'column',
          minHeight: 'clamp(500px, 70vh, 800px)',
          overflow: 'hidden',
        }}>
          {/* Chat header */}
          <div style={{
            padding: '1rem 1.25rem',
            borderBottom: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', gap: '0.625rem',
          }}>
            <div style={{ width: 32, height: 32, borderRadius: 10, background: 'linear-gradient(135deg, var(--accent), #A855F7)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sparkles size={15} color="#fff" strokeWidth={2} />
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-primary)' }}>Rental Assistant</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Powered by Gemini · Grounded in your documents</p>
            </div>
          </div>

          {/* Messages area */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>

            {/* Empty state */}
            {messages.length === 0 && (
              <div style={{
                flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                textAlign: 'center', gap: '1.25rem',
              }}>
                <div style={{
                  width: 52, height: 52, borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--accent-light), #F3E8FF)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Sparkles size={22} color="var(--accent)" strokeWidth={2} />
                </div>
                <div>
                  <p style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '0.375rem' }}>
                    Ask your rental assistant
                  </p>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: 340 }}>
                    I'll answer questions based on your uploaded documents.
                  </p>
                </div>

                {/* Suggested questions */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', width: '100%', maxWidth: 420 }}>
                  {SUGGESTED.map(q => (
                    <button key={q} onClick={() => askQuestion(q)} style={{
                      padding: '0.625rem 0.875rem',
                      borderRadius: 'var(--radius-md)',
                      border: '1.5px solid var(--border)',
                      background: 'var(--surface)',
                      color: 'var(--text-secondary)',
                      fontSize: '0.85rem',
                      cursor: 'pointer', textAlign: 'left',
                      transition: 'all 0.15s',
                      display: 'flex', alignItems: 'center', gap: '0.5rem',
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--accent)'; (e.currentTarget as HTMLElement).style.color = 'var(--accent)'; (e.currentTarget as HTMLElement).style.background = 'var(--accent-light)'; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)'; (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)'; (e.currentTarget as HTMLElement).style.background = 'var(--surface)'; }}>
                      <CornerDownLeft size={12} strokeWidth={2} style={{ flexShrink: 0, opacity: 0.5 }} />
                      "{q}"
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Chat messages */}
            {messages.map((msg, i) => (
              <div key={i} style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                animation: 'fadeIn 0.25s ease both',
              }}>
                {msg.role === 'assistant' && (
                  <div style={{
                    width: 28, height: 28, flexShrink: 0, borderRadius: 8,
                    background: msg.isError ? 'var(--error-light)' : 'linear-gradient(135deg, var(--accent), #A855F7)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginRight: '0.625rem', marginTop: 2,
                  }}>
                    {msg.isError
                      ? <AlertCircle size={14} color="var(--error)" strokeWidth={2} />
                      : <Sparkles size={13} color="#fff" strokeWidth={2} />}
                  </div>
                )}

                <div style={{
                  maxWidth: '78%',
                  padding: '0.75rem 1rem',
                  borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  background: msg.role === 'user'
                    ? 'var(--accent)'
                    : msg.isError ? 'var(--error-light)' : 'var(--surface-2)',
                  color: msg.role === 'user' ? '#fff' : msg.isError ? 'var(--error)' : 'var(--text-primary)',
                  border: msg.role === 'user' ? 'none' : `1px solid ${msg.isError ? '#FECACA' : 'var(--border)'}`,
                  fontSize: '0.9rem', lineHeight: 1.6,
                }}>
                  <p style={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.content}</p>

                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ marginTop: '0.625rem', paddingTop: '0.625rem', borderTop: '1px solid rgba(0,0,0,0.08)' }}>
                      <p style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.375rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                        Sources
                      </p>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        {msg.sources.map((src, j) => (
                          <div key={j} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                            <File size={11} color="var(--text-muted)" strokeWidth={2} />
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                              {src.filename}
                              {src.page && ` · p.${src.page}`}
                              {src.row && ` · row ${src.row}`}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isAsking && (
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.625rem', animation: 'fadeIn 0.2s ease' }}>
                <div style={{ width: 28, height: 28, flexShrink: 0, borderRadius: 8, background: 'linear-gradient(135deg, var(--accent), #A855F7)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={13} color="#fff" strokeWidth={2} />
                </div>
                <div style={{
                  padding: '0.75rem 1rem', borderRadius: '16px 16px 16px 4px',
                  background: 'var(--surface-2)', border: '1px solid var(--border)',
                  display: 'flex', gap: '0.375rem', alignItems: 'center',
                }}>
                  {[0, 1, 2].map(i => (
                    <span key={i} style={{
                      width: 7, height: 7, borderRadius: '50%',
                      background: 'var(--text-muted)',
                      display: 'inline-block',
                      animation: `pulse-dot 1.4s ease infinite`,
                      animationDelay: `${i * 0.2}s`,
                    }} />
                  ))}
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input area */}
          <div style={{
            padding: '1rem 1.25rem',
            borderTop: '1px solid var(--border)',
            background: 'var(--surface)',
          }}>
            <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-end' }}>
              <textarea
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your documents…"
                disabled={isAsking}
                rows={1}
                style={{
                  flex: 1,
                  resize: 'none',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '0.9375rem',
                  color: 'var(--text-primary)',
                  background: 'var(--surface-2)',
                  border: '1.5px solid var(--border)',
                  borderRadius: 12,
                  padding: '0.75rem 1rem',
                  outline: 'none',
                  lineHeight: 1.5,
                  maxHeight: 120,
                  overflowY: 'auto',
                  transition: 'border-color 0.15s, box-shadow 0.15s',
                }}
                onFocus={e => { (e.target as HTMLElement).style.borderColor = 'var(--border-focus)'; (e.target as HTMLElement).style.boxShadow = '0 0 0 3px rgba(124,58,237,0.1)'; }}
                onBlur={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; (e.target as HTMLElement).style.boxShadow = 'none'; }}
              />
              <button type="submit" disabled={isAsking || !inputMessage.trim()} style={{
                width: 42, height: 42, flexShrink: 0,
                borderRadius: '50%',
                background: inputMessage.trim() && !isAsking ? 'var(--accent)' : 'var(--surface-2)',
                border: `1.5px solid ${inputMessage.trim() && !isAsking ? 'var(--accent)' : 'var(--border)'}`,
                color: inputMessage.trim() && !isAsking ? '#fff' : 'var(--text-muted)',
                cursor: inputMessage.trim() && !isAsking ? 'pointer' : 'not-allowed',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.15s',
                flexShrink: 0,
              }}>
                <Send size={16} strokeWidth={2.5} />
              </button>
            </form>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.5rem', textAlign: 'center' }}>
              Enter to send · Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (max-width: 768px) {
          .rag-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
