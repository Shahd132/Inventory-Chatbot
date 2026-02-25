# import pyodbc

# server = 'localhost'   # change if needed
# database = 'InventoryDB'  # your database name

# connection_string = f"""
# DRIVER={{ODBC Driver 17 for SQL Server}};
# SERVER={server};
# DATABASE={database};
# Trusted_Connection=yes;
# """

# try:
#     conn = pyodbc.connect(connection_string)
#     cursor = conn.cursor()
    
#     cursor.execute("SELECT COUNT(*) FROM Assets")
#     result = cursor.fetchone()
    
#     print("Connection successful!")
#     print("Total Assets:", result[0])

# except Exception as e:
#     print("Error:", e)

from fastapi import FastAPI, Request
import google.genai as genai

genai.configure(api_key="AIzaSyBjrbqUieKBKctfKJ3_gPijtIRfivwCwoQ")  # Replace with your actual API key

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    
    response = genai.chat.create(
        model="gemini-1.5",
        messages=[{"author": "user", "content": prompt}]
    )
    
    output_text = response.choices[0].content[0].text
    return {"response": output_text}