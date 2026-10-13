import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { api } from '../services/api';

export default function CentreDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [centre, setCentre] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [cameras, setCameras] = useState<any[]>([]);
  const [reconciliation, setReconciliation] = useState<any>(null);
  const [infraCompliance, setInfraCompliance] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'attendance' | 'inventory' | 'cameras' | 'alerts'>('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    async function loadData() {
      try {
        setLoading(true);
        const [cRes, sRes, camRes, recRes, infRes, altRes] = await Promise.all([
          api.getCentre(id!),
          api.getCentreSummary(id!),
          api.getCameras(id!),
          api.getAttendanceReconciliation(id!),
          api.getInventoryCompliance(id!),
          api.getAlerts({ centre_id: id! }),
        ]);

        if (cRes.success) setCentre(cRes.data);
        if (sRes.success) setSummary(sRes.data);
        if (camRes.success) setCameras(camRes.data);
        if (recRes.success) setReconciliation(recRes.data);
        if (infRes.success) setInfraCompliance(infRes.data);
        if (altRes.success) setAlerts(altRes.data);
      } catch (err) {
        console.error('Error loading centre detail:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-xs font-mono text-slate-400">
        Loading Centre Monitoring Telemetry...
      </div>
    );
  }

  if (!centre) {
    return (
      <div className="p-6 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 font-mono text-xs">
        Training centre not found.
      </div>
    );
  }

  const riskBadgeColor =
    summary?.risk_level === 'HIGH' || summary?.risk_level === 'CRITICAL'
      ? 'text-rose-400 bg-rose-950/40 border-rose-800/60'
      : summary?.risk_level === 'MEDIUM'
      ? 'text-amber-400 bg-amber-950/40 border-amber-800/60'
      : 'text-emerald-400 bg-emerald-950/40 border-emerald-800/60';

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div className="space-y-1">
          <Link to="/centres" className="text-xs text-blue-400 hover:text-blue-300 font-mono flex items-center space-x-1">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>BACK TO CENTRES DIRECTORY</span>
          </Link>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-wide">{centre.name}</h1>
            <span className="text-xs font-mono px-2 py-0.5 bg-blue-900/60 text-blue-300 border border-blue-700/50 rounded">
              {centre.centre_code}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            {centre.district}, {centre.state} • Capacity: {centre.capacity} trainees
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <div className="text-[10px] uppercase font-mono text-slate-400">Overall Compliance</div>
            <div className="text-lg font-bold font-mono text-white">
              {summary?.overall_compliance_score != null ? `${summary.overall_compliance_score}%` : 'N/A'}
            </div>
          </div>
          <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${riskBadgeColor}`}>
            RISK: {summary?.risk_level ?? 'LOW'}
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-gray-800 text-xs font-mono space-x-4">
        {[
          { key: 'overview', label: 'OVERVIEW & SUMMARY' },
          { key: 'attendance', label: 'ATTENDANCE RECONCILIATION' },
          { key: 'inventory', label: 'INFRASTRUCTURE COMPLIANCE' },
          { key: 'cameras', label: `CAMERAS (${cameras.length})` },
          { key: 'alerts', label: `ALERTS (${alerts.length})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`pb-2.5 px-1 font-semibold transition-colors border-b-2 ${
              activeTab === tab.key
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Overview */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
            <div className="text-xs font-mono text-slate-400 uppercase">Estimated Physical Presence</div>
            <div className="text-3xl font-bold font-mono text-white">
              {summary?.latest_estimated_presence ?? reconciliation?.estimated_physical_presence ?? 'N/A'}
            </div>
            <div className="text-xs text-slate-400">
              Submitted Attendance: <span className="text-slate-200 font-mono">{summary?.latest_attendance_submitted ?? 'N/A'}</span>
            </div>
            <div className="text-[11px] text-slate-500">
              Anonymous presence estimation via computer vision head/body tracking.
            </div>
          </div>

          <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
            <div className="text-xs font-mono text-slate-400 uppercase">Attendance Discrepancy</div>
            <div className="text-3xl font-bold font-mono text-amber-400">
              {reconciliation?.attendance_discrepancy ?? 0}
            </div>
            <div className="text-xs text-slate-400">
              Discrepancy: <span className="text-amber-300 font-mono">{reconciliation?.discrepancy_percentage ?? 0}%</span>
            </div>
            <div className="text-[11px] text-slate-500">
              Status: <span className="font-mono text-slate-300">{reconciliation?.status ?? 'NORMAL'}</span>
            </div>
          </div>

          <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-3">
            <div className="text-xs font-mono text-slate-400 uppercase">Sanctioned Infrastructure</div>
            <div className="text-3xl font-bold font-mono text-emerald-400">
              {infraCompliance?.overall_inventory_compliance ?? 100}%
            </div>
            <div className="text-xs text-slate-400">
              Missing Items: <span className="text-rose-400 font-mono">{infraCompliance?.total_shortages ?? 0}</span>
            </div>
            <div className="text-[11px] text-slate-500">
              Sanctioned Quota verification across {infraCompliance?.items?.length ?? 0} items.
            </div>
          </div>
        </div>
      )}

      {/* Tab: Attendance Reconciliation */}
      {activeTab === 'attendance' && (
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="border-b border-gray-800 pb-3">
            <h3 className="text-sm font-semibold text-white tracking-wide">ATTENDANCE RECONCILIATION AUDIT</h3>
            <p className="text-xs text-slate-400">
              Centre-reported register attendance compared to anonymous physical presence over observation window
            </p>
          </div>

          {reconciliation ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-[#162032] border border-gray-800 rounded-lg">
                <span className="text-[11px] text-slate-400 font-mono">Submitted Attendance</span>
                <div className="text-2xl font-bold font-mono text-white mt-1">
                  {reconciliation.submitted_present}
                </div>
                <span className="text-[10px] text-slate-500">Registered: {reconciliation.registered_count}</span>
              </div>

              <div className="p-4 bg-[#162032] border border-gray-800 rounded-lg">
                <span className="text-[11px] text-slate-400 font-mono">Estimated Presence</span>
                <div className="text-2xl font-bold font-mono text-blue-400 mt-1">
                  {reconciliation.estimated_physical_presence}
                </div>
                <span className="text-[10px] text-slate-500">Confidence: {(reconciliation.confidence * 100).toFixed(0)}%</span>
              </div>

              <div className="p-4 bg-[#162032] border border-gray-800 rounded-lg">
                <span className="text-[11px] text-slate-400 font-mono">Discrepancy</span>
                <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
                  {reconciliation.attendance_discrepancy} ({reconciliation.discrepancy_percentage}%)
                </div>
                <span className="text-[10px] text-slate-500">Threshold: &gt;20% High Flag</span>
              </div>

              <div className="p-4 bg-[#162032] border border-gray-800 rounded-lg">
                <span className="text-[11px] text-slate-400 font-mono">Audit Status</span>
                <div className="text-sm font-bold font-mono text-white mt-2">
                  <span className={`px-2 py-0.5 rounded ${reconciliation.status === 'HIGH_DISCREPANCY' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'}`}>
                    {reconciliation.status}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 mt-1 block">Window: {reconciliation.observation_window_minutes} mins</span>
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-500 font-mono">No attendance reconciliation records available.</div>
          )}
        </div>
      )}

      {/* Tab: Infrastructure Compliance */}
      {activeTab === 'inventory' && (
        <div className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 bg-[#162032] border-b border-gray-800">
            <h3 className="text-sm font-semibold text-white tracking-wide">SANCTIONED EQUIPMENT INVENTORY & AI DETECTION</h3>
            <p className="text-xs text-slate-400">
              Mandated equipment quotas compared with verified camera detections
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#121b2d] border-b border-gray-800 font-mono text-slate-400 uppercase text-[11px]">
                <tr>
                  <th className="py-3 px-4">Item Type</th>
                  <th className="py-3 px-4">Item Name</th>
                  <th className="py-3 px-4">Zone</th>
                  <th className="py-3 px-4">Sanctioned</th>
                  <th className="py-3 px-4">Min Required</th>
                  <th className="py-3 px-4">Detected</th>
                  <th className="py-3 px-4">Shortage</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {infraCompliance?.items?.map((it: any, idx: number) => (
                  <tr key={idx} className="hover:bg-[#151f33] font-mono">
                    <td className="py-3 px-4 font-bold text-blue-400">{it.item_type}</td>
                    <td className="py-3 px-4 font-sans text-white">{it.item_name}</td>
                    <td className="py-3 px-4 text-slate-400">{it.zone}</td>
                    <td className="py-3 px-4 text-slate-200">{it.sanctioned_quantity}</td>
                    <td className="py-3 px-4 text-slate-200">{it.minimum_required}</td>
                    <td className="py-3 px-4 font-bold text-white">{it.detected_quantity}</td>
                    <td className="py-3 px-4 font-bold text-rose-400">{it.potential_shortage}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${it.status === 'COMPLIANT' ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40' : 'bg-rose-950/40 text-rose-400 border-rose-800/40'}`}>
                        {it.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Cameras */}
      {activeTab === 'cameras' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cameras.map((cam) => (
            <div key={cam.id} className="p-5 bg-[#111827] border border-gray-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white font-mono">{cam.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                  {cam.status}
                </span>
              </div>
              <div className="text-xs text-slate-400 space-y-1 font-mono">
                <div>Zone: <span className="text-slate-200">{cam.zone}</span></div>
                <div>Source: <span className="text-slate-200">{cam.source_type}</span></div>
                <div>Resolution / FPS: <span className="text-slate-200">{cam.resolution} @ {cam.fps} FPS</span></div>
              </div>
              <div className="pt-2 border-t border-gray-800 text-[11px] text-blue-400 font-mono">
                Stream ready for computer vision processing
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab: Alerts */}
      {activeTab === 'alerts' && (
        <div className="space-y-3">
          {alerts.length === 0 ? (
            <div className="p-8 text-center text-xs font-mono text-slate-500 bg-[#111827] border border-gray-800 rounded-xl">
              No alerts logged for this centre.
            </div>
          ) : (
            alerts.map((alt) => (
              <div key={alt.id} className="p-4 bg-[#111827] border border-gray-800 rounded-xl space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-rose-400 font-bold uppercase">{alt.severity} • {alt.alert_type}</span>
                  <span className="font-mono text-slate-500 text-[11px]">{new Date(alt.created_at).toLocaleString()}</span>
                </div>
                <div className="font-bold text-white text-sm">{alt.title}</div>
                <p className="text-slate-300 leading-relaxed">{alt.description}</p>
                <div className="text-[11px] font-mono text-slate-400">
                  Status: <span className="text-emerald-400">{alt.status}</span> • Confidence: {(alt.confidence * 100).toFixed(0)}%
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
