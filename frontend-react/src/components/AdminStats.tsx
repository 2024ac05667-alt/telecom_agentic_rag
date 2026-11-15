import { FileCheck2, Truck, Lock, Ban, Network, CheckCircle2, Phone, MapPin } from 'lucide-react';

export interface PickupTicket {
  id: string;
  createdAt: string;
  customerName: string;
  mobileNumber: string;
  dohaLocation: string;
  deviceIssue: string;
  status: string;
}

interface AdminStatsProps {
  totalLogs: number;
  latestLatency: string;
  piiCount: number;
  blockedCount: number;
  pickups: PickupTicket[];
}

export default function AdminStats({
  totalLogs,
  latestLatency,
  piiCount,
  blockedCount,
  pickups,
}: AdminStatsProps) {
  const pipelineNodes = [
    { name: '1. Security Sentinel', desc: 'Masks QID & Doha Connect' },
    { name: '2. Supervisor Agent', desc: 'Domain & Jailbreak Guardrail' },
    { name: '3. Diagnostic Orchestrator', desc: 'Vision + ChromaDB Legal RAG' },
    { name: '4. Localization Specialist', desc: 'Bilingual Reply + Pickup Offer' },
  ];

  return (
    <div className="space-y-6">
      {/* 4 KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="flex justify-between text-xs text-slate-500 font-bold">
            <span>Diagnostic Sessions</span>
            <FileCheck2 className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-extrabold mt-2">{totalLogs}</div>
          <div className="text-[11px] text-slate-400 font-mono">Latest: {latestLatency}</div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="flex justify-between text-xs text-slate-500 font-bold">
            <span>Doha Pickup Requests</span>
            <Truck className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-600 mt-2">{pickups.length}</div>
          <div className="text-[11px] text-slate-400">Consented Contacts</div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="flex justify-between text-xs text-slate-500 font-bold">
            <span>PII Redactions</span>
            <Lock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-amber-600 mt-2">{piiCount}</div>
          <div className="text-[11px] text-slate-400">QID & Mobile Masked</div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="flex justify-between text-xs text-slate-500 font-bold">
            <span>Guardrail Blocks</span>
            <Ban className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-rose-600 mt-2">{blockedCount}</div>
          <div className="text-[11px] text-slate-400">Out-of-Scope Blocked</div>
        </div>
      </div>

      {/* Consented Doha Pickup Dispatch Queue */}
      {pickups.length > 0 && (
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-emerald-500/30 space-y-3">
          <h3 className="text-xs font-bold uppercase text-emerald-600 flex items-center gap-1.5">
            <Truck className="w-4 h-4" />
            <span>Consented Doha Service Center Pickup Requests</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            {pickups.map((item) => (
              <div key={item.id} className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/25 space-y-1">
                <div className="flex justify-between font-mono text-[11px]">
                  <span className="font-bold text-emerald-600">{item.id}</span>
                  <span className="text-slate-400">{item.createdAt}</span>
                </div>
                <div className="font-extrabold text-sm">{item.customerName}</div>
                <div className="flex items-center gap-1.5 font-mono">
                  <Phone className="w-3.5 h-3.5 text-qatar-maroon" /> {item.mobileNumber}
                </div>
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-qatar-maroon" /> {item.dohaLocation}
                </div>
                {item.deviceIssue && (
                  <p className="text-[11px] text-slate-500 pt-1 border-t border-emerald-500/15">
                    {item.deviceIssue}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4-Node LangGraph Pipeline Status */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
        <h3 className="text-xs font-bold uppercase text-slate-500 mb-3 flex items-center gap-1.5">
          <Network className="w-4 h-4 text-qatar-maroon" />
          <span>Active 4-Node LangGraph Pipeline</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          {pipelineNodes.map((node, index) => (
            <div key={index} className="p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
              <div className="flex justify-between font-bold">
                <span>{node.name}</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              </div>
              <div className="text-[11px] text-slate-500 mt-1">{node.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}