def calculate_fraud_score(data):
    score = 35
    if data.get('amount_claimed', 0) > 10000:
        score += 30
    if 'Extraction failed' in data.get('risk_indicators', []):
        score += 20  # Flag incomplete data as medium risk
    if data.get('incident_date') == '2023-10-01':  # Default date as suspicious
        score += 15
    # ... (existing rules)
    return min(score, 100)