export default function AIStatusBar() {
  return (
    <div className="h-14 border-b border-white/5 backdrop-blur bg-[#070B14]/80 px-6 flex items-center justify-between">
      <div className="flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
          <span className="text-gray-300">AI Active</span>
        </div>
        <div className="text-gray-500">Production • SQL Server</div>
        <div className="text-green-400">Safe</div>
        <div className="text-gray-400">Risk: Low</div>
      </div>
      <div className="text-sm text-gray-400">User</div>
    </div>
  );
}
