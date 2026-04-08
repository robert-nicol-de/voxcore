from typing import List, Dict, Any, Optional


def run_root_cause_analysis(
    rows: List[Dict[str, Any]],
    metric: str,
    dimension: Optional[str],
    breakdown_dimension: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Identifies top contributing entity to metric change
    """

    if not rows or not breakdown_dimension:
        return None

    try:
        # --- Group by breakdown dimension ---
        grouped = {}

        for r in rows:
            key = r.get(breakdown_dimension)
            val = r.get(metric)

            if key is None or val is None:
                continue

            try:
                val = float(val)
            except:
                continue

            if key not in grouped:
                grouped[key] = []

            grouped[key].append(val)

        # --- Calculate total change ---
        total_first = 0
        total_last = 0

        for r in rows:
            val = r.get(metric)
            if val is None:
                continue
            try:
                val = float(val)
            except:
                continue

            if r == rows[0]:
                total_first += val
            if r == rows[-1]:
                total_last += val

        total_delta = total_last - total_first

        if total_delta == 0:
            return None

        # --- Calculate growth per entity and contribution % ---
        contributions = []

        for entity, values in grouped.items():
            if len(values) < 2:
                continue

            first = values[0]
            last = values[-1]

            delta = last - first

            contribution_pct = abs(delta / total_delta) if total_delta != 0 else 0

            contributions.append({
                "entity": entity,
                "delta": delta,
                "contribution_pct": round(contribution_pct, 3)
            })

        if not contributions:
            return None

        # --- Sort by importance ---
        contributions = sorted(
            contributions,
            key=lambda x: abs(x["delta"]),
            reverse=True
        )

        top = contributions[0]

        return {
            "type": "root_cause",
            "dimension": breakdown_dimension,
            "top_driver": top,
            "drivers": contributions[:3]  # top 3
        }

    except Exception:
        return None
