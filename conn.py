from dummy_products import dummy_products
from pymongo.mongo_client import MongoClient


password = ""  # enter your password

uri = "mongodb+srv://root:<password>@cluster0.le8t0.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# create the databse
try:
    db = client["eccomerce"]
    products_collection = db["products"]
    order_collection = db["order"]
except Exception as e:
    print(e)


# insert dummy products
def insert_dummy_products():
    products_collection.insert_many(dummy_products)
