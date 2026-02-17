from fastapi import APIRouter, status, HTTPException, Query
from finance.api.base_models import Transaction,TransactionUpdate,Category
from finance.database import db
router = APIRouter()

def serialize(transaction):
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
def get_transaction(id:str):
    try:
        transaction = db.get_transaction_by_id(id)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Transaction not found")
        return serialize(transaction)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid transaction ID")

@router.delete("/{id}",status_code=status.HTTP_200_OK)
def delete_transaction(id:str):
    try:
        res = db.delete_transaction(id)
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
def update_transaction(id:str,payload:TransactionUpdate):
    try:
        updated_transaction = db.update_transaction(id,payload.model_dump(exclude_unset=True))
        if not updated_transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Transaction not found")
        return serialize(updated_transaction)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid transaction ID")


@router.post("/get_transactions/", status_code=status.HTTP_201_CREATED,tags=["categories"])
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


@router.get("/transactions/",tags=["categories"])
def get_categories():
    categories = db.get_categories()
    return [serialize(cat) for cat in categories]


# PATCH
@router.patch("/transactions/{name}",tags=["categories"])
def update_category(name: str, payload: Category):

    update_data = payload.model_dump()

    updated = db.update_category(name, update_data)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return serialize(updated)


# DELETE
@router.delete("/transactions/{name}",tags=["categories"])
def delete_category(name: str):

    result = db.delete_category(name)

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return {"message": "Category deleted successfully"}



