import React, { useState, useEffect, useCallback } from 'react';
import {
  Cpu,
  Moon,
  Sun,
  Network,
  Scale,
  Database,
  Ban,
  CheckCircle2,
  RotateCcw,
  FileCheck2,
  Activity,
  Lock,
  RefreshCw,
  Image as ImageIcon,
  ShieldCheck,
  LogOut,
  AlertCircle,
  MessageSquare,
  X,
  ZoomIn,
  Truck,
  Phone,
  MapPin,
} from 'lucide-react';
import type { DiagnosticResponse, Language } from './CustomerPortal';

interface StoredAuditImage {
  name: string;
  dataUrl: string;
}

interface AuditEntry {
  id: string;
  timestamp: string;
  userQuery: string;
  images?: StoredAuditImage[];
  hasImage?: boolean;
  diagnostic: DiagnosticResponse;
}

interface PickupTicket {
  id: string;
  createdAt: string;
  customerName: string;
  mobileNumber: string;
  dohaLocation: string;
  deviceIssue: string;
  status: string;
}

const API_LOGS_URL = 'http://127.0.0.1:8000/api/audit-logs';
const API_PICKUPS_URL = 'http://127.0.0.1:8000/api/pickup-requests';
const AUTH_STORAGE_KEY = 'qt_admin_basic_token';

const formatCleanText = (text: string) => {
  if (!text) return null;
  return text.split(/(\*\*.*?\*\*)/g).map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={idx} className="font-bold text-slate-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <React.Fragment key={idx}>{part}</React.Fragment>;
  });
};

