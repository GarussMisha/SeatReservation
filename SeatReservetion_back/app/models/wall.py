"""
Wall - стены на плане помещения
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Wall(BaseModel):
    """
    Модель для стен на плане помещения
    
    Атрибуты:
        room_object_id: ID объекта в таблице room_objects
        wall_type: Тип стены (horizontal, vertical, diagonal)
        length: Длина стены в пикселях
        thickness: Толщина стены в пикселях
        has_window: Есть ли в стене окно
        has_door: Есть ли в стене дверь
    """
    __tablename__ = "walls"

    room_object_id = Column(Integer, ForeignKey("room_objects.id", ondelete="CASCADE"), nullable=False, unique=True, comment="ID объекта")
    wall_type = Column(String(20), nullable=False, default="horizontal", comment="Тип стены")
    length = Column(Integer, default=200, comment="Длина стены")
    thickness = Column(Integer, default=10, comment="Толщина стены")
    has_window = Column(Boolean, default=False, comment="Есть ли окно")
    has_door = Column(Boolean, default=False, comment="Есть ли дверь")

    # Отношение
    room_object = relationship("RoomObject", back_populates="wall_data")

    def __repr__(self):
        return f"<Wall(id={self.id}, type={self.wall_type}, length={self.length})>"
