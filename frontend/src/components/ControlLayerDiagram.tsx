export function ControlLayerDiagram() {
  return (
    <div className="bg-gradient-to-r from-blue-600/5 to-purple-600/5 border border-white/10 rounded-2xl p-8">
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 md:gap-3">
        {/* AI Agent */}
        <div className="flex flex-col items-center">
          <div className="w-24 h-24 rounded-2xl bg-blue-500/20 border border-blue-500/50 flex items-center justify-center mb-3">
            <div className="text-4xl">🤖</div>
          </div>
          <div className="text-sm font-semibold">AI Agent</div>
          <div className="text-xs text-gray-500">GPT, Claude, etc.</div>
        </div>

        {/* Arrow */}
        <div className="hidden md:flex flex-col items-center">
          <div className="text-2xl text-blue-400 mb-3">↓</div>
          <div className="text-xs text-gray-500 text-center">Natural Language</div>
        </div>

        {/* Generated SQL */}
        <div className="flex flex-col items-center">
          <div className="w-24 h-24 rounded-2xl bg-purple-500/20 border border-purple-500/50 flex items-center justify-center mb-3">
            <div className="text-3xl">📝</div>
          </div>
          <div className="text-sm font-semibold">Generated SQL</div>
          <div className="text-xs text-gray-500">Raw Query</div>
        </div>

        {/* Arrow */}
        <div className="hidden md:flex flex-col items-center">
          <div className="text-2xl text-blue-400 mb-3">↓</div>
          <div className="text-xs text-gray-500 text-center">Query String</div>
        </div>

        {/* VoxCore - HIGHLIGHTED */}
        <div className="flex flex-col items-center relative">
          <div className="w-28 h-28 rounded-2xl bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center mb-3 shadow-lg shadow-blue-500/30">
            <div className="text-4xl">🛡️</div>
          </div>
          <div className="text-sm font-bold text-blue-400">VoxCore</div>
          <div className="text-xs text-gray-400">Inspection Layer</div>
          <div className="absolute -top-8 left-1/2 -translate-x-1/2 px-3 py-1 bg-red-500 text-white text-xs font-semibold rounded-full whitespace-nowrap">
            ⚠️ CONTROL LAYER
          </div>
        </div>

        {/* Arrow */}
        <div className="hidden md:flex flex-col items-center">
          <div className="text-2xl text-blue-400 mb-3">↓</div>
          <div className="text-xs text-gray-500 text-center">Risk Analysis</div>
        </div>

        {/* Database */}
        <div className="flex flex-col items-center">
          <div className="w-24 h-24 rounded-2xl bg-green-500/20 border border-green-500/50 flex items-center justify-center mb-3">
            <div className="text-4xl">🗄️</div>
          </div>
          <div className="text-sm font-semibold">Database</div>
          <div className="text-xs text-gray-500">Safe Execution</div>
        </div>
      </div>

      {/* Decision Points */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 pt-8 border-t border-white/10">
        <div className="text-center">
          <div className="inline-block px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-full text-xs font-semibold text-green-400 mb-2">
            ✓ Approved
          </div>
          <div className="text-xs text-gray-400">Query passes all policies</div>
        </div>
        <div className="text-center">
          <div className="inline-block px-3 py-1 bg-yellow-500/20 border border-yellow-500/30 rounded-full text-xs font-semibold text-yellow-400 mb-2">
            ⏳ Review
          </div>
          <div className="text-xs text-gray-400">Requires approval</div>
        </div>
        <div className="text-center">
          <div className="inline-block px-3 py-1 bg-red-500/20 border border-red-500/30 rounded-full text-xs font-semibold text-red-400 mb-2">
            🚫 Blocked
          </div>
          <div className="text-xs text-gray-400">Dangerous operation</div>
        </div>
      </div>
    </div>
  );
}
