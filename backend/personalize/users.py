users = {
    1: {"name": "Ramesh", "risk_tolerance": "low", "portfolio": ["TCS", "HDFC"], "age_bracket": "45-60"},
    2: {"name": "Priya", "risk_tolerance": "medium", "portfolio": ["INFY", "RELIANCE"], "age_bracket": "25-35"},
    3: {"name": "Aakash", "risk_tolerance": "high", "portfolio": ["TATAMOTORS"], "age_bracket": "20-30"},
}

def get_user(user_id):
    if user_id not in users:
        raise ValueError(f"No user with id {user_id}")
    return users[user_id]
