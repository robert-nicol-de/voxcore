# Step 4: Narrative Engine Upgrade — Executive-Grade Narratives

**Status:** ✅ **COMPLETE**  
**Commit:** `c6748043`  
**File Modified:** voxcore/engine/insight_narrative_engine.py  
**Lines Added:** 400

---

## Overview

### The Problem
Previously, the narrative engine returned flat, placeholder one-liners:
- "Revenue declined 12% in APAC during Q4."
- "North America generated the highest revenue."
- "Root cause: Customer churn for EMEA."

These felt generic, lacked context, and didn't guide users toward action.

### The Solution
Upgraded to a **three-layer narrative structure** with **executive-grade wording**:
- **Headline:** One-liner hero insight (what happened)
- **Summary:** Two-sentence expanded explanation with context (why it matters)
- **Next Step:** Specific recommended action (what to do about it)

**Result:** Narratives now sound like enterprise software, not placeholder copy.

---

## What Changed

### Before (Flat String Output)
```python
"Revenue declined 12% in APAC during Q4."
```

### After (Structured Three-Layer Narrative)
```json
{
  "headline": "Revenue declined 12.0% in APAC",
  "summary": "Revenue showed a notable decline in APAC during Q4 2024. Contributing factors should be analyzed to determine if this is temporary or part of a larger trend.",
  "next_step": "investigation recommended — drill into factors affecting APAC revenue",
  "insight_type": "trend_decline",
  "tone": "operational",
  "confidence": 1.0,
  "keywords": ["revenue", "decline", "decrease", "apac"]
}
```

---

## Architecture

### Data Structure: Narrative Class

```python
@dataclass
class Narrative:
    # Three-layer content
    headline: str         # One-liner ("Revenue declined 12%")
    summary: str          # Context (2 sentences, 150 chars)
    next_step: str        # Action (specific recommendation)
    
    # Context
    insight_type: str     # Type of insight
    tone: ToneStyle       # EXECUTIVE | OPERATIONAL | ANALYTICAL
    
    # Metadata
    confidence: float     # 0.0-1.0 confidence
    keywords: List[str]   # For searching/filtering
```

### Tone Enum

```python
class ToneStyle(str, Enum):
    EXECUTIVE = "executive"      # CEO, board, strategic
    OPERATIONAL = "operational"  # Team leads, execution
    ANALYTICAL = "analytical"    # Data analysts, technical but clear
```

---

## Narrative Templates

### 1. Trend Increase
**When:** Positive growth detected

**Example Input:**
```python
{
    "type": "trend_increase",
    "metric": "Revenue",
    "percent_change": 15,
    "entity": "EMEA",
    "period": "Q4 2024"
}
```

**Output:**
```
Headline:  "Revenue increased 15.0% in EMEA"
Summary:   "Revenue showed positive momentum in EMEA during Q4 2024, with 15.0% growth. 
            This aligns with expected seasonal patterns and operational improvements."
Next Step: "Review drivers of growth in EMEA revenue"
Tone:      EXECUTIVE
```

---

### 2. Trend Decline
**When:** Negative trend detected. Severity-aware.

**Example Input (Moderate Severity):**
```python
{
    "type": "trend_decline",
    "metric": "Revenue",
    "percent_change": -12,
    "entity": "APAC",
    "period": "Q4 2024",
    "severity": "moderate"
}
```

**Output:**
```
Headline:  "Revenue declined 12.0% in APAC"
Summary:   "Revenue showed a notable decline in APAC during Q4 2024. Contributing factors 
            should be analyzed to determine if this is temporary or part of a larger trend."
Next Step: "investigation recommended — drill into factors affecting APAC revenue"
Tone:      OPERATIONAL
```

**Severity Levels:**
- `low`: "slight decline" → "monitoring recommended"
- `moderate`: "notable decline" → "investigation recommended"
- `high`: "significant decline" → "requires immediate action"

---

### 3. Top Performer
**When:** Leader/winner identified

**Example Input:**
```python
{
    "type": "top_performer",
    "metric": "Revenue",
    "entity": "North America",
    "value": 2100000,
    "rank": 1
}
```

**Output:**
```
Headline:  "North America leads in Revenue (Rank #1)"
Summary:   "North America generated the highest revenue at $2,100,000. This segment 
            demonstrates strong market position and operational effectiveness. Performance 
            is worth replicating across other regions."
Next Step: "Analyze success factors in North America for broader application"
Tone:      EXECUTIVE
```

---

### 4. Root Cause
**When:** Contributing factor or cause identified

**Example Input:**
```python
{
    "type": "root_cause",
    "cause": "Customer churn increased post-outage",
    "entity": "EMEA",
    "impact_metric": "Revenue",
    "impact_percent": -8,
    "recommendation": "Implement SLA improvements"
}
```

