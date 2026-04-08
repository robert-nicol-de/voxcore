import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import PageHeader from "@/components/layout/PageHeader";
import SnowflakeConnectionForm from "../components/datasources/SnowflakeConnectionForm";
import SQLServerConnectionForm from "../components/datasources/SQLServerConnectionForm";

export default function DataSourceNewPage() {
  const { platform } = useParams();
  const navigate = useNavigate();

  if (platform !== "snowflake" && platform !== "sqlserver") {
    return (
      <div>
        <PageHeader title="Platform Not Available" subtitle="This connector is marked as coming soon." />
        <button className="secondary-btn" onClick={() => navigate("/app/datasources")}>Back to Data Sources</button>
      </div>
    );
  }

  if (platform === "snowflake") {
    return (
      <div>
        <PageHeader title="Snowflake Connection" subtitle="Configure and validate a Snowflake datasource" />
        <SnowflakeConnectionForm onSaved={() => navigate("/app/datasources")} />
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="SQL Server Connection" subtitle="Configure and validate a SQL Server datasource" />
      <SQLServerConnectionForm onSaved={() => navigate("/app/datasources")} />
    </div>
  );
}
