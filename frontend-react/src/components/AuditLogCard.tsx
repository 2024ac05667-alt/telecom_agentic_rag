import { MessageSquare, ZoomIn } from 'lucide-react';
import type { DiagnosticResponse } from '../data/appData';

export interface AuditImage {
  name: string;
  dataUrl: string;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  userQuery: string;
  images?: AuditImage[];
  diagnostic: DiagnosticResponse;
}

interface AuditLogCardProps {
  entry: AuditEntry;
  onSelectPhoto: (img: AuditImage) => void;
}

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

export default function AuditLogCard({ entry, onSelectPhoto }: AuditLogCardProps) {
  const { diagnostic } = entry;

  return (
    <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/60 space-y-3 text-xs">
      {/* Top Status Badges */}
      <div className="flex flex-wrap justify-between gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold text-slate-500">{entry.timestamp}</span>
          <span
            className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
              diagnostic.is_out_of_scope
                ? 'bg-rose-500/15 text-rose-600'
                : 'bg-emerald-500/15 text-emerald-600'
            }`}
          >
            {diagnostic.is_out_of_scope ? 'Guardrail Blocked' : 'SLA Verified'}
          </span>
          {diagnostic.pii_scrubbed && (
            <span className="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 font-bold text-[10px]">
              PII Masked
            </span>
          )}
        </div>
        <span className="font-mono text-[11px]">
          Latency: {diagnostic.latency_seconds.toFixed(2)}s
        </span>
      </div>

      {/* Sanitized Customer Query */}
      <div>
        <div className="font-bold text-[11px] text-slate-500 uppercase">Sanitized Query:</div>
        <p className="font-medium mt-0.5">{entry.userQuery}</p>
      </div>

      {/* Uploaded Device Photos */}
      {entry.images && entry.images.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          {entry.images.map((img, idx) => (
            <button
              key={idx}
              onClick={() => onSelectPhoto(img)}
              className="relative rounded-xl overflow-hidden border border-slate-300"
            >
              <img src={img.dataUrl} alt={img.name} className="w-full h-24 object-cover" />
              <ZoomIn className="w-4 h-4 text-white absolute bottom-1 right-1 bg-black/50 rounded p-0.5" />
            </button>
          ))}
        </div>
      )}

      {/* Tier 1: Customer Replies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/25">
          <div className="font-bold text-[11px] text-emerald-700 flex items-center gap-1 mb-1">
            <MessageSquare className="w-3.5 h-3.5" /> Customer Reply (EN)
          </div>
          <p className="whitespace-pre-line">
            <BoldText text={diagnostic.customer_en} />
          </p>
        </div>

        <div dir="rtl" className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/25 text-right arabic-font">
          <div className="font-bold text-[11px] text-emerald-700 mb-1">رد العميل (AR)</div>
          <p className="whitespace-pre-line">
            <BoldText text={diagnostic.customer_ar} />
          </p>
        </div>
      </div>

      {/* Tier 2: Full Legal & Technical Audit */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold mb-1">
            Full Legal & Technical Audit (EN)
          </div>
          <p className="whitespace-pre-line">
            <BoldText text={diagnostic.response_en} />
          </p>
        </div>

        <div dir="rtl" className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-right arabic-font">
          <div className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold mb-1">
            التقرير القانوني الكامل (AR)
          </div>
          <p className="whitespace-pre-line">
            <BoldText text={diagnostic.response_ar} />
          </p>
        </div>
      </div>

      {/* Vision & ChromaDB Grounding */}
      <div className="text-[11px] font-mono text-slate-500 space-y-1">
        <div><strong>Vision:</strong> {diagnostic.hardware_assessment}</div>
        <div><strong>ChromaDB Law:</strong> {diagnostic.policy_context}</div>
      </div>
    </div>
  );
}