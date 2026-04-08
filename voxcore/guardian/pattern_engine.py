def apply_pattern_scoring(risk_score, flags, metadata):
    """
    Applies pattern-based risk scoring and flags based on detected pattern in metadata.
    Returns (risk_score, flags, pattern_info_dict or None)
    """
    pattern_name, confidence = detect_pattern(metadata)

    if not pattern_name:
        return risk_score, flags, None

    pattern = PATTERNS.get(pattern_name)

    if not pattern:
        return risk_score, flags, None

    # Basic validation placeholder (expand later)
    valid = True

    if valid:
        risk_score += pattern.get("risk_adjustment", 0)
        flags.append("TRUSTED_PATTERN")
        return risk_score, flags, {
            "pattern": pattern_name,
            "confidence": confidence if confidence is not None else pattern.get("confidence", 0.0)
        }

    return risk_score, flags, None
from voxcore.patterns.loader import PATTERNS


def detect_pattern(metadata):
    if not metadata:
        return None, None
    return (
        metadata.get("pattern"),
        metadata.get("pattern_confidence")
    )


    pattern_name, confidence = detect_pattern(metadata)

    if not pattern_name:
        return risk_score, flags, None

    pattern = PATTERNS.get(pattern_name)

    if not pattern:
        return risk_score, flags, None

    # Basic validation placeholder (expand later)
    valid = True  

    if valid:
        risk_score += pattern.get("risk_adjustment", 0)
        flags.append("TRUSTED_PATTERN")

        return risk_score, flags, {
            "pattern": pattern_name,
            "confidence": confidence if confidence is not None else pattern.get("confidence", 0.0)
        }

    return risk_score, flags, None
