def generate_advice(risk):

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

    else:
        return [
            "Loan approval chances are good",
            "Maintain your good credit history",
            "Continue making timely payments",
            "You may qualify for better interest rates"
        ]