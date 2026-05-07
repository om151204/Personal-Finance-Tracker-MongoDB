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
        """
        This constructor sets up the connection to the database and creates collections
        :return None
        """
        try:
            self.client = MongoClient(CONNECTION_STRING)
            self.db = self.client["budget_db"]
            self.collection = self.db["budgets"]
            self.cat_collection = self.db["categories"]
            print("Database budget created successfully")
        except ConnectionFailure as e:
            print("Failed to connect to database",e)

    def create_transaction(self, data):
        """
        This method creates a transaction record in the database
        :param data: Dictionary of transaction
        :return: data created in database
        """
        data["created_at"] = datetime.datetime.now()
        self.collection.insert_one(data)
        return data

    def get_all_transactions(self,page_size=2):
        """
        This method gets all the transactions in the database
        :param page_size: int
        :return: all the data from database
        """
        data = self.collection.find().limit(page_size)
        return data

    def get_transaction_by_id(self,transaction_id):
        """
        This method gets a single transaction record in the database using id
        :param transaction_id:
        :return: the extracted data from database
        """
        single_data = self.collection.find_one({"_id": ObjectId(transaction_id)})
        if single_data:
            return single_data
        else:
            return None

    def delete_transaction(self,transaction_id):
        """
        This method deletes a transaction record in the database using id
        :param transaction_id:
        :return: Success or Failure Message
        """
        record_found = self.collection.find_one({"_id":ObjectId(transaction_id)})
        if record_found:
            self.collection.delete_one({"_id": ObjectId(transaction_id)})
            return{"Successfully deleted transaction"}
        else:
            return {"Failed to delete transaction"}

    def delete_transaction_many(self,category:str):
        """
        This method deletes multiple transactions in the database
        :param category: str
        :return: Dictionary of transactions deleted
        """
        new_category = category.lower()
        return self.collection.delete_many({"category":new_category})

    def update_transaction(self,transaction_id:str,updated_data:dict):
        """
        This method updates a transaction record in the database
        :param transaction_id: str
        :param updated_data: dictionary
        :return:
        """
        updated_data["updated_at"] = datetime.datetime.now()
        result = self.collection.update_one({"_id": ObjectId(transaction_id)},{"$set":updated_data})
        if result.matched_count == 0:
            return None
        return self.collection.find_one({"_id": ObjectId(transaction_id)})

    def search_transactions(self,query:str):
        """
        This method searches for transactions in the database using query
        :param query: str
        :return: list of transactions found
        """
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}}
            ]
        }
        return list(self.collection.find(search_filter))


    def get_monthly_summary(self, year: int, month: int):
        """
        This method generates a monthly summary of the transactions
        :param year: integer
        :param month: int
        :return: the summary of the transactions
        """
        regex_pattern = f".*/{month:02d}/{year}"

        pipeline = [
            {
                "$match": {
                    "date": {"$regex": regex_pattern}
                }
            },
            {
                "$facet": {
                    "totals": [
                        {
                            "$group": {
                                "_id": None,
                                "total_income": {
                                    "$sum": {"$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]}
                                },
                                "total_expense": {
                                    "$sum": {"$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]}
                                }
                            }
                        }
                    ],
                    "category_breakdown": [
                        # Groups by category and shows total for each
                        {
                            "$group": {
                                "_id": "$category",
                                "total": {"$sum": "$amount"},
                                "type": {"$first": "$type"}
                            }
                        },
                        {"$sort": {"total": -1}}
                    ],
                    "highest_transaction": [
                        # Shows the single largest transaction of the month
                        {"$sort": {"amount": -1}},
                        {"$limit": 1}
                    ]
                }
            }
        ]

        # Ensure this points to your specific transactions collection
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def update_category(self,name:str,updated_data:dict):
        """
        This method updates a category record in the database
        :param name: str
        :param updated_data:
        :return: None or the updated collection
        """
        updated_data["updated_at"] = datetime.datetime.now()
        category = self.cat_collection.find_one({"name": name})
        if not category:
            return None

        self.cat_collection.update_one(
            {"_id": category["_id"]},
            {"$set": updated_data}
        )
        return self.cat_collection.find_one({"_id": category["_id"]})

    def delete_category(self,name:str):
        """
        This method deletes a category record in the database
        :param name: str
        :return: the deleted record in the category collection
        """
        return self.cat_collection.delete_one({"name":name})


db = Database()