export default function AdminMonitor() {
  const [lang, setLang] = useState<Language>('en');
  const [darkMode, setDarkMode] = useState<boolean>(false);

  const [authToken, setAuthToken] = useState<string | null>(() =>
    sessionStorage.getItem(AUTH_STORAGE_KEY)
  );
  const [username, setUsername] = useState<string>('admin');
  const [password, setPassword] = useState<string>('');
  const [authError, setAuthError] = useState<string>('');
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);

  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [pickups, setPickups] = useState<PickupTicket[]>([]);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [lightboxImage, setLightboxImage] = useState<StoredAuditImage | null>(null);

  const isRtl = lang === 'ar';

  const handleLogout = useCallback(() => {
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    setAuthToken(null);
    setPassword('');
    setLogs([]);
    setPickups([]);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setIsAuthenticating(true);

    const encoded = btoa(`${username.trim()}:${password}`);
    try {
      const res = await fetch(API_LOGS_URL, {
        headers: { Authorization: `Basic ${encoded}` },
      });

      if (res.status === 401) {
        setAuthError(
          isRtl
            ? 'اسم المستخدم أو كلمة المرور غير صحيحة'
            : 'Invalid username or password (Default: admin / qatar2026)'
        );
        return;
      }

      if (res.ok) {
        const data = await res.json();
        sessionStorage.setItem(AUTH_STORAGE_KEY, encoded);
        setAuthToken(encoded);
        setLogs(data.logs || []);
      } else {
        setAuthError(`Server returned HTTP ${res.status}`);
      }
    } catch {
      if (username.trim() === 'admin' && password === 'qatar2026') {
        sessionStorage.setItem(AUTH_STORAGE_KEY, encoded);
        setAuthToken(encoded);
      } else {
        setAuthError(
          isRtl
            ? 'تعذر الاتصال بالخادم — بيانات الدخول الافتراضية: admin / qatar2026'
            : 'Backend offline — use default credentials: admin / qatar2026'
        );
      }
    } finally {
      setIsAuthenticating(false);
    }
  };

  const fetchDashboardData = useCallback(async () => {
    if (!authToken) return;
    try {
      setIsSyncing(true);
      const [logsRes, pickupsRes] = await Promise.all([
        fetch(API_LOGS_URL, { headers: { Authorization: `Basic ${authToken}` } }),
        fetch(API_PICKUPS_URL, { headers: { Authorization: `Basic ${authToken}` } }),
      ]);

      if (logsRes.status === 401 || pickupsRes.status === 401) {
        handleLogout();
        return;
      }

      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData.logs || []);
      }
      if (pickupsRes.ok) {
        const pickupsData = await pickupsRes.json();
        setPickups(pickupsData.pickups || []);
      }
    } catch {
      // Backend offline fallback
    } finally {
      setIsSyncing(false);
    }
  }, [authToken, handleLogout]);

  useEffect(() => {
    if (!authToken) return;
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 2000);
    return () => clearInterval(interval);
  }, [authToken, fetchDashboardData]);

  const handleClearLogs = async () => {
    if (!authToken) return;
    try {
      const res = await fetch(API_LOGS_URL, {
        method: 'DELETE',
        headers: { Authorization: `Basic ${authToken}` },
      });
      if (res.status === 401) {
        handleLogout();
        return;
      }
    } catch {
      // ignore
    }
    setLogs([]);
  };

  const toggleDark = () => {
    setDarkMode((prev) => {
      const next = !prev;
      if (next) document.documentElement.classList.add('dark');
      else document.documentElement.classList.remove('dark');
      return next;
    });
  };

  // BASIC AUTH LOGIN GATE
  if (!authToken) {
    return (
      <div
        dir={isRtl ? 'rtl' : 'ltr'}
        className={`min-h-screen flex items-center justify-center bg-slate-950 p-4 ${
          isRtl ? 'arabic-font' : 'font-sans'
        }`}
      >
        <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
          <div className="bg-qatar-maroon text-white p-6 text-center space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-qatar-gold text-qatar-maroon flex items-center justify-center mx-auto shadow">
              <ShieldCheck className="w-7 h-7" />
            </div>
            <h1 className="font-extrabold text-lg">
              {isRtl ? 'دخول لوحة مراقبة الإدارة' : 'Enterprise Admin Monitor Login'}
            </h1>
            <p className="text-xs text-qatar-gold/90">
              {isRtl
                ? 'مطلوب مصادقة أساسية (Basic Auth) للوصول إلى سجلات التدقيق'
                : 'HTTP Basic Authentication Required • Qatar Telecom Compliance Console'}
            </p>
          </div>

          <form onSubmit={handleLogin} className="p-6 space-y-4 text-xs">
            {authError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{authError}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 dark:text-slate-200 block">
                {isRtl ? 'اسم المستخدم' : 'Admin Username'}
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-qatar-maroon"
                placeholder="admin"
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-bold text-slate-700 dark:text-slate-200 block">
                {isRtl ? 'كلمة المرور' : 'Admin Password'}
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-qatar-maroon"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isAuthenticating}
              className="w-full py-3 rounded-xl bg-qatar-maroon hover:bg-qatar-dark disabled:opacity-50 text-white font-extrabold text-xs shadow-md transition flex items-center justify-center gap-2"
            >
              <Lock className="w-4 h-4 text-qatar-gold" />
              <span>
                {isAuthenticating
                  ? isRtl
                    ? 'جاري التحقق...'
                    : 'Authenticating...'
                  : isRtl
                  ? 'تسجيل الدخول'
                  : 'Sign In to Admin Console'}
              </span>
            </button>

            <div className="pt-2 flex items-center justify-between text-[11px] text-slate-400">
              <span>Default: admin / qatar2026</span>
              <button
                type="button"
                onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}
                className="font-bold text-qatar-maroon dark:text-qatar-gold hover:underline"
              >
                {lang === 'en' ? 'عربي' : 'English'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  const totalSessions = logs.length;
  const piiMaskedCount = logs.filter((l) => l.diagnostic.pii_scrubbed).length;
  const blockedCount = logs.filter((l) => l.diagnostic.is_out_of_scope).length;
  const latest = logs[logs.length - 1];

  return (
    <div
      dir={isRtl ? 'rtl' : 'ltr'}
      className={`min-h-screen flex flex-col bg-slate-100 dark:bg-slate-950 text-slate-800 dark:text-slate-100 transition-colors ${
        isRtl ? 'arabic-font' : 'font-sans'
      }`}
    >
      {/* DEDICATED ADMIN MONITOR HEADER */}
      <header className="bg-qatar-dark text-white px-4 md:px-8 py-3 shadow-lg flex items-center justify-between sticky top-0 z-40 border-b border-qatar-gold/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-qatar-gold flex items-center justify-center text-qatar-maroon font-extrabold shadow">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base md:text-lg">
                {isRtl
                  ? 'لوحة مراقبة الإدارة والامتثال - اتصالات قطر'
                  : 'Qatar Telecom • Enterprise Admin Monitor'}
              </span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded-full font-mono font-bold uppercase">
                SQLITE PERSISTENT
              </span>
            </div>
            <p className="text-[11px] text-qatar-gold/90 hidden sm:block">
              {isRtl
                ? 'مراقبة حية للصور، طلبات استلام الأجهزة في الدوحة، والتقارير القانونية'
                : 'Live Inspection of Customer Photos, Doha Pickup Dispatch Queue & Legal Audit Trail'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchDashboardData}
            className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-bold flex items-center gap-1.5 border border-white/15"
            title="Refresh Audit Logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-qatar-gold ${isSyncing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">{isRtl ? 'تحديث' : 'Refresh'}</span>
          </button>

          {logs.length > 0 && (
            <button
              onClick={handleClearLogs}
              className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-bold flex items-center gap-1.5 border border-rose-500/30"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{isRtl ? 'مسح السجل' : 'Clear Logs'}</span>
            </button>
          )}

          <div className="bg-slate-900 p-1 rounded-xl flex items-center border border-qatar-gold/30">
            <button
              onClick={() => setLang('en')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                lang === 'en' ? 'bg-qatar-gold text-qatar-maroon shadow' : 'text-white'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLang('ar')}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold arabic-font transition ${
                lang === 'ar' ? 'bg-qatar-gold text-qatar-maroon shadow' : 'text-white'
              }`}
            >
              عربي
            </button>
          </div>

          <button
            onClick={toggleDark}
            className="w-9 h-9 rounded-xl bg-white/10 hover:bg-white/20 text-qatar-gold flex items-center justify-center border border-white/10"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <button
            onClick={handleLogout}
            className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-rose-500/30 text-white text-xs font-bold flex items-center gap-1.5 border border-white/15"
            title="Sign Out"
          >
            <LogOut className="w-3.5 h-3.5 text-qatar-gold" />
            <span className="hidden md:inline">{isRtl ? 'خروج' : 'Sign Out'}</span>
          </button>
        </div>
      </header>

      {/* MAIN ADMIN DASHBOARD BODY */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs text-slate-500 font-bold">
              <span>{isRtl ? 'إجمالي جلسات التشخيص' : 'Total Diagnostic Sessions'}</span>
              <FileCheck2 className="w-4 h-4 text-blue-500" />
            </div>
            <div className="text-2xl font-extrabold mt-2">{totalSessions}</div>
            <div className="text-[11px] text-slate-400 mt-1 font-mono">
              Latest Latency: {latest ? `${latest.diagnostic.latency_seconds.toFixed(2)}s` : '0.00s'}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs text-slate-500 font-bold">
              <span>{isRtl ? 'طلبات استلام الأجهزة' : 'Doha Pickup Requests'}</span>
              <Truck className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-2xl font-extrabold text-emerald-600 mt-2">{pickups.length}</div>
            <div className="text-[11px] text-slate-400 mt-1">Consented Service Contacts</div>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs text-slate-500 font-bold">
              <span>{isRtl ? 'حماية البيانات الشخصية (PII)' : 'PII Redactions Enforced'}</span>
              <Lock className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-2xl font-extrabold text-amber-600 mt-2">{piiMaskedCount}</div>
            <div className="text-[11px] text-slate-400 mt-1">QID & Qatar Mobile Masked</div>
          </div>

          <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between text-xs text-slate-500 font-bold">
              <span>{isRtl ? 'حظر الطلبات الخارجية' : 'Scope Guardrail Blocks'}</span>
              <Ban className="w-4 h-4 text-rose-500" />
            </div>
            <div className="text-2xl font-extrabold text-rose-600 mt-2">{blockedCount}</div>
            <div className="text-[11px] text-slate-400 mt-1">ScopeOverflow Circuit Breaker</div>
          </div>
        </div>

        {/* Doha Service Center Pickup Dispatch Queue (Consented Contacts) */}
        {pickups.length > 0 && (
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-emerald-500/30 shadow-sm space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
              <Truck className="w-4 h-4" />
              <span>
                {isRtl
                  ? 'طلبات استلام الأجهزة المعتمدة من العملاء (مراكز صيانة الدوحة)'
                  : 'Consented Customer Contact & Doha Courier Pickup Dispatch Queue'}
              </span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
              {pickups.map((p) => (
                <div
                  key={p.id}
                  className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/25 space-y-1.5"
                >
                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="font-bold text-emerald-700 dark:text-emerald-400">{p.id}</span>
                    <span className="text-slate-400">{p.createdAt}</span>
                  </div>
                  <div className="font-extrabold text-sm">{p.customerName}</div>
                  <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-200 font-mono">
                    <Phone className="w-3.5 h-3.5 text-qatar-maroon dark:text-qatar-gold" />
                    <span>{p.mobileNumber}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                    <MapPin className="w-3.5 h-3.5 text-qatar-maroon dark:text-qatar-gold flex-shrink-0" />
                    <span>{p.dohaLocation}</span>
                  </div>
                  {p.deviceIssue && (
                    <p className="text-[11px] text-slate-500 pt-1 border-t border-emerald-500/15 line-clamp-2">
                      {p.deviceIssue}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* LangGraph Pipeline Architecture Status */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
            <Network className="w-4 h-4 text-qatar-maroon dark:text-qatar-gold" />
            <span>
              {isRtl
                ? 'هندسة وكلاء LangGraph النشطة'
                : 'Active Multi-Agent LangGraph Orchestration Pipeline'}
            </span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            {[
              { name: '1. Security Sentinel', desc: 'QID & Qatar Mobile Regex Scrubber' },
              { name: '2. Supervisor Agent', desc: 'Domain Intent & Jailbreak Classifier' },
              { name: '3. Diagnostic Orchestrator', desc: 'Multi-Photo Vision + ChromaDB RAG' },
              { name: '4. Localization Specialist', desc: 'Customer Brief + Pickup Offer + Audit' },
            ].map((node, i) => (
              <div
                key={i}
                className="p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-500/5 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between font-bold mb-1">
                  <span>{node.name}</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                </div>
                <div className="text-[11px] text-slate-500">{node.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Full Audit, Images & Dual-Tier Responses Feed */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Database className="w-4 h-4 text-qatar-maroon dark:text-qatar-gold" />
              <span>
                {isRtl
                  ? 'سجل التدقيق المباشر: جميع الصور، ردود العملاء، والتقارير القانونية'
                  : 'Real-Time Enterprise Audit: All Uploaded Photos, Customer Replies & Full Legal Reports'}
              </span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">
              Polling SQLite /api/audit-logs (2s)
            </span>
          </div>

          {logs.length === 0 ? (
            <div className="text-center py-14 text-xs text-slate-400 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
              <Activity className="w-8 h-8 mx-auto text-slate-300" />
              <div>
                {isRtl
                  ? 'في انتظار استفسارات العملاء من بوابة http://localhost:5173/ ...'
                  : 'Waiting for customer sessions from http://localhost:5173/ ...'}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {[...logs].reverse().map((entry) => {
                const entryImages = entry.images || [];
                return (
                  <div
                    key={entry.id}
                    className="p-4 md:p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/60 space-y-4 text-xs"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-200 dark:border-slate-800">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-500">{entry.timestamp}</span>
                        {entry.diagnostic.is_out_of_scope ? (
                          <span className="px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-600 font-bold text-[10px]">
                            Guardrail Blocked
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 font-bold text-[10px]">
                            SLA Verified
                          </span>
                        )}
                        {entry.diagnostic.pii_scrubbed && (
                          <span className="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 font-bold text-[10px]">
                            PII Masked
                          </span>
                        )}
                        {entryImages.length > 0 && (
                          <span className="px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-600 font-bold text-[10px] inline-flex items-center gap-1">
                            <ImageIcon className="w-3 h-3" /> {entryImages.length} Photo(s) Uploaded
                          </span>
                        )}
                      </div>
                      <span className="font-mono text-[11px] bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded">
                        Latency: {entry.diagnostic.latency_seconds.toFixed(2)}s
                      </span>
                    </div>

                    {/* Customer Query + All Uploaded Images Gallery */}
                    <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
                      <div>
                        <div className="font-bold text-[11px] text-slate-500 uppercase mb-1">
                          Sanitized Customer Inquiry:
                        </div>
                        <p className="text-slate-800 dark:text-slate-100 font-medium">
                          {entry.userQuery}
                        </p>
                      </div>

                      {entryImages.length > 0 && (
                        <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                          <div className="font-bold text-[11px] text-blue-600 dark:text-blue-400 mb-2 flex items-center gap-1.5">
                            <ImageIcon className="w-3.5 h-3.5" />
                            <span>
                              Attached Hardware Photos ({entryImages.length}) — Click any photo to inspect full size:
                            </span>
                          </div>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            {entryImages.map((img, i) => (
                              <button
                                key={i}
                                type="button"
                                onClick={() => setLightboxImage(img)}
                                className="group relative rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-start"
                              >
                                <img
                                  src={img.dataUrl}
                                  alt={img.name}
                                  className="w-full h-28 object-cover group-hover:scale-105 transition"
                                />
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/35 transition flex items-center justify-center">
                                  <ZoomIn className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition" />
                                </div>
                                <div className="px-2 py-1 text-[10px] font-mono truncate bg-white/90 dark:bg-slate-900/90">
                                  {img.name}
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Tier 1: Exact Concise Response Sent to Customer Chat */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                      <div
                        dir="ltr"
                        className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/25 space-y-1 text-left"
                      >
                        <div className="font-bold text-[11px] text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>Customer Chat Reply Delivered (EN)</span>
                        </div>
                        <p className="leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-line">
                          {formatCleanText(entry.diagnostic.customer_en)}
                        </p>
                      </div>

                      <div
                        dir="rtl"
                        className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/25 space-y-1 text-right arabic-font"
                      >
                        <div className="font-bold text-[11px] text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>الرد المختصر المرسل للعميل (AR)</span>
                        </div>
                        <p className="leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-line">
                          {formatCleanText(entry.diagnostic.customer_ar)}
                        </p>
                      </div>
                    </div>

                    {/* Tier 2: Full Bilingual Legal & Technical Audit Reports */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                      <div
                        dir="ltr"
                        className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1.5 text-left"
                      >
                        <div className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold">
                          Full Technical & Legal Audit Report (EN)
                        </div>
                        <p className="leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-line">
                          {formatCleanText(entry.diagnostic.response_en)}
                        </p>
                      </div>

                      <div
                        dir="rtl"
                        className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1.5 text-right arabic-font"
                      >
                        <div className="font-bold text-[11px] text-qatar-maroon dark:text-qatar-gold">
                          التقرير القانوني والفني الكامل (AR)
                        </div>
                        <p className="leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-line">
                          {formatCleanText(entry.diagnostic.response_ar)}
                        </p>
                      </div>
                    </div>

                    {/* Vision Findings + ChromaDB Clauses + Agent Trace */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 pt-1">
                      <div className="space-y-1.5">
                        <div className="font-bold text-slate-700 dark:text-slate-200">
                          Multi-Photo Vision Hardware Assessment:
                        </div>
                        <p className="font-mono text-[11px] text-blue-700 dark:text-blue-400">
                          {entry.diagnostic.hardware_assessment}
                        </p>
                      </div>

                      <div className="space-y-1.5">
                        <div className="font-bold text-amber-800 dark:text-amber-300">
                          ChromaDB Grounded Legal Clause (Law No. 8 / CRA):
                        </div>
                        <p className="font-mono text-[11px] text-amber-700 dark:text-amber-400">
                          {entry.diagnostic.policy_context}
                        </p>
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {entry.diagnostic.agent_history.map((step, i) => (
                            <span
                              key={i}
                              className="text-[10px] font-mono px-2 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700"
                            >
                              {step}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* FULL-SIZE IMAGE INSPECTION LIGHTBOX MODAL */}
      {lightboxImage && (
        <div
          onClick={() => setLightboxImage(null)}
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-xs z-50 flex items-center justify-center p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="max-w-3xl w-full bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-2xl"
          >
            <div className="px-4 py-3 bg-slate-950 text-white flex items-center justify-between text-xs">
              <span className="font-mono font-bold truncate">{lightboxImage.name}</span>
              <button
                onClick={() => setLightboxImage(null)}
                className="p-1 rounded-lg hover:bg-white/10 text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 flex items-center justify-center bg-black">
              <img
                src={lightboxImage.dataUrl}
                alt={lightboxImage.name}
                className="max-h-[75vh] w-auto object-contain rounded-lg"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}