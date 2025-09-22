from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# Allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Admin Endpoints ----------------

@app.post("/admin/add-product")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...)
):
    # Generate unique filename
    filename = f"{uuid.uuid4()}_{file.filename}"
    content = await file.read()

    # Upload to Supabase storage bucket 'images'
    supabase.storage.from_("images").upload(filename, content)

    # Get public URL
    image_url = supabase.storage.from_("images").get_public_url(filename)

    # Insert into products table
    supabase.table("products").insert({
        "name": name,
        "description": description,
        "price": price,
        "image_url": image_url
    }).execute()

    return {"message": "Product added successfully", "image_url": image_url}

@app.get("/admin/products")
def get_all_products():
    products = supabase.table("products").select("*").execute()
    return {"products": products.data}

# ---------------- Customer Endpoints ----------------

@app.get("/customer/products")
def list_products():
    products = supabase.table("products").select("*").execute()
    return {"products": products.data}

@app.post("/customer/place-order")
def place_order(
    customer_name: str = Form(...),
    customer_email: str = Form(None),
    products: str = Form(...)  # JSON string of products [{product_id, name, quantity, price}]
):
    import json
    product_list = json.loads(products)

    # Generate new order_id
    all_orders = supabase.table("orders").select("order_id").execute().data
    max_order_id = max([o["order_id"] for o in all_orders], default=100)
    new_order_id = max_order_id + 1

    # Insert each product as a separate row
    for item in product_list:
        supabase.table("orders").insert({
            "order_id": new_order_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "product_name": item["name"],
            "product_price": item["price"],
            "quantity": item["quantity"],
            "total_price": item["price"] * item["quantity"],
            "status": "pending"
        }).execute()

    return {"message": "Order placed successfully", "order_id": new_order_id}

@app.get("/customer/orders/{customer_name}")
def get_customer_orders(customer_name: str):
    orders = supabase.table("orders").select("*").eq("customer_name", customer_name).execute()
    return {"orders": orders.data}
