import os
import pandas as pd
from PyPDF2 import PdfReader
import re

def gender_budget_score(sentence):
    words = sentence.lower().split()
    gender_pos = [i for i, w in enumerate(words) if "gender" in w]
    budget_pos = [i for i, w in enumerate(words) if "budget" in w]
    
    if not gender_pos or not budget_pos:
        return None
    
    min_distance = min(abs(g - b) for g in gender_pos for b in budget_pos)
    return 1 / (min_distance + 1)

pdf_folder = os.path.join(os.getcwd(), "ndc_pdfs")
records = []

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(pdf_folder, filename)
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                page_text = page_text.replace('\n', ' ')
                text += page_text + " "
            
            text = re.sub(r'\s+', ' ', text)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            scores = []
            for s in sentences:
                if "gender" in s.lower() and "budget" in s.lower():
                    score = gender_budget_score(s)
                    if score is not None:
                        scores.append(score)
            
            avg_score = sum(scores)/len(scores) if scores else 0
            
            records.append({
                "File_Name": filename,
                "avg_gender_budget_score": avg_score
            })
        except Exception as e:
            print(f"Error reading {filename}: {e}")

df = pd.DataFrame(records)
print(df)