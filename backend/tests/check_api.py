"""Debug script to see exact error"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

try:
    model = genai.GenerativeModel('gemini-3.6-flash')
    response = model.generate_content('Say hello')
    print("Success:", response.text)
except Exception as e:
    print("Error type:", type(e).__name__)
    print("Error message:", str(e))
