"""
generate_explanation.py
────────────────────────
Rule-based credit risk explanation generator.
Replaces the LSTM/TensorFlow model for deployment compatibility.
"""


def generate_explanation(risk_score: str) -> str:
    """
    Generate a human-readable explanation for a given risk category.

    Args:
        risk_score (str): "High Risk", "Medium Risk", or "Low Risk"

    Returns:
        str: Explanation text
    """

    if risk_score == "High Risk":
        return (
            "High debt ratio and elevated credit utilization significantly increase your default risk. "
            "Multiple late payment indicators detected in your financial profile suggest instability. "
            "Your revolving credit usage is above safe thresholds, which lenders view unfavorably. "
            "Immediate steps to reduce outstanding debt and improve payment discipline are strongly recommended. "
            "Consider consulting a financial advisor to create a structured repayment plan."
        )

    elif risk_score == "Medium Risk":
        return (
            "Moderate financial risk detected based on your credit profile. "
            "Your debt ratio is manageable but your credit utilization could be improved. "
            "Some minor delinquency indicators are present but not critical at this stage. "
            "Maintaining consistent on-time payments and reducing revolving balances will help lower your risk. "
            "With disciplined financial habits over the next 6-12 months, your profile can improve significantly."
        )

    else:
        return (
            "Low financial risk detected — your credit profile looks healthy and well-managed. "
            "Your debt ratio and credit utilization are well within safe limits. "
            "No significant late payment history detected, which reflects strong financial discipline. "
            "You are in a favorable position for loan approvals and credit products. "
            "Continue your current financial habits to maintain this strong credit standing."
        )