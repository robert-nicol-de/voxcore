export type Aggregation = "sum" | "avg" | "count" | "min" | "max";

export interface Metric {
  name: string;
  description: string;
  logic: string; // NON-SQL logical expression
  aggregation: Aggregation;
  sourceFields: string[];
}

export interface Dimension {
  name: string;
  type: "categorical" | "hierarchical" | "temporal";
  sourceField: string;
  hierarchy?: string[];
}

export interface Relationship {
  from: string; // table.column
  to: string;   // table.column
  type: "one_to_one" | "one_to_many" | "many_to_one" | "many_to_many";
}

export interface TimeLogic {
  defaultField: string;
  supportedGranularity: ("day" | "week" | "month" | "quarter" | "year")[];
  relativePeriods: string[];
}

export interface SemanticModel {
  metrics: Metric[];
  dimensions: Dimension[];
  relationships: Relationship[];
  time: TimeLogic;
}
