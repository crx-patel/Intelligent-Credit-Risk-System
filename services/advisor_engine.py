# ═════════════════════════════════════════════════════════════════════════════
# Advisor Engine - Financial Advice Generation
# ═════════════════════════════════════════════════════════════════════════════

"""
Financial advice generation engine.
Provides personalized recommendations based on credit risk assessment.
"""


# ═════════════════════════════════════════════════════════════════════════════
# ADVICE GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def generate_advice(risk: str) -> list:
    """
    Generate financial advice based on risk classification.
    
    Args:
        risk (str): Risk classification (High Risk, Medium Risk, Low Risk)
        
    Returns:
        list: List of personalized financial recommendations
    """
    if risk == "High Risk":
        return [
            "Immediately reduce your debt ratio",
            "Avoid applying for new loans",
            "Clear pending late payments as soon as possible",
            "Increase monthly income stability",
            "Consult a financial advisor for debt restructuring"
        ]

    elif risk == "Medium Risk":
        return [
            "Reduce credit card utilization below 30%",
            "Avoid missing any upcoming payments",
            "Try to increase monthly savings",
            "Limit new credit inquiries for next 6 months"
        ]

    else:  # Low Risk
        return [
            "Loan approval chances are good",
            "Maintain your good credit history",
            "Continue making timely payments",
            "You may qualify for better interest rates"
        ]