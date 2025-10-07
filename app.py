from flask import Flask, render_template, request, jsonify, redirect
from utils.ocr import extract_text
from utils.extract import extract_info, generate_summary
from utils.fraud_score import calculate_fraud_score
from models import Session, Claim
import json
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text(filepath)
            print(f"OCR Extracted Text:\n{text}\n") # Added print statement
            raw_response = extract_info(text, open('annotations.json').read())
            try:
                cleaned_response = raw_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:-3].strip()  # Remove ```json and ```
                extracted_json = json.loads(cleaned_response)
                # Handle invalid or null responses
                if not extracted_json.get('policy_number') or extracted_json.get('policy_number') == 'null':
                    print(f"Invalid extraction: {extracted_json}")
                    extracted_json = {
                        "policy_number": f"POL-{uuid.uuid4()}",
                        "policy_holder": "Unknown",
                        "claim_type": "Unknown",
                        "effective_date": "2023-10-01",
                        "diagnosis_codes": [],
                        "policy_limit": 0.0,
                        "risk_indicators": ["Extraction failed"]
                    }
                    # Generate a unique claim number if LLM fails to extract one
                    if extracted_json['policy_number'] is None or extracted_json['policy_number'] == "null":
                        extracted_json['policy_number'] = f"POL-{uuid.uuid4()}"
                else:
                    # If policy_number is extracted, use it to ensure uniqueness
                    pass # No change needed if policy_number is already set
            except json.decoder.JSONDecodeError as e:
                print(f"JSON parse error: {e}, Raw response: {raw_response}")
                extracted_json = {
                    "policy_number": f"POL-{uuid.uuid4()}", # Also generate UUID here
                    "policy_holder": "Unknown",
                    "claim_type": "Unknown",
                    "effective_date": "2023-10-01",
                    "diagnosis_codes": [],
                    "policy_limit": 0.0,
                    "risk_indicators": ["JSON parse failed"]
                }
            fraud_score = calculate_fraud_score(extracted_json)
            summary = generate_summary(extracted_json)
            session = Session()
            claim = Claim(
                claim_number=extracted_json['policy_number'], # Use policy_number for claim_number column
                extracted_data=extracted_json,
                fraud_score=fraud_score,
                summary=summary
            )
            session.add(claim)
            session.commit()
            policy_id = claim.claim_number  # Use claim_number as identifier, which now holds policy_number
            session.close()
            return redirect(f'/summary/{policy_id}')
        return jsonify({'error': 'No file uploaded'}), 400
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/summary/<policy_num>') # Change route parameter
def get_summary(policy_num):
    session = Session()
    claim = session.query(Claim).filter_by(claim_number=policy_num).first() # Query by claim_number column, which stores policy_number
    if claim:
        rendered = render_template('summary.html', claim=claim)
        session.close()  # Close after rendering
        return rendered
    session.close()  # Close if not found
    return 'Not found', 404

if __name__ == '__main__':
    app.run(debug=True)