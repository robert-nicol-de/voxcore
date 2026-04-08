import { Shield, AlertCircle, CheckCircle } from 'lucide-react';

interface Policy {
  title: string;
  description?: string;
  severity?: 'high' | 'medium' | 'low';
}

interface GovernancePoliciesViewProps {
  currentDataset?: string;
}

const policiesByDataset: {
  [key: string]: Policy[];
} = {
  users: [
    {
      title: 'Block raw export of email addresses',
      severity: 'high',
    },
    {
      title: 'Mask personal identifiers for analyst role',
      severity: 'high',
    },
    {
      title: 'Require review for full user table scans',
      severity: 'medium',
    },
  ],
  sales: [
    {
      title: 'Encrypt customer revenue data at rest',
      severity: 'high',
    },
    {
      title: 'Limit region-level aggregations to managers+',
      severity: 'medium',
    },
    {
      title: 'Audit all product margin queries',
      severity: 'high',
    },
  ],
  products: [
    {
      title: 'Redact supplier cost from analyst view',
      severity: 'high',
    },
    {
      title: 'Require COO sign-off for product discontinuation analysis',
      severity: 'medium',
    },
  ],
};

export function GovernancePoliciesView({ currentDataset = 'users' }: GovernancePoliciesViewProps) {
  const policies = policiesByDataset[currentDataset] || policiesByDataset.users;

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/10 border-red-500/30 text-red-200';
      case 'medium':
        return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-200';
      case 'low':
        return 'bg-green-500/10 border-green-500/30 text-green-200';
      default:
        return 'bg-slate-500/10 border-slate-500/30 text-slate-200';
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-4">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/4 border border-white/8">
            <Shield className="w-4 h-4 text-sky-300 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">Active Governance Policies</p>
              <p className="text-xs text-slate-300 mt-1">
                {policies.length} policies protect {currentDataset} dataset
              </p>
            </div>
          </div>

          <div className="space-y-3 px-4 py-2">
            {policies.map((policy, idx) => (
              <div
                key={idx}
                className={`rounded-lg border p-4 ${getSeverityColor(policy.severity)}`}
              >
                <div className="flex items-start gap-3">
                  {policy.severity === 'high' && (
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  )}
                  {policy.severity === 'medium' && (
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  )}
                  {policy.severity === 'low' && (
                    <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{policy.title}</p>
                    {policy.description && (
                      <p className="text-xs mt-1 opacity-75">{policy.description}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
