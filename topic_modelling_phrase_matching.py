#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 23:14:17 2025

@author: manickamvalliappan
"""

import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
import re


nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")  


data_path = "difference1.csv"  
df = pd.read_csv(data_path)

keyword_expertise = {
    "issue_areas": ["just transition", "digital resilience", "humanitarian", "cultural heritage", "biodiversity", "food systems"],
    "methodologies": ["qualitative research", "policy evaluation", "case study", "literature review", "policy brief", "predictive analytics", "desk review", "desk research"]
}


for category, terms in keyword_expertise.items():
    patterns = [nlp(term) for term in terms]
    matcher.add(category, patterns)

def keyword_match(doc):
    matches = matcher(doc)
    matched_terms = {"issue_areas": [], "methodologies": []}
    
    for match_id, start, end in matches:
        category = nlp.vocab.strings[match_id]
        if category in matched_terms:
            matched_terms[category].append(doc[start:end].text)
    
    issue_match = len(matched_terms["issue_areas"]) > 0
    method_match = len(matched_terms["methodologies"]) > 0
    
    return issue_match, method_match, matched_terms["issue_areas"], matched_terms["methodologies"]

def semantic_similarity(doc, expertise_list):
    return max((doc.similarity(nlp(term)) for term in expertise_list), default=0)

def evaluate_description(description):
    doc = nlp(description.lower())
    issue_keyword, method_keyword, matched_issues, matched_methods = keyword_match(doc)
    
    issue_similarity = semantic_similarity(doc, keyword_expertise["issue_areas"]) * 5  # Scale to 0-5
    method_similarity = semantic_similarity(doc, keyword_expertise["methodologies"]) * 5  # Scale to 0-5
    
    keyword_score = (issue_keyword * 5) + (method_keyword * 5)  # Max 10
    similarity_score = issue_similarity + method_similarity  # Max 10
    
    return keyword_score, similarity_score, method_similarity, issue_similarity, keyword_score + similarity_score, ", ".join(matched_issues), ", ".join(matched_methods)

df[["keyword_score", "similarity_score", "method_similarity_score", "issue_similarity_score", "total_score", "matched_issue_areas", "matched_methodologies"]] = df["Description"].apply(lambda x: pd.Series(evaluate_description(str(x))))

def detect_headers_and_clean(text):
    """
    Cleans and structures the scraped description:
    - Uses NLP to detect section headers
    - Formats text into readable paragraphs
    - Boldens detected headers
    - Handles bullet points & whitespace issues
    """
    if not text or text.strip() == "":
        return "No description available"


    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'(\*|\-)\s+', '• ', text)  


    doc = nlp(text)
    structured_text = []
    prev_was_header = False  

    for sent in doc.sents:
        sent_text = sent.text.strip()

       
        if (
            len(sent_text) < 10 or  
            sent_text.isupper() or  
            sent_text.endswith(":") or  
            sent_text.istitle()  
        ):
            structured_text.append(f"\n\n**{sent_text}**")  
            prev_was_header = True
        else:
            if prev_was_header:
                structured_text.append(f"\n{sent_text}")  
            else:
                structured_text.append(f" {sent_text}")  

            prev_was_header = False

    return "".join(structured_text).strip()


df["Cleaned_Description"] = df["Description"].apply(lambda x: detect_headers_and_clean(str(x)))


df = df.sort_values(by="total_score", ascending=False)
print(df[["Job Title", "Organisation", "keyword_score", "similarity_score", "total_score", "matched_issue_areas", "matched_methodologies"]])
df.to_excel("RFPs_ranked_2.xlsx", index=False)











