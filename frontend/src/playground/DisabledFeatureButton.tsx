type DisabledFeatureButtonProps = {
  label: string;
};

export function DisabledFeatureButton({ label }: DisabledFeatureButtonProps) {
  return (
    <button
      type="button"
      disabled
      title="Available in full VoxCore deployment"
      className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-500 opacity-80"
    >
      {label}
    </button>
  );
}
