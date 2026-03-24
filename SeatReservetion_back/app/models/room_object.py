"""
RoomObject - базовая модель для всех объектов на плане помещения
Стены, двери, окна, рабочие места, принтеры и другие объекты
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class RoomObject(BaseModel):
    """
    Базовая модель для всех объектов на плане помещения
    
    Атрибуты:
        room_id: ID помещения, к которому принадлежит объект
        object_type: Тип объекта (wall, door, window, workspace, printer, kitchen, meeting_room, staircase)
        x: Координата X левого верхнего угла (в пикселях относительно холста)
        y: Координата Y левого верхнего угла (в пикселях относительно холста)
        rotation: Угол поворота объекта в градусах (0, 90, 180, 270)
        width: Ширина объекта в пикселях
        height: Высота объекта в пикселях
        name: Пользовательское имя объекта (например, "Рабочее место 1")
        description: Описание объекта
        is_active: Активен ли объект (для рабочих мест)
        properties: JSON строка с дополнительными свойствами объекта
    """
    __tablename__ = "room_objects"

    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True, comment="ID помещения")
    object_type = Column(String(50), nullable=False, index=True, comment="Тип объекта")
    x = Column(Float, default=0.0, comment="Координата X")
    y = Column(Float, default=0.0, comment="Координата Y")
    rotation = Column(Integer, default=0, comment="Угол поворота в градусах")
    width = Column(Float, default=100.0, comment="Ширина объекта")
    height = Column(Float, default=50.0, comment="Высота объекта")
    name = Column(String(200), nullable=True, comment="Имя объекта")
    description = Column(String(1000), nullable=True, comment="Описание объекта")
    is_active = Column(Boolean, default=True, comment="Активен ли объект")
    properties = Column(Text, nullable=True, comment="JSON с дополнительными свойствами")

    # Отношение к помещению
    room = relationship("Room", back_populates="room_objects")

    # Отношения к специализированным моделям
    workspace_data = relationship("WorkspaceOnPlan", back_populates="room_object", uselist=False, cascade="all, delete-orphan")
    wall_data = relationship("Wall", back_populates="room_object", uselist=False, cascade="all, delete-orphan")
    door_data = relationship("Door", back_populates="room_object", uselist=False, cascade="all, delete-orphan")
    window_data = relationship("Window", back_populates="room_object", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RoomObject(id={self.id}, type={self.object_type}, room_id={self.room_id})>"
