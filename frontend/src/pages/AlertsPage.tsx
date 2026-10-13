import { useEffect, useState } from 'react';
import { Check } from 'lucide-react';
import { api } from '../services/api';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const res = await api.getAlerts({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
      });
      if (res.success) {
        setAlerts(res.data);
      }
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [severityFilter, statusFilter]);

  const handleUpdateStatus = async (alertId: number, newStatus: string) => {
    try {
      const res = await api.updateAlertStatus(alertId, newStatus);
      if (res.success) {
        loadAlerts();
      }
    } catch (err) {
      console.error('Failed to update alert status', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">COMPLIANCE ALERTS & INCIDENTS</h1>
          <p className="text-xs text-slate-400">
            Automated alerts flagged by computer vision threshold analysis
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-[#111827] border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500 font-mono"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#111827] border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500 font-mono"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs font-mono text-slate-400">
          Loading active compliance alerts...
        </div>
      ) : alerts.length === 0 ? (
        <div className="p-12 text-center text-xs font-mono text-slate-500 bg-[#111827] border border-gray-800 rounded-xl">
          No compliance alerts match filter criteria.
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alt) => {
            const isHigh = alt.severity === 'HIGH' || alt.severity === 'CRITICAL';
            return (
              <div
                key={alt.id}
                className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-3 transition-colors hover:border-gray-700"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border uppercase ${
                        isHigh
                          ? 'bg-rose-950/40 text-rose-400 border-rose-800/40'
                          : 'bg-amber-950/40 text-amber-400 border-amber-800/40'
                      }`}
                    >
                      {alt.severity} • {alt.alert_type}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Centre ID: {alt.centre_id}
                    </span>
                  </div>

                  <span className="text-xs font-mono text-slate-500">
                    {new Date(alt.created_at).toLocaleString()}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white tracking-wide">{alt.title}</h3>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">{alt.description}</p>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-gray-800/80 text-xs font-mono">
                  <div className="text-slate-400">
                    Status: <span className="font-bold text-white">{alt.status}</span> • Confidence: {(alt.confidence * 100).toFixed(0)}%
                  </div>

                  <div className="flex items-center space-x-2">
                    {alt.status === 'OPEN' && (
                      <button
                        onClick={() => handleUpdateStatus(alt.id, 'ACKNOWLEDGED')}
                        className="px-2.5 py-1 rounded bg-[#1e293b] hover:bg-[#283548] text-slate-200 border border-slate-700 text-[11px] transition-colors"
                      >
                        ACKNOWLEDGE
                      </button>
                    )}
                    {alt.status !== 'RESOLVED' && (
                      <button
                        onClick={() => handleUpdateStatus(alt.id, 'RESOLVED')}
                        className="px-2.5 py-1 rounded bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-300 border border-emerald-800/50 text-[11px] transition-colors flex items-center space-x-1"
                      >
                        <Check className="w-3 h-3" />
                        <span>RESOLVE</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
