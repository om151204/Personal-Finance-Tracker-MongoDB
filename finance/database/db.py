import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure
from bson import ObjectId
import datetime


load_dotenv()
CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(CONNECTION_STRING)
            self.db = self.client["budget_db"]
            self.collection = self.db["budgets"]
            self.cat_collection = self.db["categories"]
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

    def delete_transaction_many(self,category:str):
        new_category = category.lower()
        return self.collection.delete_many({"category":new_category})

    def update_transaction(self,transaction_id:str,updated_data:dict):
        updated_data["updated_at"] = datetime.datetime.now()
        result = self.collection.update_one({"_id": ObjectId(transaction_id)},{"$set":updated_data})
        if result.matched_count == 0:
            return None
        return self.collection.find_one({"_id": ObjectId(transaction_id)})

    def search_transactions(self,query:str):
        # Use a dictionary for the filter, NOT an ObjectId
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}}
            ]
        }
        # find() returns a cursor
        return list(self.collection.find(search_filter))

    def create_category(self,data:dict):
        data["created_at"] = datetime.datetime.now()
        return self.cat_collection.insert_one(data)

    def get_categories(self):
        return self.cat_collection.find()

    def update_category(self,name:str,updated_data:dict):
        result = self.cat_collection.update_one({"name":name},{"$set":updated_data})
        if result.matched_count == 0:
            return None
        return self.cat_collection.find_one({"name":name})

    def delete_category(self,name:str):
        return self.cat_collection.delete_one({"name":name})



db = Database()