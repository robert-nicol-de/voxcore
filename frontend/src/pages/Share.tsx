
import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import Layout from "../components/ui/Layout";
import Section from "../components/ui/Section";
import Card from "../components/ui/Card";

export default function Share() {
  const { id } = useParams();
  const navigate = useNavigate();

  const data = localStorage.getItem(`share-${id}`);
  const parsed = data ? JSON.parse(data) : null;

  if (!parsed)
    return (
      <Layout>
        <Section title="Shared Query">
          <Card>No data found</Card>
        </Section>
      </Layout>
    );

  return (
    <Layout>
      <Section title="Shared Query">
        <Card>
          <p className="text-gray-400">Query</p>
          <p>{parsed.input}</p>
        </Card>
        <Card>
          <p className="text-gray-400">Results</p>
          <table className="w-full text-sm mb-2">
            <thead>
              <tr className="text-gray-400 text-left">
                {parsed.result.columns.map((col: string) => (
                  <th key={col} className="pb-2">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {parsed.result.data.map((row: any, i: number) => (
                <tr key={i}>
                  {parsed.result.columns.map((col: string) => (
                    <td key={col}>{row[col]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        <Card>
          <p className="text-gray-400">Risk Score</p>
          <p className={`font-semibold ${
            parsed.result.risk === "HIGH"
              ? "text-red-400"
              : parsed.result.risk === "MEDIUM"
              ? "text-yellow-400"
              : "text-green-400"
          }`}>
            {parsed.result.risk}
          </p>
        </Card>
        <button
          className="mt-6 bg-sky-500 px-4 py-2 rounded"
          onClick={() => navigate("/playground")}
        >
          Try VoxCore Playground
        </button>
      </Section>
    </Layout>
  );
}
