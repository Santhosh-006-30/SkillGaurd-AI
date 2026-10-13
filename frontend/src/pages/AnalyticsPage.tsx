import { useEffect, useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { api } from '../services/api';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [compTrend, setCompTrend] = useState<any[]>([]);
  const [alertTrend, setAlertTrend] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [ovRes, ctRes, atRes] = await Promise.all([
          api.getOverview(),
          api.getComplianceTrend(),
          api.getAlertsTrend(),
        ]);
        if (ovRes.success) setOverview(ovRes.data);
        if (ctRes.success) setCompTrend(ctRes.data);
        if (atRes.success) setAlertTrend(atRes.data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-xl font-bold text-white tracking-wide">ANALYTICS & RISK MODELLING</h1>
        <p className="text-xs text-slate-400">
          Aggregated trend evaluation across attendance integrity, infrastructure quotas, and risk classifications
        </p>
      </div>

      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
            <div className="text-[10px] font-mono uppercase text-slate-400">Mean Compliance</div>
            <div className="text-xl font-bold font-mono text-blue-400 mt-1">{overview.average_compliance?.toFixed(1) || 0}%</div>
          </div>
          <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
            <div className="text-[10px] font-mono uppercase text-slate-400">High Risk Centres</div>
            <div className="text-xl font-bold font-mono text-rose-400 mt-1">{overview.high_risk_centres || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
            <div className="text-[10px] font-mono uppercase text-slate-400">Open Incidents</div>
            <div className="text-xl font-bold font-mono text-amber-400 mt-1">{overview.open_alerts || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-[#111827] border border-gray-800">
            <div className="text-[10px] font-mono uppercase text-slate-400">Total Monitored</div>
            <div className="text-xl font-bold font-mono text-white mt-1">{overview.total_centres || 0} Centres</div>
          </div>
        </div>
      )}

      {loading && <div className="text-xs text-slate-400 font-mono">Loading analytics telemetry...</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white">Daily Compliance Trajectory</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={compTrend}>
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} />
                <Area type="monotone" dataKey="overall_score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.2} name="Composite Index" />
                <Area type="monotone" dataKey="attendance_score" stroke="#10B981" fillOpacity={0} name="Attendance Match" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white">Incident Severity Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={alertTrend}>
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="critical_count" fill="#DC2626" name="Critical" />
                <Bar dataKey="high_count" fill="#EF4444" name="High" />
                <Bar dataKey="medium_count" fill="#F59E0B" name="Medium" />
                <Bar dataKey="low_count" fill="#10B981" name="Low" />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
