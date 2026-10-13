import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2, Video, AlertTriangle, ShieldAlert,
  Users, Wrench, WifiOff, ArrowUpRight, TrendingUp
} from 'lucide-react';
import {
  AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { api } from '../services/api';

const RISK_COLORS: Record<string, string> = {
  LOW: '#10B981',
  MEDIUM: '#F59E0B',
  HIGH: '#EF4444',
  CRITICAL: '#DC2626',
};

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [riskDist, setRiskDist] = useState<any[]>([]);
  const [compTrend, setCompTrend] = useState<any[]>([]);
  const [rankings, setRankings] = useState<any[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [ovRes, rdRes, ctRes, rkRes, altRes] = await Promise.all([
          api.getOverview(),
          api.getRiskDistribution(),
          api.getComplianceTrend(),
          api.getRankings(),
          api.getAlerts(),
        ]);

        if (ovRes.success) setOverview(ovRes.data);
        if (rdRes.success) setRiskDist(rdRes.data);
        if (ctRes.success) setCompTrend(ctRes.data);
        if (rkRes.success) setRankings(rkRes.data);
        if (altRes.success) setRecentAlerts(altRes.data.slice(0, 5));
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard metrics');
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 font-mono text-sm text-slate-400">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span>Loading Real-Time Compliance Analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 font-mono text-sm">
        Error loading dashboard: {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top SOC Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono uppercase">Total Centres</span>
            <Building2 className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-white font-mono">{overview?.total_centres ?? 0}</span>
            <span className="text-xs text-slate-400">Under MSDE</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono uppercase">Active Cameras</span>
            <Video className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-emerald-400 font-mono">{overview?.active_cameras ?? 0}</span>
            <span className="text-xs text-slate-400">/ {overview?.total_cameras ?? 0} total</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono uppercase">Open Alerts</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-rose-400 font-mono">{overview?.open_alerts ?? 0}</span>
            <span className="text-xs text-slate-400">Action required</span>
          </div>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono uppercase">High Risk Centres</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-amber-400 font-mono">{overview?.high_risk_centres ?? 0}</span>
            <span className="text-xs text-slate-400">Priority review</span>
          </div>
        </div>
      </div>

      {/* Secondary Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#0f172a] border border-gray-800/80 rounded-xl p-3.5 flex items-center space-x-3">
          <div className="p-2 rounded bg-blue-950/60 border border-blue-800/40 text-blue-400">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">Avg Compliance</div>
            <div className="text-base font-bold text-white font-mono">{overview?.average_compliance ?? 0}%</div>
          </div>
        </div>

        <div className="bg-[#0f172a] border border-gray-800/80 rounded-xl p-3.5 flex items-center space-x-3">
          <div className="p-2 rounded bg-amber-950/60 border border-amber-800/40 text-amber-400">
            <Users className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">Attendance Flags</div>
            <div className="text-base font-bold text-amber-300 font-mono">{overview?.total_attendance_discrepancies ?? 0}</div>
          </div>
        </div>

        <div className="bg-[#0f172a] border border-gray-800/80 rounded-xl p-3.5 flex items-center space-x-3">
          <div className="p-2 rounded bg-rose-950/60 border border-rose-800/40 text-rose-400">
            <Wrench className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">Infra Issues</div>
            <div className="text-base font-bold text-rose-300 font-mono">{overview?.total_infrastructure_shortages ?? 0}</div>
          </div>
        </div>

        <div className="bg-[#0f172a] border border-gray-800/80 rounded-xl p-3.5 flex items-center space-x-3">
          <div className="p-2 rounded bg-slate-900 border border-slate-700 text-slate-400">
            <WifiOff className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">Offline Cameras</div>
            <div className="text-base font-bold text-slate-300 font-mono">{overview?.offline_cameras ?? 0}</div>
          </div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Trend Chart */}
        <div className="lg:col-span-2 bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">COMPLIANCE PERFORMANCE TREND</h2>
              <p className="text-xs text-slate-400">Attendance and Infrastructure weighted index</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-900/40 text-blue-300 border border-blue-700/50 rounded">
              HISTORICAL AUDIT
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={compTrend}>
                <defs>
                  <linearGradient id="colorOverall" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="overall_score" name="Overall Compliance" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#colorOverall)" />
                <Area type="monotone" dataKey="attendance_score" name="Attendance Score" stroke="#10B981" strokeWidth={1.5} fillOpacity={0} />
                <Area type="monotone" dataKey="infrastructure_score" name="Infrastructure Score" stroke="#F59E0B" strokeWidth={1.5} fillOpacity={0} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Level Distribution */}
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
          <div className="border-b border-gray-800 pb-3">
            <h2 className="text-sm font-semibold text-white tracking-wide">CENTRE RISK DISTRIBUTION</h2>
            <p className="text-xs text-slate-400">Composite objective classification</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDist}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {riskDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#94A3B8'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-2">
            {riskDist.map((r) => (
              <div key={r.name} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: RISK_COLORS[r.name] || '#94A3B8' }} />
                <span className="text-slate-300">{r.name}:</span>
                <span className="font-semibold text-white">{r.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Secondary Row: Centre Rankings & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Centre Ranking Table */}
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">CENTRE COMPLIANCE RANKING</h2>
              <p className="text-xs text-slate-400">Monitored training institutes ranked by composite index</p>
            </div>
            <Link to="/centres" className="text-xs text-blue-400 hover:text-blue-300 font-mono flex items-center space-x-1">
              <span>VIEW ALL</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-gray-800 text-xs">
            {rankings.map((c) => (
              <div key={c.centre_code} className="py-2.5 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">{c.name}</div>
                  <div className="text-[11px] text-slate-400 font-mono">{c.centre_code} • {c.district}</div>
                </div>
                <div className="flex items-center space-x-3 text-right">
                  <div>
                    <div className="font-mono font-bold text-white">{c.overall_score}%</div>
                    <span
                      className="text-[10px] font-mono px-1.5 py-0.5 rounded font-semibold"
                      style={{
                        backgroundColor: `${RISK_COLORS[c.risk_level]}20`,
                        color: RISK_COLORS[c.risk_level],
                        border: `1px solid ${RISK_COLORS[c.risk_level]}40`
                      }}
                    >
                      {c.risk_level}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Open Alerts */}
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-gray-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">RECENT COMPLIANCE ALERTS</h2>
              <p className="text-xs text-slate-400">Automated computer vision threshold events</p>
            </div>
            <Link to="/alerts" className="text-xs text-blue-400 hover:text-blue-300 font-mono flex items-center space-x-1">
              <span>VIEW ALL ALERTS</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {recentAlerts.length === 0 ? (
              <div className="p-6 text-center text-xs font-mono text-slate-500">
                No active compliance alerts. System compliant.
              </div>
            ) : (
              recentAlerts.map((alt) => (
                <div
                  key={alt.id}
                  className="p-3 bg-[#162032] border border-gray-800/80 rounded-lg space-y-1.5 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span
                      className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded uppercase"
                      style={{
                        backgroundColor: `${RISK_COLORS[alt.severity] || '#94A3B8'}20`,
                        color: RISK_COLORS[alt.severity] || '#94A3B8',
                        border: `1px solid ${RISK_COLORS[alt.severity] || '#94A3B8'}40`
                      }}
                    >
                      {alt.severity} • {alt.alert_type}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(alt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div className="font-medium text-slate-200">{alt.title}</div>
                  <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">{alt.description}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
