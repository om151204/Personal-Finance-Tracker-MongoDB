import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure
from bson import ObjectId


load_dotenv()
CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(CONNECTION_STRING)
            self.db = self.client["budget_db"]
            self.collection = self.db["budgets"]
            print("Database budget created successfully")
        except ConnectionFailure as e:
            print("Failed to connect to database",e)

    def create_transaction(self, data):
        self.collection.insert_one(data)
        return data

    def get_all_transactions(self,page_size=2):
        data = self.collection.find().limit(page_size)
        return data

    def get_transaction_by_id(self,transaction_id):
        single_data = self.collection.find_one({"_id": ObjectId(transaction_id)})
        if single_data:
            return single_data
        else:
            return None

    def delete_transaction(self,transaction_id):
        record_found = self.collection.find_one({"_id":ObjectId(transaction_id)})
        if record_found:
            self.collection.delete_one({"_id": ObjectId(transaction_id)})
            return{"Successfully deleted transaction"}
        else:
            return {"Failed to delete transaction"}

db = Database()