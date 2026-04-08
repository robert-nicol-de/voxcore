export default function Topbar() {
  return (
    <div className="h-14 bg-white border-b flex items-center justify-between px-6">
      <div className="text-sm text-gray-500">
        Connected • Database: Demo
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm">Admin</span>
        <div className="w-8 h-8 bg-gray-300 rounded-full" />
      </div>
    </div>
  );
}
