from fastapi import FastAPI
from pydantic import BaseModel
import os
import time
import pyodbc
from dotenv import load_dotenv
import google.genai as genai  

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("MODEL_API_KEY"))

# Database connection
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=InventoryDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: dict = {}


@app.post("/api/chat")
def chat(request: ChatRequest):
    start_time = time.time()

    prompt = f"""
You are a senior SQL Server data analyst You generate production-safe queries 
Generate only SELECT statements 
never generate INSERT, UPDATE, DELETE, DROP 
never use markdown 
you stictly follow schema
Database Schema (SQL Server):

Customers(
  CustomerId PK,
  CustomerCode,
  CustomerName,
  Email,
  Phone,
  BillingCity,
  BillingCountry,
  IsActive
)

Vendors(
  VendorId PK,
  VendorCode,
  VendorName,
  Email,
  Phone,
  City,
  Country,
  IsActive
)

Sites(
  SiteId PK,
  SiteCode,
  SiteName,
  City,
  Country,
  IsActive
)

Locations(
  LocationId PK,
  SiteId FK -> Sites.SiteId,
  LocationCode,
  LocationName,
  ParentLocationId,
  IsActive
)

Items(
  ItemId PK,
  ItemCode,
  ItemName,
  Category,
  UnitOfMeasure,
  IsActive
)

Assets(
  AssetId PK,
  AssetTag,
  AssetName,
  SiteId FK -> Sites.SiteId,
  LocationId FK -> Locations.LocationId,
  SerialNumber,
  Category,
  Status,
  Cost,
  PurchaseDate,
  VendorId FK -> Vendors.VendorId
)

Bills(
  BillId PK,
  VendorId FK -> Vendors.VendorId,
  BillNumber,
  BillDate,
  DueDate,
  TotalAmount,
  Currency,
  Status
)

PurchaseOrders(
  POId PK,
  PONumber,
  VendorId FK -> Vendors.VendorId,
  PODate,
  Status,
  SiteId FK -> Sites.SiteId
)

PurchaseOrderLines(
  POLineId PK,
  POId FK -> PurchaseOrders.POId,
  LineNumber,
  ItemId FK -> Items.ItemId,
  ItemCode,
  Quantity,
  UnitPrice
)

SalesOrders(
  SOId PK,
  SONumber,
  CustomerId FK -> Customers.CustomerId,
  SODate,
  Status,
  SiteId FK -> Sites.SiteId
)

SalesOrderLines(
  SOLineId PK,
  SOId FK -> SalesOrders.SOId,
  LineNumber,
  ItemId FK -> Items.ItemId,
  ItemCode,
  Quantity,
  UnitPrice
)

AssetTransactions(
  AssetTxnId PK,
  AssetId FK -> Assets.AssetId,
  FromLocationId FK -> Locations.LocationId,
  ToLocationId FK -> Locations.LocationId,
  TxnType,
  Quantity,
  TxnDate
)

use only the columns listed in the schema above
don't assume additional columns
don't use tables not listed in the schema

Logic Rules:
Exclude assets where Status column = 'Disposed'
when grouping by site, join Assets with Sites on SiteId
when grouping by vendor, join with Vendors
only apply IsActive = 1 filter to these tables:
Customers, Vendors, Sites, Locations, Items
don't assume other tables contain IsActive.

Time Logic Rules:
for this year:
YEAR(date_column) = YEAR(GETDATE())
For last month, filter using:
MONTH(date_column) = MONTH(DATEADD(MONTH, -1, GETDATE()))
AND YEAR(date_column) = YEAR(DATEADD(MONTH, -1, GETDATE()))
For quarterly reports of the current year:
YEAR(date_column) = YEAR(GETDATE())
AND DATEPART(QUARTER, date_column) = DATEPART(QUARTER, GETDATE())

return only one valid SQL statement. Do not return multiple queries
Question: {request.message}
"""
    try:
        response = client.models.generate_content(
            model=os.getenv("MODEL_NAME"),
            contents=prompt,
        )
        sql_query = response.text.strip()

        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    except Exception as e:
        return {
            "status": "error",
            "error_stage": "model_call",
            "error_message": str(e)
        }

    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        if len(rows) == 1 and len(rows[0]) == 1:
            value = rows[0][0]
            natural_answer = f"You have {value} items matching your query."
        else:
            lines = [", ".join([str(c) for c in row]) for row in rows]
            natural_answer = "Here are the results:\n" + "\n".join(lines)

        status = "ok"

    except Exception as e:
        return {
            "status": "error",
            "error_stage": "sql_execution",
            "sql_query": sql_query,
            "error_message": str(e)
        }

    latency = int((time.time() - start_time) * 1000)

    token_usage = {
        "prompt_tokens": len(prompt),
        "completion_tokens": len(sql_query),
        "total_tokens": len(prompt) + len(sql_query)
    }

    return {
        "natural_language_answer": natural_answer,
        "sql_query": sql_query,          
        "token_usage": token_usage,
        "latency_ms": latency,
        "provider": os.getenv("PROVIDER"),
        "model": os.getenv("MODEL_NAME" ),
        "status": status
    }
