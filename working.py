from fastapi import FastAPI, Query, Path, HTTPException
from conn import products_collection, order_collection
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId


# fastapi app
app = FastAPI()


# order item model
class OrderItem(BaseModel):
    productId: str
    boughtQuantity: int


# user address model
class UserAddress(BaseModel):
    city: str
    country: str
    zipcode: str


# order model
class OrderCreate(BaseModel):
    items: list[OrderItem]
    total_amount: float
    user_address: UserAddress


# available quantity model
class UpdateProduct(BaseModel):
    available_quantity: int


# to get all the available products
@app.get("/products")
def get_products():
    try:
        cursor = products_collection.find()
        available_items = []

        for item in cursor:
            item["_id"] = str(item["_id"])
            available_items.append(item)

        return available_items

    except Exception as e:
        return {"error": e}


# Endpoint to create a new order
@app.post("/orders")
def create_order(order: OrderCreate):
    try:
        # time at wich order is placed
        timestamp = datetime.now()

        # Prepare the order document
        order_doc = {
            "timestamp": timestamp,
            "items": [
                {"product_id": item.productId, "bought_quantity": item.boughtQuantity}
                for item in order.items
            ],
            "total_amount": order.total_amount,
            "user_address": {
                "city": order.user_address.city,
                "country": order.user_address.country,
                "zip_code": order.user_address.zipcode,
            },
        }

        # Insert the order into MongoDB
        result = order_collection.insert_one(order_doc)

        # Return the inserted order ID
        return {"order_id": str(result.inserted_id)}

    except Exception as e:
        return {"error": e}

# get all the order from database 
@app.get("/orders")
def get_orders(
    limit: int = Query(default=10, ge=1), offset: int = Query(default=0, ge=0)
):
    try:
        orders = order_collection.find().skip(offset).limit(limit)
        result = []

        for order in orders:
            # convert the objectid to string
            order["_id"] = str(order["_id"])
            result.append(order)

        return {"orders": result}

    except Exception as e:
        return {"error": e}


# get specific order from database using order id
@app.get("/orders/{order_id}")
def get_order(order_id: str = Path(..., title="please pass the Order ID")):
    order = order_collection.find_one({"_id": ObjectId(order_id)})

    if order:
        order["_id"] = str(order["_id"])
        return {"order found": order}
    else:
        raise HTTPException(status_code=404, detail="Order not found")


# to update specific record using is product id
@app.put("/products/{product_id}")
def update_product(
    *,
    product_id: str = Path(..., title="please pass the product id"),
    update_product: UpdateProduct
):
    result = products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"Product available quantity": update_product.available_quantity}}
    )

    if result.matched_count:
        if result.modified_count:
            return {"message": "Product updated successfully"}
        else:
            return {"message": "Product already has the same available quantity"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")
