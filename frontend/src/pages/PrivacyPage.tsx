import { Shield, EyeOff, Lock, CheckCircle2, Cpu, FileCheck, AlertCircle } from 'lucide-react';

export default function PrivacyPage() {
  const privacyPrinciples = [
    {
      title: "Zero Facial Recognition Architecture",
      description: "No face detection models, facial landmark extractors, or face embeddings are ever deployed or stored in the pipeline. Attendance audit is strictly based on head/body bounding box detection and anonymous spatial tracking.",
      icon: EyeOff,
      badge: "STRICT COMPLIANCE",
      status: "ACTIVE"
    },
    {
      title: "Ephemeral Session Tracking (No Biometric Profiling)",
      description: "Person detections use short-lived numeric track IDs assigned strictly within a single video processing session. No cross-session or persistent identity graphs are maintained.",
      icon: Lock,
      badge: "PRIVACY PRESERVING",
      status: "ACTIVE"
    },
    {
      title: "Edge Metadata Extraction & Low-Bandwidth Telemetry",
      description: "CCTV video streams are analyzed directly on edge nodes or local processing instances. Only anonymous telemetry metadata (counts, bounding boxes, timestamps, and compliance metrics) are sent upstream, reducing bandwidth by 99%.",
      icon: Cpu,
      badge: "BANDWIDTH OPTIMIZED",
      status: "ACTIVE"
    },
    {
      title: "Conservative & Objective Terminology",
      description: "The system outputs 'Estimated Physical Presence' instead of claimed verified individual identity, and 'Activity observed / Apparently active' rather than asserting machine functional certification.",
      icon: FileCheck,
      badge: "EXPLAINABLE AI",
      status: "ACTIVE"
    }
  ];

  const auditVerifications = [
    { rule: "Biometric Data Collection", compliant: true, note: "Zero biometric signatures or facial coordinates retained" },
    { rule: "GDPR / DPDP Act Alignment", compliant: true, note: "Minimization of person-identifiable records at ingestion" },
    { rule: "Tamper-Evident Processing Sessions", compliant: true, note: "Cryptographic session IDs & deterministic frame rates" },
    { rule: "Data Minimization in Transit", compliant: true, note: "Raw video retention configurable; metadata sent in JSON format" },
    { rule: "Automated Evidence Redaction", compliant: true, note: "Evidence snapshot frames can apply blurring to non-relevant zones" }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="border-b border-gray-800 pb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-emerald-600/20 border border-emerald-500/40 rounded-xl text-emerald-400">
            <EyeOff className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white">PRIVACY-PRESERVING ARCHITECTURE</h1>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 rounded">
                SIH 26245 MANDATE
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Ethical AI governance, zero facial recognition policy, and data minimization protocols
            </p>
          </div>
        </div>
      </div>

      {/* Main Banner */}
      <div className="p-6 rounded-xl bg-gradient-to-r from-emerald-950/40 via-[#111827] to-[#111827] border border-emerald-800/40">
        <div className="flex items-start space-x-4">
          <Shield className="w-8 h-8 text-emerald-400 flex-shrink-0 mt-1" />
          <div className="space-y-2">
            <h2 className="text-base font-semibold text-white">
              Strict Adherence to Ministry of Skill Development & Entrepreneurship (MSDE) Privacy Norms
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              SkillGuard AI was architected from day one to eliminate privacy liabilities inherent in conventional surveillance systems. In full accordance with national privacy guidelines and the Digital Personal Data Protection (DPDP) Act, SkillGuard AI completely eschews facial recognition technology. Presence verification relies exclusively on anonymous spatial localization and temporal motion tracking.
            </p>
          </div>
        </div>
      </div>

      {/* 4 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {privacyPrinciples.map((pillar, idx) => {
          const Icon = pillar.icon;
          return (
            <div key={idx} className="p-5 rounded-xl bg-[#111827] border border-gray-800 hover:border-gray-700 transition">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 rounded-lg bg-[#162136] text-blue-400">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                  {pillar.badge}
                </span>
              </div>
              <h3 className="text-sm font-semibold text-white mb-2">{pillar.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{pillar.description}</p>
            </div>
          );
        })}
      </div>

      {/* Architecture Pipeline Comparison */}
      <div className="p-6 rounded-xl bg-[#111827] border border-gray-800 space-y-4">
        <h3 className="text-sm font-semibold text-white">Surveillance Paradigm Comparison</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Traditional */}
          <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-900/40 space-y-2">
            <div className="flex items-center space-x-2 text-rose-400 font-semibold font-mono text-xs">
              <AlertCircle className="w-4 h-4" />
              <span>CONVENTIONAL MONITORING (PROHIBITED)</span>
            </div>
            <ul className="space-y-1.5 text-slate-400 list-disc list-inside">
              <li>Facial recognition databases matching student faces</li>
              <li>Biometric template indexing across centres</li>
              <li>Constant high-bandwidth raw video uploading</li>
              <li>High risk of biometric leaks and surveillance overreach</li>
            </ul>
          </div>

          {/* SkillGuard AI */}
          <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-900/40 space-y-2">
            <div className="flex items-center space-x-2 text-emerald-400 font-semibold font-mono text-xs">
              <CheckCircle2 className="w-4 h-4" />
              <span>SKILLGUARD AI (APPROVED)</span>
            </div>
            <ul className="space-y-1.5 text-slate-300 list-disc list-inside">
              <li>Anonymous head/body detection with zero face features</li>
              <li>Short-lived session track IDs reset per processing session</li>
              <li>Local metadata extraction; transmit only low-bandwidth telemetry</li>
              <li>Fully compliant with Indian DPDP Act & international standards</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Verification Checklist */}
      <div className="p-6 rounded-xl bg-[#111827] border border-gray-800 space-y-3">
        <h3 className="text-sm font-semibold text-white">Compliance & Governance Verification Checklist</h3>
        <div className="divide-y divide-gray-800">
          {auditVerifications.map((v, i) => (
            <div key={i} className="py-2.5 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span className="text-slate-200 font-medium">{v.rule}</span>
              </div>
              <span className="text-slate-400 font-mono text-[11px]">{v.note}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
