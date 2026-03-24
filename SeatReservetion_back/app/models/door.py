"""
Door - двери на плане помещения
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class Door(BaseModel):
    """
    Модель для дверей на плане помещения
    
    Атрибуты:
        room_object_id: ID объекта в таблице room_objects
        door_type: Тип двери (single, double, sliding)
        swing_direction: Направление открытия (left, right, none)
        is_open: Открыта ли дверь (для визуализации)
        width: Ширина двери в пикселях
    """
    __tablename__ = "doors"

    room_object_id = Column(Integer, ForeignKey("room_objects.id", ondelete="CASCADE"), nullable=False, unique=True, comment="ID объекта")
    door_type = Column(String(20), nullable=False, default="single", comment="Тип двери")
    swing_direction = Column(String(10), nullable=False, default="left", comment="Направление открытия")
    is_open = Column(Boolean, default=False, comment="Открыта ли дверь")
    width = Column(Integer, default=80, comment="Ширина двери")

    # Отношение
    room_object = relationship("RoomObject", back_populates="door_data")

    def __repr__(self):
        return f"<Door(id={self.id}, type={self.door_type})>"
