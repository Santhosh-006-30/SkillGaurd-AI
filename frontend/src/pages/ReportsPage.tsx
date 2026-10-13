import { useState, useEffect } from 'react';
import {
  FileText, Download, Printer, Building2, RefreshCw, ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';

export default function ReportsPage() {
  const [centres, setCentres] = useState<any[]>([]);
  const [selectedCentreId, setSelectedCentreId] = useState<number | null>(null);
  const [centreSummary, setCentreSummary] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [reportsList, setReportsList] = useState<any[]>([]);

  useEffect(() => {
    loadCentres();
  }, []);

  useEffect(() => {
    if (selectedCentreId) {
      loadCentreDetails(selectedCentreId);
    }
  }, [selectedCentreId]);

  const loadCentres = async () => {
    try {
      setLoading(true);
      const res = await api.getCentres();
      if (res.success && res.data.length > 0) {
        setCentres(res.data);
        setSelectedCentreId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load centres for reports', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCentreDetails = async (id: number) => {
    try {
      const summaryRes = await api.getCentreSummary(id);
      if (summaryRes.success) {
        setCentreSummary(summaryRes.data);
      }
      const repRes = await api.getReports(id);
      if (repRes.success && repRes.data.reports) {
        setReportsList(repRes.data.reports);
      }
    } catch (err) {
      console.error('Failed to fetch summary for centre report', err);
    }
  };

  const handleGenerateReport = () => {
    setGenerating(true);
    setTimeout(() => {
      const newReport = {
        id: `REP-${selectedCentreId}-${Date.now().toString().slice(-4)}`,
        title: `Formal Inspection Audit Dossier - ${centreSummary?.centre?.centre_code || 'CENTRE'}`,
        generated_at: new Date().toISOString(),
        format: 'PDF',
        status: 'READY'
      };
      setReportsList(prev => [newReport, ...prev]);
      setGenerating(false);
    }, 800);
  };

  const handleDownloadJSON = () => {
    if (!centreSummary) return;
    const blob = new Blob([JSON.stringify(centreSummary, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SkillGuard_Audit_${centreSummary.centre.centre_code}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mr-3 text-blue-500" />
        <span>Loading Inspection & Audit Reports...</span>
      </div>
    );
  }

  const centre = centreSummary?.centre;
  const compliance = centreSummary?.compliance;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold tracking-tight text-white">INSPECTION & AUDIT REPORTS</h1>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-950/80 text-blue-400 border border-blue-800/60 rounded">
              MSDE COMPLIANCE ARCHIVE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Generate and export tamper-evident training centre compliance dossiers [SIMULATED DEMO DATA]
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handlePrint}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-slate-200 text-xs font-medium border border-gray-700 transition"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print View</span>
          </button>
          <button
            onClick={handleDownloadJSON}
            disabled={!centreSummary}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 text-xs font-medium border border-blue-500/40 transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Audit JSON</span>
          </button>
        </div>
      </div>

      {/* Centre Selection & Quick Generator */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-1 items-center space-x-3">
          <Building2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
          <div className="w-full max-w-md">
            <label className="block text-[11px] font-mono uppercase text-slate-400 mb-1">
              Select Target Training Centre
            </label>
            <select
              value={selectedCentreId || ''}
              onChange={(e) => setSelectedCentreId(Number(e.target.value))}
              className="w-full bg-[#1e293b] border border-gray-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            >
              {centres.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.centre_code} — {c.name} ({c.district})
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={generating}
          className="flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition disabled:opacity-50"
        >
          {generating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Generating Dossier...</span>
            </>
          ) : (
            <>
              <FileText className="w-4 h-4" />
              <span>Generate Audit Dossier</span>
            </>
          )}
        </button>
      </div>

      {/* Live Report Preview Canvas */}
      {centre && compliance && (
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-800 pb-4 gap-2">
            <div>
              <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">
                OFFICIAL AUDIT SUMMARY MEMORANDUM
              </span>
              <h2 className="text-lg font-bold text-white mt-1">
                {centre.name} [{centre.centre_code}]
              </h2>
              <p className="text-xs text-slate-400">{centre.address}, {centre.district}, {centre.state}</p>
            </div>
            <div className="text-right">
              <span className="inline-block px-3 py-1 rounded-md text-xs font-mono font-bold uppercase bg-blue-950 text-blue-300 border border-blue-800">
                STATUS: {centre.status}
              </span>
              <div className="text-[10px] font-mono text-slate-500 mt-1">
                Generated: {new Date().toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Key Metric Highlights in Dossier */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-[#162136] border border-gray-800">
              <div className="text-[10px] uppercase font-mono text-slate-400">Overall Compliance</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                {compliance.overall_score.toFixed(1)}%
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Formula Weight: 40/40/10/10</div>
            </div>

            <div className="p-4 rounded-lg bg-[#162136] border border-gray-800">
              <div className="text-[10px] uppercase font-mono text-slate-400">Risk Assessment</div>
              <div className={`text-lg font-bold font-mono mt-1 ${
                compliance.risk_category === 'HIGH' ? 'text-rose-400' :
                compliance.risk_category === 'MEDIUM' ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {compliance.risk_category} RISK
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Discrepancy Severity</div>
            </div>

            <div className="p-4 rounded-lg bg-[#162136] border border-gray-800">
              <div className="text-[10px] uppercase font-mono text-slate-400">Sanctioned Seats</div>
              <div className="text-2xl font-bold font-mono text-white mt-1">
                {centre.sanctioned_capacity}
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Approved Batch Capacity</div>
            </div>

            <div className="p-4 rounded-lg bg-[#162136] border border-gray-800">
              <div className="text-[10px] uppercase font-mono text-slate-400">Active Sensors</div>
              <div className="text-2xl font-bold font-mono text-blue-400 mt-1">
                {centreSummary.cameras?.length || 0}
              </div>
              <div className="text-[10px] text-slate-400 mt-1">CCTV Streams Processed</div>
            </div>
          </div>

          {/* Privacy Protection Notice */}
          <div className="p-4 rounded-lg bg-emerald-950/30 border border-emerald-800/40 flex items-start space-x-3 text-xs text-emerald-300">
            <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-emerald-200">Zero Biometric Storage Guarantee</div>
              <p className="mt-0.5 text-slate-300">
                This audit is generated using head and body bounding boxes with short-lived session tracking IDs. No facial recognition, biometric face embeddings, or personal identifiable imagery are retained on local disks or transmitted over network backbones.
              </p>
            </div>
          </div>

          {/* Historical Generated Reports Table */}
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-mono font-semibold uppercase text-slate-400 tracking-wider">
              Generated Reports & Audit Dossiers
            </h3>
            <div className="border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#162136] text-slate-400 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2.5 px-4">Dossier ID</th>
                    <th className="py-2.5 px-4">Title</th>
                    <th className="py-2.5 px-4">Format</th>
                    <th className="py-2.5 px-4">Generated Timestamp</th>
                    <th className="py-2.5 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 font-mono text-slate-300">
                  {reportsList.map((r, idx) => (
                    <tr key={idx} className="hover:bg-[#1a2333]/50">
                      <td className="py-2.5 px-4 text-blue-400 font-semibold">{r.id}</td>
                      <td className="py-2.5 px-4 font-sans text-slate-200">{r.title}</td>
                      <td className="py-2.5 px-4 text-slate-400">{r.format}</td>
                      <td className="py-2.5 px-4 text-slate-400">{new Date(r.generated_at).toLocaleString()}</td>
                      <td className="py-2.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px]">
                          {r.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
