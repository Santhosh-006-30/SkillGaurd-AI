import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User, AlertCircle, EyeOff, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const demoAccounts = [
    { label: 'Admin', username: 'admin', role: 'ADMIN', pwd: 'AdminPassword@2026' },
    { label: 'Monitor', username: 'monitor', role: 'MONITOR', pwd: 'MonitorPassword@2026' },
    { label: 'Inspector', username: 'inspector', role: 'INSPECTOR', pwd: 'InspectorPassword@2026' },
    { label: 'Operator', username: 'operator', role: 'CENTRE_OPERATOR', pwd: 'OperatorPassword@2026' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please provide both username and password.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error?.message || 'Authentication failed');
      }

      login(data.data.access_token, data.data.user);
      navigate('/');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = (acc: typeof demoAccounts[0]) => {
    setUsername(acc.username);
    setPassword(acc.pwd);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col justify-center items-center p-4">
      {/* Privacy Notice Banner */}
      <div className="mb-6 flex items-center space-x-2 px-3 py-1.5 rounded-full bg-blue-950/50 border border-blue-800/40 text-blue-300 text-xs font-mono">
        <EyeOff className="w-3.5 h-3.5 text-blue-400" />
        <span>ZERO FACIAL RECOGNITION ARCHITECTURE — ANONYMOUS VERIFICATION</span>
      </div>

      <div className="w-full max-w-md bg-[#111827] border border-gray-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-800/80 bg-gradient-to-b from-[#182338] to-[#111827]">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="font-bold text-lg text-white tracking-wide">SKILLGUARD AI</h1>
                <span className="text-[10px] font-mono px-1.5 py-0.5 bg-blue-900/60 text-blue-300 border border-blue-700/50 rounded">
                  SIH 26245
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Central Compliance & Oversight Portal
              </p>
            </div>
          </div>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-6">
          {error && (
            <div className="flex items-start space-x-2 p-3 bg-rose-950/40 border border-rose-800/50 rounded-lg text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase mb-1.5">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter system username"
                  className="w-full bg-[#162032] border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-mono"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter secure password"
                  className="w-full bg-[#162032] border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-mono"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-medium rounded-lg text-sm transition-colors flex items-center justify-center space-x-2 shadow-lg shadow-blue-900/30 font-mono"
            >
              {loading ? (
                <span>AUTHENTICATING...</span>
              ) : (
                <>
                  <span>AUTHENTICATE & ENTER</span>
                  <CheckCircle2 className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials */}
          <div className="pt-4 border-t border-gray-800">
            <span className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2">
              Select Demo Role Credential (Simulated):
            </span>
            <div className="grid grid-cols-2 gap-2">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.username}
                  type="button"
                  onClick={() => handleFillDemo(acc)}
                  className="px-2.5 py-1.5 bg-[#172133] hover:bg-[#1e2c45] border border-gray-700/80 rounded-md text-left transition-colors"
                >
                  <div className="text-xs font-semibold text-slate-200">{acc.label}</div>
                  <div className="text-[10px] text-blue-400 font-mono">{acc.role}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-[#0d131f] border-t border-gray-800/80 text-[11px] text-center text-slate-500 font-mono">
          Ministry of Skill Development & Entrepreneurship (MSDE)
        </div>
      </div>
    </div>
  );
}
