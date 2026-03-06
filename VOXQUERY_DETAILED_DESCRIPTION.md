# VoxQuery - Detailed Technical Description

## Executive Summary

VoxQuery is an enterprise-grade, AI-powered SQL generation and data analysis platform that democratizes database access. It enables business users, analysts, and executives to query complex databases using natural language, eliminating the need for SQL expertise. The system leverages advanced language models (LLMs) to understand business questions and translate them into optimized SQL queries across multiple database platforms.

### Problem Statement
Traditional data access requires SQL expertise, creating bottlenecks where:
- Business users must wait for data teams to write queries
- Data teams spend time on repetitive query writing
- Ad-hoc analysis is slow and expensive
- Knowledge silos prevent self-service analytics

### Solution
VoxQuery solves this by:
- Converting natural language to SQL automatically
- Supporting multiple database platforms seamlessly
- Providing instant results with professional visualizations
- Enabling self-service analytics for all users
- Reducing time-to-insight from hours to seconds

---

## System Architecture - Deep Dive

### 1. Frontend Architecture (React/TypeScript)

#### Component Hierarchy
```
App.tsx (Root)
├── ConnectionHeader.tsx
│   ├── Database Type Selector
│   ├── Connection Status Indicator
│   └── Disconnect Button
├── Sidebar.tsx
│   ├── Database Selection
│   ├── Connection Form
│   │   ├── Host Input
│   │   ├── Username Input
│   │   ├── Password Input
│   │   ├── Database Input
│   │   └── Connect Button
│   └── Smart Questions Display
├── Chat.tsx (Main Component)
│   ├── Messages Container
│   │   ├── User Messages
│   │   ├── Assistant Messages
│   │   ├── SQL Block
│   │   │   ├── SQL Code Display
│   │   │   ├── Action Buttons
│   │   │   │   ├── Copy SQL
│   │   │   │   ├── Export CSV
│   │   │   │   ├── Export Excel
│   │   │   │   └── Email
│   │   │   └── Chart Type Selector
│   │   │       ├── Bar Chart
│   │   │       ├── Pie Chart
│   │   │       ├── Line Chart
│   │   │       └── Comparison Chart
│   │   ├── Results Block
│   │   │   ├── Results Table
│   │   │   └── Row Count
│   │   └── Loading Indicator
│   ├── Input Area
│   │   ├── Textarea
│   │   └── Send Button
│   └── Notifications Container
│       └── Toast Notifications
└── Settings.tsx (Optional)
    └── Configuration Options
```

#### State Management
```typescript
// Message State
interface Message {
  id: string;
  type: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  sql?: string;
  results?: any[];
  chart?: any;
  chartType?: string;
}

// Notification State
interface Notification {
  id: string;
  type: 'error' | 'success' | 'info' | 'warning';
  message: string;
  duration?: number;
}

// Component State
- messages: Message[]
- input: string
- loading: boolean
- isConnected: boolean
- notifications: Notification[]
- selectedChartType: string
```

#### Key Features
1. **Real-time Message Updates** - Messages update instantly as they arrive
2. **Auto-scrolling** - Chat scrolls to latest message automatically
3. **Responsive Design** - Works on desktop, tablet, and mobile
4. **Accessibility** - ARIA labels and keyboard navigation
5. **Performance** - Virtualized message list for large histories

### 2. Backend Architecture (FastAPI/Python)

#### API Layer Structure
```
FastAPI Application
├── Health Check Router
│   └── GET /health
├── Query Router (/api/v1)
│   ├── POST /query
│   ├── POST /query/validate
│   ├── POST /query/explain
│   └── POST /export/excel
├── Schema Router (/api/v1)
│   ├── GET /schema
│   ├── POST /schema/generate-questions
│   └── GET /schema/analyze
└── Auth Router (/api/v1)
    ├── POST /auth/connect
    ├── POST /auth/validate
    └── POST /auth/disconnect
```

#### Core Engine Components

##### A. SQL Generator (sql_generator.py)
```python
class SQLGenerator:
    def __init__(self, engine: Engine, dialect: str):
        - Initialize LLM connection
        - Set up schema analyzer
        - Configure dialect-specific features
    
    def generate(self, question: str) -> GeneratedSQL:
        1. Analyze schema context
        2. Build optimized prompt
 