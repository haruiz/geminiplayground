from enum import Enum
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from .registry import mapper_registry as reg


class EntryStatus(Enum):
    """
    Upload status enum.
    """

    PENDING = "pending"
    READY = "ready"
    ERROR = "error"


class Base(DeclarativeBase):
    registry = reg


class MultimodalPartEntry(Base):
    """
    Multimodal part model.
    """

    __tablename__ = "part"

    name: Mapped[str] = mapped_column(primary_key=True)
    content_type: Mapped[str] = mapped_column()
    status: Mapped[EntryStatus] = mapped_column(default=EntryStatus.PENDING)
    status_message: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    thumbnail: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)

    def as_dict(self):
        """
        Return the model as a dictionary.
        """
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name}, {self.name})>"


__all__ = ["MultimodalPartEntry", "EntryStatus"]
