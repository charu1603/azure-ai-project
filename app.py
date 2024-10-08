import os
from flask import Flask, request, render_template
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Azure Cognitive Services Configuration
 # Replace with your Azure subscription key


@app.route('/', methods=['GET', 'POST'])
def index():
    text = None
    safety_message = None
    try:
        if request.method == 'POST':
            file = request.files['image']
            if file and file.filename.endswith(('png', 'jpg', 'jpeg', 'jfif', 'webp')):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                # OCR processing with Azure Cognitive Services
                text = azure_ocr(filepath)
                os.remove(filepath)  # Optionally remove the file after processing

                # Manual safety check based on the extracted text (simulated check)
                if text:
                    safety_message = manual_safety_check(text)
                else:
                    safety_message = "No text extracted from image."
            else:
                safety_message = "Please upload a valid image file."
    except Exception as e:
        safety_message = f"An error occurred: {str(e)}"  # Capture the exception message

    return render_template('index.html', text=text, safety_message=safety_message)


def azure_ocr(image_path):
    """Extract text from an image using Azure OCR."""
    try:
        with open(image_path, 'rb') as image_file:
            headers = {
                'Ocp-Apim-Subscription-Key': AZURE_SUBSCRIPTION_KEY,
                'Content-Type': 'application/octet-stream',
            }
            params = {'language': 'unk', 'detectOrientation': 'true'}
            response = requests.post(AZURE_OCR_ENDPOINT, headers=headers, params=params, data=image_file)
        
        # Check response status
        if response.status_code == 200:
            ocr_data = response.json()
            extracted_text = ""
            for region in ocr_data['regions']:
                for line in region['lines']:
                    for word in line['words']:
                        extracted_text += word['text'] + " "
            return extracted_text.strip()
        else:
            return f"Error with OCR: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error during OCR processing: {str(e)}"


def manual_safety_check(text):
    """Manual safety check using if-else logic."""
    if "milk" in text.lower():
        return "Product contains milk. Safe to consume for non-lactose-intolerant people."
    elif "gluten" in text.lower():
        return "Product contains gluten. May not be safe for gluten-sensitive individuals."
    elif "sugar" in text.lower():
        return "Product contains sugar. High sugar content may be harmful."
    elif "organic" in text.lower():
        return "Product is organic. Safe to consume."
    elif "expired" in text.lower():
        return "Product is expired. Not safe to consume."
    else:
        return "No harmful ingredients detected. Product is safe to consume."


if __name__ == '__main__':
    app.run(debug=True)
