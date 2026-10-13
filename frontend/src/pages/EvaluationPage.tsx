import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function EvaluationPage() {
  const [evalData, setEvalData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await api.getEvaluationResults();
        if (res.success) setEvalData(res.data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-xs font-mono text-slate-400">Loading model evaluation metrics...</div>;
  }

  const renderMetricCard = (title: string, metrics: any) => (
    <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-gray-800 pb-2">
        <h3 className="text-sm font-bold text-white tracking-wide">{title}</h3>
        <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-900/40 text-blue-300 rounded">
          N={evalData?.dataset_samples ?? 450} SAMPLES
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="p-3 bg-[#162032] border border-gray-800/80 rounded-lg">
          <span className="text-[10px] text-slate-400 font-mono">Precision</span>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            {(metrics.precision * 100).toFixed(1)}%
          </div>
        </div>

        <div className="p-3 bg-[#162032] border border-gray-800/80 rounded-lg">
          <span className="text-[10px] text-slate-400 font-mono">Recall</span>
          <div className="text-xl font-bold font-mono text-blue-400 mt-1">
            {(metrics.recall * 100).toFixed(1)}%
          </div>
        </div>

        <div className="p-3 bg-[#162032] border border-gray-800/80 rounded-lg">
          <span className="text-[10px] text-slate-400 font-mono">F1-Score</span>
          <div className="text-xl font-bold font-mono text-purple-400 mt-1">
            {(metrics.f1_score * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs font-mono pt-2 border-t border-gray-800/80">
        <div className="flex justify-between text-slate-300">
          <span>False Positive Rate (FPR):</span>
          <span className="text-amber-400 font-bold">{(metrics.false_positive_rate * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between text-slate-300">
          <span>False Negative Rate (FNR):</span>
          <span className="text-rose-400 font-bold">{(metrics.false_negative_rate * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-xl font-bold text-white tracking-wide">AI MODEL EVALUATION & ERROR METRICS</h1>
        <p className="text-xs text-slate-400">
          Quantitative false-positive and false-negative evaluation across model inference tasks (SIH PS 26245 Mandate)
        </p>
      </div>

      <div className="p-4 bg-[#162032] border border-blue-900/40 rounded-xl flex items-center justify-between text-xs font-mono">
        <div>Model Version: <span className="text-white font-bold">{evalData?.model_version}</span></div>
        <div>Dataset: <span className="text-blue-400 font-bold">Simulated Benchmark Ground Truth</span></div>
        <div>Samples: <span className="text-emerald-400 font-bold">{evalData?.dataset_samples} items</span></div>
      </div>

      <div className="space-y-6">
        {evalData?.person_detection && renderMetricCard('1. Anonymous Person Detection & Occupancy Counting', evalData.person_detection)}
        {evalData?.equipment_detection && renderMetricCard('2. Sanctioned Equipment Detection (YOLOv8)', evalData.equipment_detection)}
        {evalData?.discrepancy_classification && renderMetricCard('3. Attendance Discrepancy Multi-Window Classification', evalData.discrepancy_classification)}
      </div>
    </div>
  );
}
