"""
API роуты для статусов
Предоставляет эндпоинт для получения всех статусов системы.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.status import Status

router = APIRouter(tags=["statuses"])

@router.get("/", response_model=List[Dict[str, Any]])
def get_statuses(db: Session = Depends(get_db)):
    """
    Получить список всех статусов
    
    Returns:
        Список статусов с id, name и description
    """
    try:
        statuses = db.query(Status).all()
        return [
            {
                "id": status.id,
                "name": status.name,
                "description": status.description
            }
            for status in statuses
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статусов: {str(e)}"
        )