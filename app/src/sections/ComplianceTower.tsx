import { useState } from 'react';
import {
  Scale, CheckCircle, XCircle, AlertTriangle, Clock,
  FileText, RefreshCw, Shield, Globe
} from 'lucide-react';
import type { ComplianceCheck } from '@/types/agents';
import { AgentChatBox } from '@/components/ui/AgentChatBox';

const MOCK_CHECKS: ComplianceCheck[] = [
  {
    check_id: '1', regulation_name: 'EU CBAM', regulation_category: 'environmental',
    jurisdiction: 'EU', status: 'compliant', checked_by: 'compliance',
    findings: ['All requirements met'], required_actions: [],
    risk_level: 'low', next_review_date: '2026-06-01',
    reasoning_trace: 'Steel shipment verified against CBAM requirements',
    documents_verified: ['CBAM_Declaration', 'Emissions_Report'],
    confidence: { score: 0.95 },
  },
  {
    check_id: '2', regulation_name: 'EU Deforestation Regulation (EUDR)', regulation_category: 'environmental',
    jurisdiction: 'EU', status: 'pending_review', checked_by: 'compliance',
    findings: ['Partial compliance', 'Missing geolocation data'], required_actions: ['Submit supplier geolocation coordinates'],
    risk_level: 'medium', next_review_date: '2026-04-15',
    reasoning_trace: 'Coffee shipment requires additional due diligence documentation',
    documents_verified: ['Certificate_of_Origin'],
    confidence: { score: 0.75 },
  },
  {
    check_id: '3', regulation_name: 'IMO 2023 CII', regulation_category: 'environmental',
    jurisdiction: 'Global', status: 'compliant', checked_by: 'compliance',
    findings: ['CII rating: B', 'SEEMP updated'], required_actions: [],
    risk_level: 'low', next_review_date: '2026-12-31',
    reasoning_trace: 'Vessel meets CII requirements for current rating period',
    documents_verified: ['CII_Certificate', 'SEEMP'],
    confidence: { score: 0.92 },
  },
  {
    check_id: '4', regulation_name: 'US OFAC Sanctions', regulation_category: 'trade',
    jurisdiction: 'US', status: 'compliant', checked_by: 'compliance',
    findings: ['All parties screened', 'No matches found'], required_actions: [],
    risk_level: 'low', next_review_date: '2026-04-01',
    reasoning_trace: 'SDN list screening complete for all shipment parties',
    documents_verified: ['Sanctions_Screening_Report'],
    confidence: { score: 0.98 },
  },
  {
    check_id: '5', regulation_name: 'SOLAS VGM', regulation_category: 'safety',
    jurisdiction: 'Global', status: 'compliant', checked_by: 'compliance',
    findings: ['VGM verified', 'Method 1 used'], required_actions: [],
    risk_level: 'low', next_review_date: '2026-05-01',
    reasoning_trace: 'Container weight verified using certified weighing equipment',
    documents_verified: ['VGM_Certificate'],
    confidence: { score: 0.96 },
  },
  {
    check_id: '6', regulation_name: 'AfCFTA Rules of Origin', regulation_category: 'trade',
    jurisdiction: 'Africa', status: 'pending_review', checked_by: 'compliance',
    findings: ['Certificate of origin incomplete'], required_actions: ['Complete AfCFTA CoO', 'Verify local content percentage'],
    risk_level: 'medium', next_review_date: '2026-04-20',
    reasoning_trace: 'African continental free trade area certification requires update',
    documents_verified: ['Draft_CoO'],
    confidence: { score: 0.68 },
  },
  {
    check_id: '7', regulation_name: 'ISPS Code', regulation_category: 'security',
    jurisdiction: 'Global', status: 'compliant', checked_by: 'security_audit',
    findings: ['SSA current', 'SSP approved', 'SSO designated'], required_actions: [],
    risk_level: 'low', next_review_date: '2026-07-01',
    reasoning_trace: 'International Ship and Port Facility Security code compliance verified',
    documents_verified: ['SSA_Report', 'SSP_Approval', 'SSO_Certificate'],
    confidence: { score: 0.94 },
  },
];

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    compliant: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    non_compliant: 'bg-red-500/10 text-red-400 border-red-500/20',
    pending_review: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    exempt: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
  };
  const icons = { compliant: CheckCircle, non_compliant: XCircle, pending_review: Clock, exempt: Shield };
  const Icon = icons[status as keyof typeof icons] || AlertTriangle;
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full border ${styles[status] || styles.pending_review}`}>
      <Icon className="w-3 h-3" />
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    low: 'text-emerald-400', medium: 'text-amber-400', high: 'text-orange-400', critical: 'text-red-400',
  };
  return <span className={`text-[10px] font-medium ${colors[level] || colors.medium}`}>{level.toUpperCase()}</span>;
}

export function ComplianceTower() {
  const [checks] = useState<ComplianceCheck[]>(MOCK_CHECKS);
  const [filter, setFilter] = useState('all');

  const filtered = filter === 'all' ? checks : checks.filter(c => c.status === filter);
  const stats = {
    total: checks.length,
    compliant: checks.filter(c => c.status === 'compliant').length,
    pending: checks.filter(c => c.status === 'pending_review').length,
    nonCompliant: checks.filter(c => c.status === 'non_compliant').length,
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Compliance Tower</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Regulatory compliance monitoring and audit</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[hsl(195,70%,55%/0.1)] flex items-center justify-center">
            <Scale className="w-4 h-4 text-[hsl(195,70%,55%)]" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.total}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Total Checks</div>
          </div>
        </div>
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.compliant}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Compliant</div>
          </div>
        </div>
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.pending}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Pending Review</div>
          </div>
        </div>
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center">
            <XCircle className="w-4 h-4 text-red-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.nonCompliant}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Non-Compliant</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {['all', 'compliant', 'pending_review', 'non_compliant'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === f ? 'bg-[hsl(195,70%,55%)] text-[hsl(220,20%,6%)]' :
                'bg-[hsl(220,14%,12%)] text-[hsl(215,20%,55%)] hover:text-white border border-[hsl(220,14%,20%)]'
            }`}
          >
            {f === 'all' ? 'All' : f.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-280px)] min-h-[500px]">
        {/* Compliance Table */}
        <div className="lg:col-span-2 overflow-hidden card-elevated rounded-lg flex flex-col">
          <div className="flex-1 overflow-auto scrollbar-thin">
            <table className="w-full">
              <thead className="sticky top-0 bg-[hsl(220,14%,12%)] z-10">
                <tr className="border-b border-[hsl(220,14%,18%)]">
                  <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Regulation</th>
                  <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Category</th>
                  <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Status</th>
                  <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Risk</th>
                  <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Confidence</th>
                  <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[hsl(220,14%,15%)]">
                {filtered.map((check) => (
                  <tr key={check.check_id} className="hover:bg-[hsl(220,14%,10%)] transition-colors">
                    <td className="px-4 py-3">
                      <div className="text-xs text-white font-medium">{check.regulation_name}</div>
                      <div className="text-[10px] text-[hsl(215,20%,50%)] flex items-center gap-1 mt-0.5">
                        <Globe className="w-2.5 h-2.5" /> {check.jurisdiction}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-[10px] px-2 py-0.5 bg-[hsl(220,14%,15%)] rounded text-[hsl(215,20%,65%)] capitalize">
                        {check.regulation_category}
                      </span>
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={check.status} /></td>
                    <td className="px-4 py-3"><RiskBadge level={check.risk_level} /></td>
                    <td className="px-4 py-3">
                      <div className="text-xs font-mono text-white">{((check.confidence?.score || 0) * 100).toFixed(0)}%</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1.5">
                        <button className="p-1 rounded bg-[hsl(220,14%,15%)] hover:bg-[hsl(220,14%,20%)] text-[hsl(215,20%,55%)] hover:text-white transition-colors">
                          <FileText className="w-3 h-3" />
                        </button>
                        <button className="p-1 rounded bg-[hsl(220,14%,15%)] hover:bg-[hsl(220,14%,20%)] text-[hsl(215,20%,55%)] hover:text-white transition-colors">
                          <RefreshCw className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Agent Chat */}
        <div className="h-full">
          <AgentChatBox agentId="compliance" agentName="Compliance Tower" />
        </div>
      </div>
    </div>
  );
}
