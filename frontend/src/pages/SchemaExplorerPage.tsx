import React from "react";
import PageHeader from "@/components/layout/PageHeader";
import SchemaExplorer from "../components/schema/SchemaExplorer";

export default function SchemaExplorerPage() {
  return (
    <div>
      <PageHeader
        title="Schema Explorer"
        subtitle="Enterprise schema tree with AI table summaries and metadata-aware column view"
      />
      <SchemaExplorer />
    </div>
  );
}
