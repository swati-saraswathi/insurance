import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

def extract_info(text, annotations_json):
    prompt = f"""
    Extract structured data from this OCR-extracted text: {text}
    Schema: {{
      "policy_number": str,  // e.g., "POL-261754"
      "policy_holder": str,  // e.g., "Geeta Kapoor"
      "claim_type": str,  // e.g., "Health", "Auto", "Medical, Vehicle, Property Damage"
      "effective_date": str,  // e.g., "2024-12-06"
      "diagnosis_codes": list[str],  // e.g., ["S72.001A"]
      "policy_limit": float,  // e.g., 200000.0
      "risk_indicators": list[str]  // e.g., ["Inconsistent dates"]
    }}
    Examples: {annotations_json[:3]}  # Use more examples for few-shot
    Instructions:
    - Output ONLY valid JSON.
    - Correct common OCR errors (e.g., 'l' vs '1', 'O' vs '0', missing punctuation).
    - If data is missing, infer from context or use defaults (e.g., today for date if not found).
    - No extra text or code fences.
    """
    try:
        response = model.generate_content(prompt)
        print("Raw Gemini response:", response.text)  # Debug
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return json.dumps({"error": "Gemini API failed"})

def generate_summary(extracted_json):
    prompt = """
    Generate a concise adjuster summary from this data: {json_str}
    Structure:
    - Claim Number: [num]
    - Policy Holder: [name or 'Unknown - Verify manually']
    - Type of Claim: [type or 'Unknown - Infer from description']
    - Incident Description: [2-3 sentences, summarize from text; if unknown, note 'Details incomplete']
    - Potential Issues: [Bullet list risks, e.g., 'Missing diagnosis codes - Possible fraud', or 'None detected']
    - Recommendation: [Approve, Deny, Review - based on fraud_score > 50 = Review, >80 = Deny]
    Keep under 200 words. Professional tone. Highlight gaps in data.
    """.format(json_str=json.dumps(extracted_json))
    response = model.generate_content(prompt)
    return response.text