**Output:**
```
Headline:  "Root cause identified: Customer churn increased post-outage"
Summary:   "Customer churn increased post-outage impacting EMEA, contributing to -8.0% 
            of the change in revenue. This factor appears to be the primary driver of the 
            observed change and should be addressed to restore normal performance."
Next Step: "Recommended action: Implement SLA improvements. Implement mitigation and 
            monitor improvement."
Tone:      OPERATIONAL
Confidence: 0.8 (Root cause analysis is often probabilistic)
```

---

### 5. Explain Data Summary
**When:** Dataset discovered/previewed

**Example Input:**
```python
{
    "type": "explain_data_summary",
    "table_name": "Sales",
    "row_count": 245000,
    "key_metrics": ["Revenue", "Orders", "Customer Count"],
    "time_range": "36 months rolling"
}
```

**Output:**
```
Headline:  "Dataset overview: Sales table"
Summary:   "This dataset contains 245,000 records covering transactional and organizational 
            data. Track Revenue, Orders, Customer Count. Data spans 36 months rolling. 
            All data has been validated and is ready for analysis."
Next Step: "Begin exploration — start with total revenue by region or product"
Tone:      ANALYTICAL
```

---

### 6. Exploration Suggestion
**When:** Recommending analysis path

**Example Input:**
```python
{
    "type": "exploration_suggestion",
    "metric": "Revenue",
    "dimension": "Product Category",
    "reason": "To identify category-level performance drivers"
}
```

**Output:**
```
Headline:  "Explore revenue by Product Category"
Summary:   "Breaking down revenue by Product Category will reveal concentration and 
            distribution patterns. This provides visibility into category-level performance 
            drivers."
Next Step: "Run analysis: Revenue grouped by Product Category"
Tone:      ANALYTICAL
```

---

### 7. Comparison Insight (Bonus)
**When:** Comparing two groups/regions/products

**Example Input:**
```python
{
    "type": "comparison_insight",
    "metric": "Margin",
    "group_a": "Product A",
    "group_b": "Product B",
    "difference_percent": 18,
    "winner": "Product A"
}
```

**Output:**
```
Headline:  "Margin gap: 18.0% between Product A and Product B"
Summary:   "Product A outperforms Product B in margin by 18.0%. This variance warrants 
            investigation to determine if it reflects pricing, efficiency, or market conditions."
Next Step: "Deep dive into operational differences between Product A and Product B"
Tone:      OPERATIONAL
```

---

## Tone: No Hype, Premium Language

### Principles

**✅ DO:**
- Use calm, measured language
- Focus on facts and implications
- Guide toward action
- Sound operational and strategic
- Respect executive time

**❌ DON'T:**
- Use exclamation marks
- Say "amazing", "incredible", "skyrocketing"
- Use developer jargon (e.g., "queries", "endpoints")
- Be alarmist about minor changes
- Assume patterns without caveats

### Example Comparisons

| ❌ Bad | ✅ Good |
|--------|---------|
| "Revenue SKYROCKETED 15%!" | "Revenue increased 15% in EMEA" |
| "Amazingly, North America is the best!" | "North America demonstrates strong market position" |
| "Customer endpoint failures triggered churn" | "Customer churn increased post-outage" |
| "This query result is super useful!" | "This dataset contains key metrics for analysis" |
| "Wow, you need to look at this!" | "Review drivers of growth in this segment" |

---

## API Usage

### Basic Usage

```python
from voxcore.engine.insight_narrative_engine import InsightNarrativeEngine

engine = InsightNarrativeEngine()

# Input insight data
insight = {
    "type": "trend_decline",
    "metric": "Revenue",
    "percent_change": -12,
    "entity": "APAC",
    "period": "Q4 2024",
    "severity": "moderate",
}

# Generate narrative
narrative = engine.generate(insight)

# Output is Narrative object
print(narrative.headline)    # "Revenue declined 12.0% in APAC"
print(narrative.summary)     # Full explanation
print(narrative.next_step)   # Recommended action
print(narrative.tone)        # ToneStyle.OPERATIONAL
print(narrative.confidence)  # 1.0
```

### In Playground Response

```python
# In Playground API
narrative = engine.generate(insight_data)

# Convert to API format
response = PlaygroundQueryResponse(
    hero_insight=narrative.headline,
    why_this_answer=narrative.summary,
    suggestions=[narrative.next_step],
    ...
)
```

### Backward Compatibility

For code expecting just a headline string:

```python
# Old code that expects string
headline = InsightNarrativeEngine.generate_headline_only(insight)
# Returns: "Revenue declined 12.0% in APAC"
```

---

## Narrative Rendering Examples

### Frontend: Insight Card

```
┌─────────────────────────────────────────┐
│ Revenue declined 12.0% in APAC           │  ← Headline
├─────────────────────────────────────────┤
│ Revenue showed a notable decline in APAC │ ← Summary (2 lines)
│ during Q4 2024. Contributing factors     │
│ should be analyzed to determine if this  │
│ is temporary or part of a larger trend.  │
├─────────────────────────────────────────┤
│ investigation recommended — drill into   │ ← Next Step (action)
│ factors affecting APAC revenue           │
├─────────────────────────────────────────┤
│ Risk: OPERATIONAL | Confidence: 100%     │ ← Metadata
└─────────────────────────────────────────┘
```

