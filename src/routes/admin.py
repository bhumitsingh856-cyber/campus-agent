from fastapi import APIRouter
from src.db.vector import get_all_namespaces
import src.db.checkpointer as d

admin_router = APIRouter()

@admin_router.get("/admin/namespaces")
def read_namespaces():
    """Get all namespaces"""
    try:
        data=get_all_namespaces()
        return {"PDF":str(data)}
    except Exception as e:
        print(e)
        return {"PDF":[]}
