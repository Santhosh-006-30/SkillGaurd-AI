import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, ArrowRight, Video } from 'lucide-react';
import { api } from '../services/api';

export default function CentresPage() {
  const [centres, setCentres] = useState<any[]>([]);
  const [summaries, setSummaries] = useState<Record<number, any>>({});
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCentres() {
      try {
        setLoading(true);
        const res = await api.getCentres({ search, status: statusFilter || undefined });
        if (res.success) {
          setCentres(res.data);
          // Load summaries for each centre in parallel
          const summaryPromises = res.data.map((c) => api.getCentreSummary(c.id));
          const summaryResults = await Promise.all(summaryPromises);
          const map: Record<number, any> = {};
          summaryResults.forEach((sRes) => {
            if (sRes.success && sRes.data) {
              map[sRes.data.id] = sRes.data;
            }
          });
          setSummaries(map);
        }
      } catch (err) {
        console.error('Failed to load centres', err);
      } finally {
        setLoading(false);
      }
    }
    loadCentres();
  }, [search, statusFilter]);

  return (
    <div className="space-y-6">
      {/* Header and Filter bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">TRAINING CENTRES</h1>
          <p className="text-xs text-slate-400">
            Registered vocational training institutes under MSDE monitoring
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by code, name, district..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-[#111827] border border-gray-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono w-64"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#111827] border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500 font-mono"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="UNDER_REVIEW">UNDER_REVIEW</option>
            <option value="SUSPENDED">SUSPENDED</option>
          </select>
        </div>
      </div>

      {/* Centres Table */}
      <div className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-slate-400">
            Loading centres directory...
          </div>
        ) : centres.length === 0 ? (
          <div className="p-12 text-center text-xs font-mono text-slate-500">
            No training centres matching query criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#162032] border-b border-gray-800 text-[11px] font-mono uppercase text-slate-400">
                <tr>
                  <th className="py-3 px-4">Centre Code</th>
                  <th className="py-3 px-4">Institute Name</th>
                  <th className="py-3 px-4">District / State</th>
                  <th className="py-3 px-4">Cameras</th>
                  <th className="py-3 px-4">Compliance</th>
                  <th className="py-3 px-4">Risk Level</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {centres.map((c) => {
                  const sum = summaries[c.id];
                  const riskColor =
                    sum?.risk_level === 'HIGH' || sum?.risk_level === 'CRITICAL'
                      ? 'text-rose-400 bg-rose-950/40 border-rose-800/40'
                      : sum?.risk_level === 'MEDIUM'
                      ? 'text-amber-400 bg-amber-950/40 border-amber-800/40'
                      : 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';

                  return (
                    <tr key={c.id} className="hover:bg-[#151f33] transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-blue-400">
                        {c.centre_code}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-white max-w-xs truncate">
                        {c.name}
                      </td>
                      <td className="py-3.5 px-4 text-slate-300">
                        {c.district}, {c.state}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-slate-300">
                        <div className="flex items-center space-x-1.5">
                          <Video className="w-3.5 h-3.5 text-emerald-400" />
                          <span>{sum?.active_cameras ?? 0} / {sum?.camera_count ?? 0}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-semibold text-white">
                        {sum?.overall_compliance_score != null ? `${sum.overall_compliance_score}%` : 'N/A'}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${riskColor}`}>
                          {sum?.risk_level ?? 'LOW'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          to={`/centres/${c.id}`}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/30 text-[11px] font-mono transition-colors"
                        >
                          <span>MONITOR</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
