import Layout from "../components/ui/Layout";
import Section from "../components/ui/Section";

export default function AIModel() {
  return (
    <Layout>
      <Section className="py-16 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-4">AI Model</h2>
        <p className="text-gray-300 mb-4">
          VoxCore leverages advanced AI models to interpret, optimize, and secure your database queries. Our AI is continuously updated to ensure safe, efficient, and compliant data access for your organization.
        </p>
        <ul className="list-disc list-inside text-gray-400 space-y-2">
          <li>Natural language to SQL translation</li>
          <li>Query risk analysis</li>
          <li>Automated compliance checks</li>
          <li>Continuous learning from your data</li>
        </ul>
      </Section>
    </Layout>
  );
}
