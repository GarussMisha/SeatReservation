"""
Window - окна на плане помещения
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Window(BaseModel):
    """
    Модель для окон на плане помещения
    
    Атрибуты:
        room_object_id: ID объекта в таблице room_objects
        width: Ширина окна в пикселях
        height: Высота окна в пикселях
        is_open: Открыто ли окно (для визуализации)
        window_type: Тип окна (single, double, panoramic)
    """
    __tablename__ = "windows"

    room_object_id = Column(Integer, ForeignKey("room_objects.id", ondelete="CASCADE"), nullable=False, unique=True, comment="ID объекта")
    width = Column(Integer, default=100, comment="Ширина окна")
    height = Column(Integer, default=60, comment="Высота окна")
    is_open = Column(Boolean, default=False, comment="Открыто ли окно")
    window_type = Column(String(20), nullable=False, default="single", comment="Тип окна")

    # Отношение
    room_object = relationship("RoomObject", back_populates="window_data")

    def __repr__(self):
        return f"<Window(id={self.id}, width={self.width}, height={self.height})>"
