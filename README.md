**#AI-Powered Insurance Claims Processing System**
Overview
This project is a prototype for an AI-powered insurance claims processing system that automates the extraction, analysis, and summarization of claim data from various document types (PDFs, images, DOCX). Leveraging OCR (Tesseract with Poppler), Google Gemini for structured data extraction, and a Flask-based web interface, it generates summaries and fraud scores for adjusters.

Features

1. Document Ingestion: Supports scanned PDFs, images (JPG, PNG), and DOCX files.
2. OCR Extraction: Uses Tesseract with Poppler to extract text from scanned documents.
3. Data Extraction: Employs Google Gemini to convert raw text into structured JSON (claim number, policy holder, etc.).
4. Fraud Detection: Calculates a fraud score based on extracted data and flags risks.
5. Summary Generation: Provides a concise adjuster summary with recommendations (Approve, Review, Deny).
6. Web Interface: Flask-based app for uploading files and viewing summaries.

Prerequisites

Python 3.9+
Virtual Environment (recommended)

Dependencies:

flask
pdf2image
pytesseract
python-docx
google-generativeai
PyPDF2 (optional for text-based PDFs)
pillow
sqlalchemy (for database)


External Tools:

Tesseract OCR (included locally in tesseract folder)
Poppler (included locally in poppler/bin folder)
