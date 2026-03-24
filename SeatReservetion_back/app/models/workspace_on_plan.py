"""
WorkspaceOnPlan - рабочие места на плане помещения
Связывает RoomObject с Workspace из основной таблицы
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import BaseModel


class WorkspaceOnPlan(BaseModel):
    """
    Модель для рабочих мест на плане помещения
    
    Атрибуты:
        room_object_id: ID объекта в таблице room_objects
        workspace_id: ID рабочего места в таблице workspaces (может быть NULL для новых мест)
        status_id: ID статуса рабочего места (свободно, занято, не активно)
        workspace_number: Номер рабочего места (автогенерируемый)
    """
    __tablename__ = "workspaces_on_plan"

    room_object_id = Column(Integer, ForeignKey("room_objects.id", ondelete="CASCADE"), nullable=False, unique=True, comment="ID объекта")
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, comment="ID рабочего места")
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False, default=1, comment="ID статуса")
    workspace_number = Column(Integer, nullable=True, comment="Номер рабочего места")

    # Отношения
    room_object = relationship("RoomObject", back_populates="workspace_data")
    workspace = relationship("Workspace", back_populates="plan_data")
    status = relationship("Status")

    def __repr__(self):
        return f"<WorkspaceOnPlan(id={self.id}, workspace_id={self.workspace_id}, number={self.workspace_number})>"
