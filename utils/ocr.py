import pytesseract
from pdf2image import convert_from_path
from PIL import ImageOps, ImageEnhance, ImageOps, ImageFilter
import docx
from PyPDF2 import PdfReader
import os

# Set local paths (adjust based on your exact folder names)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POPPLER_PATH = os.path.join(BASE_DIR, 'poppler', 'library', 'bin')
TESSERACT_PATH = os.path.join(BASE_DIR, 'Tesseract-OCR', 'tesseract.exe')

# Configure pytesseract to use local Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def preprocess_image(img):
    # Convert to grayscale
    img = img.convert('L')
    # Enhance contrast
    img = ImageEnhance.Contrast(img).enhance(2.0)
    # Auto-adjust contrast and brightness
    img = ImageOps.autocontrast(img)
    # Reduce noise with median filter
    img = img.filter(ImageFilter.MedianFilter(size=3))
    # Optional: Deskew (basic correction)
    def deskew(image):
        return image.rotate(-1 * image.convert('L').getextrema()[1], expand=True)
    img = deskew(img)
    return img



# def extract_text(file_path):
#     file_ext = os.path.splitext(file_path.lower())[1]
    
#     if file_ext == '.pdf':
#         try:
#             # Use local Poppler path
#             images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
#             text = ' '.join(pytesseract.image_to_string(img) for img in images)
#             return text.strip() if text.strip() else "No text extracted from PDF"
#         except Exception as e:
#             print(f"PDF OCR failed: {e}")
#             return f"PDF OCR failed: {str(e)}"

def extract_text(file_path):
    file_ext = os.path.splitext(file_path.lower())[1]
    
    if file_ext == '.pdf':
        try:
            # Try text extraction first
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            if text.strip():
                return text.strip()
            # Fallback to OCR if no text
            images = convert_from_path(file_path, poppler_path=POPPLER_PATH, dpi=300)
            text = ' '.join(pytesseract.image_to_string(preprocess_image(img), config='--psm 6 --oem 3') for img in images)
            print(f"Extracted OCR text: {text}")
            return text.strip() if text.strip() else "No text extracted"
        except Exception as e:
            print(f"PDF extraction/OCR failed: {e}")
            return f"PDF extraction/OCR failed: {e}"

    elif file_ext == '.docx':
        doc = docx.Document(file_path)
        text = ' '.join(p.text for p in doc.paragraphs)
        return text
    
    elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"OCR failed for image: {e}")
            return f"Image OCR failed: {str(e)}"
    
    else:
        return "Unsupported file type."

if __name__ == "__main__":
    # Test the function (optional)
    sample_path = os.path.join(BASE_DIR, 'samples', 'claim1.pdf')
    if os.path.exists(sample_path):
        print(extract_text(sample_path))
    else:
        print("Sample file not found.")