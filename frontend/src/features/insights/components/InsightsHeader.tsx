export const InsightsHeader = ({ personalized }: { personalized?: boolean }) => (
  <div className="mb-4">
    <h1 className="text-3xl font-bold">Insights</h1>
    <p className="text-gray-600">AI-generated analysis of your data</p>
    <div className="flex gap-4 mt-2">
      {personalized && (
        <span className="text-blue-600 font-semibold">🧠 Personalized for you</span>
      )}
      <span className="text-green-600 font-semibold">⚡ Real-time analysis</span>
      <span className="text-blue-700 font-semibold">🔗 Slack Connected</span>
      <span className="text-indigo-700 font-semibold">📩 Email Reports Enabled</span>
    </div>
  </div>
);
