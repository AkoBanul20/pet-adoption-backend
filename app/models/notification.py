from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Text,
    ForeignKey,
    Boolean,
)

from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), index=True)
    messages = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    _metadata = Column(Text, nullable=True)
