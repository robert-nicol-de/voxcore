export type QueryFlowStatus = 'idle' | 'active' | 'safe' | 'warning' | 'blocked';

export type QueryFlowStage = {
  label: string;
  status: QueryFlowStatus;
  detail?: string;
};

type LiveQueryFlowProps = {
  title?: string;
  subtitle?: string;
  stages: QueryFlowStage[];
  compact?: boolean;
};

function stageSymbol(status: QueryFlowStatus) {
  if (status === 'safe') return '✔';
  if (status === 'warning') return '⚠';
  if (status === 'blocked') return '✖';
  if (status === 'active') return '●';
  return '○';
}

function defaultDetail(status: QueryFlowStatus) {
  if (status === 'active') return 'In progress';
  if (status === 'safe') return 'Passed';
  if (status === 'warning') return 'Warning';
  if (status === 'blocked') return 'Blocked';
  return 'Waiting';
}

export default function LiveQueryFlow({
  title = 'AI Query Flow',
  subtitle,
  stages,
  compact = false,
}: LiveQueryFlowProps) {
  return (
    <section className={`card query-flow-card${compact ? ' query-flow-card--compact' : ''}`}>
      <div className="query-flow-header">
        <h3>{title}</h3>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>

      <div className="query-flow-steps">
        {stages.map((stage, index) => (
          <div key={stage.label} className="query-flow-step-wrap">
            <div className={`query-flow-step query-flow-step--${stage.status}`}>
              <span className="query-flow-step-icon">{stageSymbol(stage.status)}</span>
              <div className="query-flow-step-copy">
                <span className="query-flow-step-label">{stage.label}</span>
                <span className="query-flow-step-detail">{stage.detail || defaultDetail(stage.status)}</span>
              </div>
            </div>
            {index < stages.length - 1 ? <div className="query-flow-arrow">↓</div> : null}
          </div>
        ))}
      </div>
    </section>
  );
}