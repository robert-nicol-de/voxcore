import React from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/ui/Layout";
import Section from "../components/ui/Section";
import PageHeader from "@/components/layout/PageHeader";
import SemanticModelCreator from "../components/datasources/SemanticModelCreator";

export default function SemanticModelsPage() {
  const navigate = useNavigate();

  return (
    <Section>
      <PageHeader
        title="Semantic Models"
        subtitle="Define business entities and metrics for more accurate AI SQL generation"
      />
      <SemanticModelCreator onSaved={() => navigate("/app")} />
    </Section>
  );
}
