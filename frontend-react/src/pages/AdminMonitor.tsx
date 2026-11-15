import React, { useState, useEffect, useCallback } from 'react';
import {
  Cpu, RefreshCw, Trash2, LogOut, ShieldCheck,
  Truck, ShieldAlert, Ban, FileText, Scale,
  Clock, CheckCircle2, Lock, Eye,
} from 'lucide-react';
import { AuditLogEntry, PickupRequestEntry, Language } from '../data/appData';

interface AdminMonitorProps {
  lang: Language;
  setLang: (lang: Language) => void;
  onExit: () => void;
}

const API_BASE = 'http://127.0.0.1:8000';

export default function AdminMonitor({ lang, setLang, onExit }: AdminMonitorProps) {
  const [authHeader, setAuthHeader] = useState<string>(() => sessionStorage.getItem('qm_admin_auth') || '');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');

  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [pickups, setPickups] = useState<PickupRequestEntry[]>([]);
  const [loading, setLoading] = useState(false);

  const isRtl = lang === 'ar';

  const fetchDashboardData = useCallback(async (basicAuth: string) => {
    if (!basicAuth) return;
    setLoading(true);
    try {
      const headers = { Authorization: `Basic ${basicAuth}` };
      const [logsRes, pickupsRes] = await Promise.all([
        fetch(`${API_BASE}/api/audit-logs`, { headers }),
        fetch(`${API_BASE}/api/pickup-requests`, { headers }),
      ]);

      if (logsRes.status === 401 || pickupsRes.status === 401) {
        sessionStorage.removeItem('qm_admin_auth');
        setAuthHeader('');
        setAuthError('Invalid admin credentials');
        return;
      }

      const logsData = await logsRes.json();
      const pickupsData = await pickupsRes.json();
      setLogs(logsData.logs || []);
      setPickups(pickupsData.pickups || []);
      setAuthError('');
    } catch {
      setAuthError('Cannot reach FastAPI backend on http://127.0.0.1:8000');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authHeader) {
      fetchDashboardData(authHeader);
    }
  }, [authHeader, fetchDashboardData]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const encoded = btoa(`${username.trim()}:${password}`);
    sessionStorage.setItem('qm_admin_auth', encoded);
    setAuthHeader(encoded);
  };

  const handleClearLogs = async () => {
    if (!window.confirm('Clear all SQLite diagnostic audit logs?')) return;
    await fetch(`${API_BASE}/api/audit-logs`, {
      method: 'DELETE',
      headers: { Authorization: `Basic ${authHeader}` },
    });
    fetchDashboardData(authHeader);
  };

  if (!authHeader) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4">
        <form
          onSubmit={handleLogin}
          className="w-full max-w-sm bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-lg space-y-4"
        >
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-qatar-maroon text-qatar-gold">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-base text-slate-900 dark:text-white">
                Doha Connect • Admin Login
              </h1>
              <p className="text-xs text-slate-500">dohaconnect.qa Service & Audit Console</p>
            </div>
          </div>

          {authError && (
            <div className="p-2.5 rounded-xl bg-rose-50 text-rose-700 text-xs font-semibold border border-rose-200">
              {authError}
            </div>
          )}

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter admin password"
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <button
              type="submit"
              className="flex-1 py-2.5 rounded-xl bg-qatar-maroon text-white text-xs font-bold"
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={onExit}
              className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs font-bold text-slate-700 dark:text-slate-200"
            >
              Back
            </button>
          </div>
        </form>
      </div>
    );
  }

  const latestLatency = logs.length > 0 ? logs[logs.length - 1].diagnostic.latency_seconds.toFixed(2) : '0.00';
  const piiCount = logs.filter((l) => l.diagnostic.pii_scrubbed).length;
  const blockedCount = logs.filter((l) => l.diagnostic.is_out_of_scope).length;

  return (
    <div dir={isRtl ? 'rtl' : 'ltr'} className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Admin Top Header */}
      <header className="bg-qatar-maroon text-white px-4 sm:px-6 py-3.5 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-qatar-gold text-qatar-maroon">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-extrabold text-sm sm:text-base tracking-tight">
                {isRtl ? 'دوحة كونكت • لوحة مراقبة الصيانة' : 'Doha Connect • Admin Monitor'}
              </h1>
              <p className="text-[11px] text-qatar-gold">
                {isRtl
                  ? 'سجلات التدقيق وطلبات استلام الأجهزة في الدوحة (dohaconnect.qa)'
                  : 'SQLite Audit Logs & Doha Service Center Pickup Queue (dohaconnect.qa)'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchDashboardData(authHeader)}
              className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-bold flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-qatar-gold ${loading ? 'animate-spin' : ''}`} />
              <span>{isRtl ? 'تحديث' : 'Refresh'}</span>
            </button>

            <button
              onClick={handleClearLogs}
              className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-rose-600/80 text-xs font-bold flex items-center gap-1.5"
            >
              <Trash2 className="w-3.5 h-3.5 text-qatar-gold" />
              <span>{isRtl ? 'مسح' : 'Clear'}</span>
            </button>

            <button
              onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}
              className="px-3 py-1.5 rounded-xl bg-black/25 text-xs font-bold text-qatar-gold"
            >
              {lang === 'en' ? 'عربي' : 'EN'}
            </button>

            <button
              onClick={() => {
                sessionStorage.removeItem('qm_admin_auth');
                onExit();
              }}
              className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-bold flex items-center gap-1"
            >
              <LogOut className="w-3.5 h-3.5 text-qatar-gold" />
              <span>{isRtl ? 'خروج' : 'Exit'}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>{isRtl ? 'جلسات التشخيص' : 'Diagnostic Sessions'}</span>
              <FileText className="w-4 h-4 text-blue-600" />
            </div>
            <div className="mt-2 text-2xl font-extrabold">{logs.length}</div>
            <div className="mt-1 text-[11px] text-slate-400">Latest: {latestLatency}s</div>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>{isRtl ? 'طلبات استلام الدوحة' : 'Doha Pickup Requests'}</span>
              <Truck className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="mt-2 text-2xl font-extrabold text-emerald-600">{pickups.length}</div>
            <div className="mt-1 text-[11px] text-slate-400">Consented Contacts</div>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>{isRtl ? 'إخفاء البيانات الشخصية' : 'PII Redactions'}</span>
              <ShieldAlert className="w-4 h-4 text-amber-500" />
            </div>
            <div className="mt-2 text-2xl font-extrabold text-amber-500">{piiCount}</div>
            <div className="mt-1 text-[11px] text-slate-400">QID & Mobile Masked</div>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>{isRtl ? 'حظر خارج النطاق' : 'Guardrail Blocks'}</span>
              <Ban className="w-4 h-4 text-rose-500" />
            </div>
            <div className="mt-2 text-2xl font-extrabold text-rose-500">{blockedCount}</div>
            <div className="mt-1 text-[11px] text-slate-400">Out-of-Scope Blocked</div>
          </div>
        </div>

        {/* Consented Doha Pickup Queue */}
        <section className="rounded-2xl bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-900/50 p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
            <Truck className="w-4 h-4" />
            <span>
              {isRtl
                ? 'طلبات استلام الأجهزة المعتمدة - مركز صيانة دوحة كونكت'
                : 'Consented Doha Connect Doha Service Center Pickup Requests'}
            </span>
          </div>

          {pickups.length === 0 ? (
            <p className="text-xs text-slate-400">No pickup requests submitted yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {pickups.map((p) => (
                <div
                  key={p.id}
                  className="p-4 rounded-xl bg-emerald-50/40 dark:bg-slate-800/60 border border-emerald-200/80 dark:border-slate-700 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="font-bold text-emerald-700 dark:text-emerald-400">{p.id}</span>
                    <span className="text-slate-400">{p.createdAt}</span>
                  </div>
                  <div className="font-bold text-sm">{p.customerName}</div>
                  <div className="text-slate-600 dark:text-slate-300">📞 {p.mobileNumber}</div>
                  <div className="text-slate-600 dark:text-slate-300">📍 {p.dohaLocation}</div>
                  <p className="pt-1 border-t border-slate-200/70 dark:border-slate-700 text-[11px] text-slate-500 line-clamp-2">
                    {p.deviceIssue}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Active 4-Node LangGraph Architecture Strip */}
        <section className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 space-y-3">
          <div className="text-xs font-extrabold uppercase tracking-wider text-slate-600 dark:text-slate-300">
            Active 4-Node LangGraph Pipeline (Doha Connect)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            {[
              { title: '1. Security Sentinel', sub: 'Masks QID & Doha Connect' },
              { title: '2. Supervisor Agent', sub: 'Doha Connect Domain Guardrail' },
              { title: '3. Diagnostic Orchestrator', sub: 'Vision + Law No. 8 RAG' },
              { title: '4. Localization Specialist', sub: 'Layman Bilingual + Pickup' },
            ].map((node, i) => (
              <div
                key={i}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700 flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">{node.title}</div>
                  <div className="text-[11px] text-slate-500">{node.sub}</div>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              </div>
            ))}
          </div>
        </section>

        {/* Full Legal & Vision Audit Trail */}
        <section className="space-y-3">
          <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-600 dark:text-slate-300">
            Enterprise Vision & Qatar Law No. 8 Audit Logs ({logs.length})
          </h2>

          {[...logs].reverse().map((entry) => (
            <div
              key={entry.id}
              className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 space-y-3 text-xs"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 font-mono text-[11px]">
                  <span className="font-bold text-qatar-maroon dark:text-qatar-gold">{entry.id}</span>
                  <span className="text-slate-400">• {entry.timestamp}</span>
                  {entry.diagnostic.pii_scrubbed && (
                    <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">PII Masked</span>
                  )}
                  {entry.diagnostic.is_out_of_scope && (
                    <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-700 font-bold">Blocked</span>
                  )}
                </div>
                <span className="flex items-center gap-1 font-mono text-[11px] text-emerald-600">
                  <Clock className="w-3.5 h-3.5" />
                  {entry.diagnostic.latency_seconds.toFixed(2)}s
                </span>
              </div>

              <div className="font-semibold text-slate-800 dark:text-slate-100">
                Query: <span className="font-normal text-slate-600 dark:text-slate-300">{entry.userQuery}</span>
              </div>

              {entry.images && entry.images.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {entry.images.map((img, idx) => (
                    <img
                      key={idx}
                      src={img.dataUrl}
                      alt={img.name}
                      className="w-16 h-16 object-cover rounded-lg border border-slate-200 dark:border-slate-700"
                    />
                  ))}
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 pt-1">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 space-y-1">
                  <div className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold flex items-center gap-1">
                    <Eye className="w-3.5 h-3.5" />
                    <span>Vision Hardware Assessment</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {entry.diagnostic.hardware_assessment}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 space-y-1">
                  <div className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold flex items-center gap-1">
                    <Scale className="w-3.5 h-3.5" />
                    <span>Qatar Consumer Law Audit (EN)</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                    {entry.diagnostic.response_en}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}