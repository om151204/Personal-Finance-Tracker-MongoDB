from fastapi import APIRouter, status, HTTPException, Query
from finance.api.base_models import Transaction,TransactionUpdate,Category,CategoryPatch
from finance.database import db
router = APIRouter()

def serialize(transaction):
    """
    This is a helper function to serialize a transaction
    :param transaction: dictionary with transaction info
    :return: Formatted print
    """
    return {
        "id": str(transaction["_id"]),
        "title": transaction["title"],
        "description": transaction["description"],
        "amount": transaction["amount"],
        "type": transaction["type"],
        "category": transaction["category"],
        "date": transaction["date"],
        "tags": transaction["tags"],
    }

def serialize_category(category):
    """
        This is a helper function to serialize a category
        :param category: dictionary with transaction info
        :return: Formatted print
        """
    return {
        "id": str(category["_id"]),
        "name": category["name"]
    }

@router.post("/",status_code=status.HTTP_201_CREATED)
def create_transaction(transaction:Transaction):
    try:
        created_transaction = db.create_transaction(transaction.model_dump(mode="json"))
        return serialize(created_transaction)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/summary")
def get_summary(month: str):
    try:
        year, month_number = map(int, month.split("-"))
    except:
        raise HTTPException(
            status_code=400,
            detail="Month format must be YYYY-MM"
        )

    summary = db.get_monthly_summary(year, month_number)

    if not summary:
        raise HTTPException(
            status_code=404,
            detail="No transactions found for this month"
        )

    totals = summary.get("totals", [])
    category_data = summary.get("category_breakdown", [])
    highest = summary.get("highest_expense", [])

    total_income = totals[0]["total_income"] if totals else 0
    total_expense = totals[0]["total_expense"] if totals else 0

    net_balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "category_breakdown": category_data,
        "highest_expense": highest[0] if highest else None
    }

@router.get("/search",status_code=status.HTTP_200_OK)
def search_transactions(query:str):
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Search query is required")
    results = db.search_transactions(query)
    transactions = [serialize(t) for t in results]
    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No matching transaction not found")
    return transactions
@router.get("/",status_code=status.HTTP_200_OK)
def get_transactions(page_size:int=Query(10,le=100)):
    transactions = db.get_all_transactions(page_size)
    return [serialize(t) for t in transactions]

@router.get("/{id}",status_code=status.HTTP_200_OK)
def get_transaction(id_:str):
    try:
        transaction = db.get_transaction_by_id(id_)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Transaction not found")
        return serialize(transaction)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid transaction ID")



@router.delete("/{id}",status_code=status.HTTP_200_OK)
def delete_transaction(id_:str):
    try:
        res = db.delete_transaction(id_)
        return res
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid transaction ID")

@router.delete("/bulk/{category}",status_code=status.HTTP_202_ACCEPTED)
def bulk_delete_transaction(category:str):
    result = db.delete_transaction_many(category)
    if result:
        return{
            "message":"Transaction deleted successfully",
            "deleted_count": result.deleted_count,
        }
    else:
        return {"Message":"Transaction could not be deleted"}

@router.patch("/{id}",status_code=status.HTTP_200_OK)
def update_transaction(id_:str,payload:TransactionUpdate):
    try:
        updated_transaction = db.update_transaction(id_,payload.model_dump(exclude_unset=True))
        if not updated_transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Transaction not found")
        return serialize(updated_transaction)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid transaction ID")


@router.post("/post_categories/", status_code=status.HTTP_201_CREATED,tags=["categories"])
def create_category(category: Category):
    existing = db.cat_collection.find_one({"name": category.name})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    result = db.create_category(category.model_dump())
    created = db.cat_collection.find_one({"_id": result.inserted_id})

    return serialize_category(created)


@router.get("/get_categories/",tags=["categories"])
def get_categories():
    categories = db.get_categories()
    return [serialize_category(cat) for cat in categories]



@router.patch("/categories/{name}",tags=["categories"])
def update_category(name: str, payload: CategoryPatch):

    update_data = payload.model_dump(exclude_unset=True)

    updated = db.update_category(name, update_data)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return serialize_category(updated)



@router.delete("/transactions/{name}",tags=["categories"])
def delete_category(name: str):

    result = db.delete_category(name)

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return {"message": "Category deleted successfully"}



