import React, { useState } from 'react';
import { ShieldCheck, Lock, AlertCircle } from 'lucide-react';

interface AdminLoginProps {
  apiUrl: string;
  onLoginSuccess: (token: string, initialLogs: any[]) => void;
}

export default function AdminLogin({ apiUrl, onLoginSuccess }: AdminLoginProps) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const token = btoa(`${username.trim()}:${password}`);

    try {
      const res = await fetch(apiUrl, {
        headers: { Authorization: `Basic ${token}` },
      });

      if (res.status === 401) {
        setError('Invalid username or password (Default: admin / qatar2026)');
        return;
      }

      if (res.ok) {
        const data = await res.json();
        onLoginSuccess(token, data.logs || []);
      }
    } catch {
      setError('Cannot connect to FastAPI backend on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4 font-sans">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-800 overflow-hidden">
        <div className="bg-qatar-maroon text-white p-6 text-center space-y-2">
          <ShieldCheck className="w-10 h-10 text-qatar-gold mx-auto" />
          <h1 className="font-extrabold text-lg">Enterprise Admin Monitor Login</h1>
          <p className="text-xs text-qatar-gold/90">HTTP Basic Auth Required</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 text-rose-600 font-semibold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="font-bold block mb-1">Admin Username</label>
            <input
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
            />
          </div>

          <div>
            <label className="font-bold block mb-1">Admin Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-qatar-maroon text-white font-extrabold flex items-center justify-center gap-2"
          >
            <Lock className="w-4 h-4 text-qatar-gold" />
            <span>{loading ? 'Signing in...' : 'Sign In'}</span>
          </button>

          <p className="text-[11px] text-slate-400 text-center">Default: admin / qatar2026</p>
        </form>
      </div>
    </div>
  );
}