"""
Базовый SQLAlchemy класс для моделей
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Создаем Base для всех моделей
Base = declarative_base()


class BaseModel(Base):
    """Базовый класс для всех моделей с общими полями"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Экспорт Base для удобства импорта
__all__ = ["Base", "BaseModel"]