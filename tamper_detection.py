import cv2
import easyocr
import re
reader = easyocr.Reader(['en'], gpu=False)

def detect_tampering(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return "Suspicious", "Image Not Found"

    results = reader.readtext(image)

    extracted_text = ""

    for (bbox, text, prob) in results:
        if prob > 0.3:   # confidence threshold
            extracted_text += text

    print("Raw OCR:", extracted_text)

    cleaned_text = re.sub(r'[^A-Z0-9]', '', extracted_text.upper())

    print("Cleaned OCR:", cleaned_text)

    plate_pattern = r'[A-Z]{2}[0-9]{1,2}[A-Z]{1}[0-9]{4,5}'

    match = re.search(plate_pattern, cleaned_text)

    if match:
        plate_number = match.group()
        tamper_status = "Normal"
    else:
        plate_number = "Not Detected"
        tamper_status = "Suspicious"

    return tamper_status, plate_number