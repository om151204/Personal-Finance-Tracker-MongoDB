from fastapi import APIRouter, status, HTTPException, Query
from finance.api.base_models import Transaction
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

@router.post("/",status_code=status.HTTP_201_CREATED)
def create_transaction(transaction:Transaction):
    try:
        created_transaction = db.create_transaction(transaction.model_dump(mode="json"))
        return serialize(created_transaction)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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



