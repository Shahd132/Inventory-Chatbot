import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("MODEL_API_KEY"))

print("Available Models:\n")

for model in genai.list_models():
    print("Model Name:", model.name)
    print("Supported Methods:", model.supported_generation_methods)
    print("-" * 50)