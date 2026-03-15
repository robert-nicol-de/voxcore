"""
VoxCore SQL Accuracy Score System (VSAS)
Calculates the overall reliability score for the SQL benchmark suite.
"""

def calculate_vsas(planner, syntax, logic, execution, repair):
    """
    Calculate the VoxCore SQL Reliability Score (VSAS)
    Args:
        planner (float): Planner accuracy percentage (0-100)
        syntax (float): SQL syntax accuracy percentage (0-100)
        logic (float): SQL logic accuracy percentage (0-100)
        execution (float): Execution success percentage (0-100)
        repair (float): Repair success percentage (0-100)
    Returns:
        float: Final VSAS score (0-100, rounded to 2 decimals)
    """
    score = (
        planner * 0.25
        + syntax * 0.20
        + logic * 0.25
        + execution * 0.20
        + repair * 0.10
    )
    return round(score, 2)

if __name__ == "__main__":
    # Example usage
    planner = 92
    syntax = 98
    logic = 90
    execution = 97
    repair = 85
    score = calculate_vsas(planner, syntax, logic, execution, repair)
    print("VoxCore SQL Reliability Score:", score)