### Frontend: Hero Insight (Compact)

```
Revenue declined 12.0% in APAC

Expand for details...
```

---

## Confidence Scoring

Each narrative includes a confidence score (0.0-1.0):

| Type | Typical Confidence |
|---|---|
| trend_increase / trend_decline | 1.0 (fact-based) |
| top_performer | 1.0 (clear winner) |
| root_cause | 0.8 (statistical/probabilistic) |
| explain_data_summary | 1.0 (metadata) |
| exploration_suggestion | 0.85 (heuristic) |
| comparison_insight | 1.0 (calculated) |

Confidence influences UI rendering (e.g., opacity, highlight color).

---

## Keywords for Searching/Filtering

Each narrative includes keywords for UX enhancements:

```python
narrative.keywords
# ["revenue", "decline", "decrease", "apac"]

# Use in UI:
# - Filter "show only decline insights"
# - Search "find all revenue insights"
# - Highlight keywords in narrative text
```

---

## Checklist: Done When ✅

- ✅ **Replace flat one-line output:** Now returns structured Narrative with 3 layers
- ✅ **Three-layer structure:** headline, summary, next_step
- ✅ **Narrative templates:** 7 templates (trend increase/decline, top performer, root cause, explain data, exploration, comparison)
- ✅ **Structured output:** Narrative dataclass, not strings
- ✅ **Tone rules:** Calm, executive, operational, no hype, no developer phrasing
- ✅ **Ready for rendering:** Hero insight = narrative.headline directly
- ✅ **Enterprise sound:** Premium language, strategic context, clear actions

---

## Key Benefits

### For Users
1. **Clarity:** Understand what happened (headline), why it matters (summary), what to do (next step)
2. **Action-oriented:** Every insight includes a specific next step
3. **Professional tone:** Sounds like enterprise software, not placeholder text
4. **Confidence indicators:** Know how reliable the insight is

### For Product Teams
1. **Structured data:** Easy to render and customize in UI
2. **Type safety:** Python dataclasses prevent errors
3. **Extensible:** Add new templates without touching core logic
4. **Searchable:** Keywords enable better UX features
5. **Tonal consistency:** All narratives follow same principles
6. **Backward compatible:** Old code expecting strings still works

---

## Integration with Rest of Stack

### With Scenario Handlers (Step 2)
Narrative engine should replace generic "narratives" from scenarios:
```python
# Scenario returns insight data
scenario_result = {
    "data": [...],
    "narrative": "Revenue distribution shows strong performance",  # Old
}

# Should instead return insight for narrative generation
insight = {
    "type": "top_performer",
    "metric": "Revenue",
    "entity": "North America",
}
narrative = engine.generate(insight)  # New: structured, executive-grade
```

### With Playground API
Hero insight field now gets premium narrative:
```python
narrative = engine.generate(insight)
response = PlaygroundQueryResponse(
    hero_insight=narrative.headline,  # "Revenue increased 15% in EMEA"
    why_this_answer=narrative.summary,  # Full context
    suggestions=[narrative.next_step]  # Action
)
```

### With Governance (Step 3a)
Narrative tone aligns with governance tone:
- Blocked queries: OPERATIONAL tone ("investigation recommended")
- Approved queries: EXECUTIVE tone ("strong market position")
- Error scenarios: ANALYTICAL tone ("review approach")

---

## Example: Complete User Journey

```
1. User queries: "Show revenue by region"
2. Scenario handler (Step 2) identifies: top performer = North America
3. Creates insight: {"type": "top_performer", "metric": "Revenue", "entity": "North America"}
4. Narrative engine (Step 4) generates:
   - Headline: "North America leads in Revenue"
   - Summary: "...strong market position..."
   - Next Step: "Analyze success factors..."
5. Playground API returns response with structured narrative
6. Frontend renders:
   - Hero insight: "North America leads in Revenue"
   - Expanded view: Full summary
   - CTA: "Analyze success factors"
7. User clicks next step → new analysis → cycle repeats
```

---

## Summary

**Step 4 transforms narrative generation from placeholder copy into executive-grade, structured, action-oriented insight narratives.**

The engine now provides:
- **Three-layer structure** (headline, summary, next_step)
- **Seven templates** covering common insight types
- **Type-safe output** (Narrative dataclass)
- **Premium wording** (no hype, enterprise-appropriate)
- **Confidence scoring** (0.0-1.0)
- **Keywords** (for UX filtering)
- **Tonal awareness** (EXECUTIVE, OPERATIONAL, ANALYTICAL)

**Result:** Hero insights are now compelling, contextual, and actionable.

---

**Status:** ✅ Step 4 Complete / Ready for Step 5 (Query Rewriting)

