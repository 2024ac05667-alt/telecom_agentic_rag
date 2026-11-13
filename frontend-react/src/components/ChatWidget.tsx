import React, { useState, useRef, useEffect } from 'react';
import {
  Cpu, Send, ShieldAlert, Scale, Ban, Camera, X,
  MessageSquare, Loader2, RotateCcw, ChevronDown,
  Maximize2, Minimize2, Plus,
} from 'lucide-react';
import { LABELS, Language, ChatTurn, DiagnosticResponse } from '../data/appData';
import PickupForm from './PickupForm';

export interface AttachedImage {
  id: string;
  file: File | null;
  preview: string;
  name: string;
}

interface ChatWidgetProps {
  lang: Language;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  query: string;
  setQuery: (q: string) => void;
  attachments: AttachedImage[];
  setAttachments: React.Dispatch<React.SetStateAction<AttachedImage[]>>;
  triggerUploadCount?: number;
}

const API_DIAGNOSE = 'http://127.0.0.1:8000/api/diagnose';

function BoldText({ text }: { text: string }) {
  return (
    <>
      {text.split(/(\*\*.*?\*\*)/g).map((part, i) =>
        part.startsWith('**') && part.endsWith('**') ? (
          <strong key={i} className="font-bold text-slate-900 dark:text-white">
            {part.slice(2, -2)}
          </strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

export default function ChatWidget({
  lang,
  isOpen,
  setIsOpen,
  query,
  setQuery,
  attachments,
  setAttachments,
  triggerUploadCount = 0,
}: ChatWidgetProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [latency, setLatency] = useState('0.00s');
  const [history, setHistory] = useState<ChatTurn[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('qt_chat_history') || '[]');
    } catch {
      return [];
    }
  });

  const fileRef = useRef<HTMLInputElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);

  const text = LABELS[lang];
  const isRtl = lang === 'ar';
  const hasPII = /\b[23]\d{10}\b/.test(query) || /\b[3567]\d{7}\b/.test(query);

  useEffect(() => {
    try {
      localStorage.setItem('qt_chat_history', JSON.stringify(history.slice(-20)));
    } catch {
      // ignore storage quota limits
    }
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, isRunning]);

  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => inputRef.current?.focus(), 80);
      return () => clearTimeout(timer);
    }
  }, [isOpen, query]);

  useEffect(() => {
    if (triggerUploadCount > 0 && isOpen) {
      const timer = setTimeout(() => fileRef.current?.click(), 120);
      return () => clearTimeout(timer);
    }
  }, [triggerUploadCount, isOpen]);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).slice(0, 4 - attachments.length);
    files.forEach((file, idx) => {
      const reader = new FileReader();
      reader.onload = () => {
        setAttachments((prev) => [
          ...prev,
          { id: `${Date.now()}_${idx}`, file, preview: reader.result as string, name: file.name },
        ]);
      };
      reader.readAsDataURL(file);
    });
    if (fileRef.current) fileRef.current.value = '';
  };

  const sendMessage = async () => {
    const cleanText = query.trim();
    if (!cleanText || isRunning) return;

    const currentImages = [...attachments];
    setQuery('');
    setAttachments([]);
    setIsRunning(true);

    const start = performance.now();
    const timer = setInterval(() => {
      setLatency(`${((performance.now() - start) / 1000).toFixed(2)}s`);
    }, 50);

    const lastTurn = history[history.length - 1];
    const promptWithContext = lastTurn
      ? `Previous Question: "${lastTurn.userQuery}" | Previous Verdict: "${lastTurn.diagnostic.customer_en}" | Current Question: ${cleanText}`
      : cleanText;

    try {
      const formData = new FormData();
      formData.append('query', promptWithContext);
      currentImages.forEach((img) => {
        if (img.file) formData.append('images', img.file);
      });

      const res = await fetch(API_DIAGNOSE, { method: 'POST', body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: DiagnosticResponse = await res.json();

      const persistedImages =
        data.image_urls && data.image_urls.length > 0
          ? data.image_urls.map((url, idx) => ({
              preview: url,
              name: currentImages[idx]?.name || `photo_${idx + 1}.jpg`,
            }))
          : currentImages.map((a) => ({ preview: a.preview, name: a.name }));

      setHistory((prev) => [
        ...prev,
        {
          id: `${Date.now()}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          userQuery: cleanText,
          userImages: persistedImages,
          diagnostic: data,
        },
      ]);
    } catch {
      alert('Cannot reach FastAPI backend on http://127.0.0.1:8000');
    } finally {
      clearInterval(timer);
      setIsRunning(false);
    }
  };

  const attachTicketId = (turnId: string, ticketId: string) => {
    setHistory((prev) =>
      prev.map((item) => (item.id === turnId ? { ...item, pickupTicketId: ticketId } : item))
    );
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-4 ${isRtl ? 'left-4 sm:left-6' : 'right-4 sm:right-6'} z-50 px-4 py-3 rounded-full bg-qatar-maroon text-white shadow-2xl border-2 border-qatar-gold flex items-center gap-2 font-bold text-xs`}
      >
        <MessageSquare className="w-4 h-4 text-qatar-gold" />
        <span>{text.floatingBtn}</span>
      </button>
    );
  }

  return (
    <div
      className={
        isExpanded
          ? 'fixed inset-0 z-50 bg-slate-950/60 flex items-center justify-center p-4'
          : `fixed bottom-4 ${isRtl ? 'left-4 sm:left-6' : 'right-4 sm:right-6'} z-50`
      }
    >
      <div
        className={`bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden ${
          isExpanded ? 'w-[94vw] md:w-[80vw] h-[82vh]' : 'w-[92vw] sm:w-[410px] h-[550px] max-h-[82vh]'
        }`}
      >
        {/* Chat Header */}
        <div className="bg-qatar-maroon text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-qatar-gold" />
            <div>
              <div className="font-bold text-xs sm:text-sm">{text.chatTitle}</div>
              <div className="text-[10px] text-qatar-gold">{text.chatSub}</div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {history.length > 0 && (
              <button
                onClick={() => {
                  setHistory([]);
                  localStorage.removeItem('qt_chat_history');
                }}
                className="p-1.5 rounded-lg hover:bg-white/10 text-qatar-gold"
                title="Clear Chat"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}
            <button onClick={() => setIsExpanded(!isExpanded)} className="p-1.5 rounded-lg hover:bg-white/10">
              {isExpanded ? <Minimize2 className="w-3.5 h-3.5 text-qatar-gold" /> : <Maximize2 className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={() => {
                setIsExpanded(false);
                setIsOpen(false);
              }}
              className="p-1.5 rounded-lg hover:bg-white/10"
            >
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3.5 space-y-3 bg-slate-50/70 dark:bg-slate-950/60">
          <div className="p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs">
            {text.chatWelcome}
          </div>

          {history.map((turn) => {
            const isTurnAr = isRtl || /[\u0600-\u06FF]/.test(turn.userQuery);
            return (
              <div key={turn.id} className="space-y-2.5">
                <div className="flex justify-end">
                  <div
                    dir={isTurnAr ? 'rtl' : 'ltr'}
                    className="max-w-[85%] p-2.5 rounded-2xl bg-qatar-maroon text-white text-xs space-y-2"
                  >
                    <p className="whitespace-pre-line">{turn.userQuery}</p>
                    {turn.userImages.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {turn.userImages.map((img, i) => (
                          <img key={i} src={img.preview} alt={img.name} className="w-16 h-16 object-cover rounded-lg" />
                        ))}
                      </div>
                    )}
                    <div className="text-[9px] text-qatar-gold text-end">{turn.timestamp}</div>
                  </div>
                </div>

                <div
                  dir={isTurnAr ? 'rtl' : 'ltr'}
                  className="max-w-[92%] p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs space-y-2"
                >
                  <div className="flex items-center justify-between pb-1 border-b border-slate-100 dark:border-slate-800">
                    <span className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold flex items-center gap-1">
                      {turn.diagnostic.is_out_of_scope ? (
                        <>
                          <Ban className="w-3.5 h-3.5 text-rose-500" />
                          <span className="text-rose-600">{text.blockedBadge}</span>
                        </>
                      ) : (
                        <>
                          <Scale className="w-3.5 h-3.5" />
                          <span>{isTurnAr ? 'رعاية قطر موبايل' : 'Qatar Mobile Care'}</span>
                        </>
                      )}
                    </span>
                    <span className="text-[9px] font-mono bg-emerald-500/10 text-emerald-600 px-1.5 py-0.5 rounded">
                      {turn.diagnostic.latency_seconds.toFixed(2)}s
                    </span>
                  </div>

                  <p className="leading-relaxed whitespace-pre-line">
                    <BoldText text={isTurnAr ? turn.diagnostic.customer_ar : turn.diagnostic.customer_en} />
                  </p>

                  {!turn.diagnostic.is_out_of_scope && (
                    <PickupForm
                      turnId={turn.id}
                      deviceIssue={turn.userQuery}
                      ticketId={turn.pickupTicketId}
                      isArabic={isTurnAr}
                      onSuccess={attachTicketId}
                    />
                  )}
                </div>
              </div>
            );
          })}

          {isRunning && (
            <div className="flex items-center gap-2 p-2.5 rounded-xl bg-white dark:bg-slate-900 border text-xs w-fit">
              <Loader2 className="w-3.5 h-3.5 text-qatar-maroon animate-spin" />
              <span className="font-mono text-[11px]">{latency}</span>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input Bar */}
        <div className="p-2.5 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 space-y-2">
          {hasPII && (
            <div className="text-[10px] text-rose-600 font-bold flex items-center gap-1">
              <ShieldAlert className="w-3 h-3" />
              <span>{isRtl ? 'سيتم إخفاء الرقم الشخصي تلقائياً' : 'QID / Mobile will be auto-masked'}</span>
            </div>
          )}

          {attachments.length > 0 && (
            <div className="flex items-center gap-2 overflow-x-auto">
              {attachments.map((att) => (
                <div key={att.id} className="relative w-12 h-12 rounded-lg overflow-hidden border border-qatar-maroon flex-shrink-0">
                  <img src={att.preview} alt={att.name} className="w-full h-full object-cover" />
                  <button
                    type="button"
                    onClick={() => setAttachments((prev) => prev.filter((x) => x.id !== att.id))}
                    className="absolute top-0 right-0 bg-rose-600 text-white rounded-bl p-0.5"
                  >
                    <X className="w-2.5 h-2.5" />
                  </button>
                </div>
              ))}
              {attachments.length < 4 && (
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="w-12 h-12 rounded-lg border-2 border-dashed border-slate-300 flex items-center justify-center text-slate-400"
                >
                  <Plus className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          <div className="flex items-end gap-1.5">
            <button
              type="button"
              disabled={attachments.length >= 4}
              onClick={() => fileRef.current?.click()}
              className="p-2 bg-slate-100 dark:bg-slate-800 rounded-xl relative"
            >
              <Camera className="w-4 h-4 text-qatar-maroon dark:text-qatar-gold" />
              {attachments.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-qatar-maroon text-qatar-gold text-[9px] font-bold flex items-center justify-center">
                  {attachments.length}
                </span>
              )}
            </button>
            <input ref={fileRef} type="file" accept="image/*" multiple onChange={handleUpload} className="hidden" />

            <textarea
              ref={inputRef}
              rows={1}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder={text.chatPlaceholder}
              className="flex-1 p-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 outline-none resize-none"
            />

            <button
              disabled={isRunning || !query.trim()}
              onClick={sendMessage}
              className="px-3.5 py-2 bg-qatar-maroon disabled:opacity-50 text-white text-xs font-bold rounded-xl flex items-center gap-1"
            >
              <Send className="w-3.5 h-3.5 text-qatar-gold" />
              <span>{text.sendBtn}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}