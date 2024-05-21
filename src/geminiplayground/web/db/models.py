from enum import Enum

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .registry import mapper_registry as reg


class EntryStatus(Enum):
    """
    Upload status enum.
    """

    PENDING = "pending"
    READY = "ready"
    ERROR = "error"


@reg.mapped_as_dataclass
class MultimodalPartEntry:
    """
    Multimodal part model.
    """

    __tablename__ = "part"

    name: Mapped[str] = mapped_column(primary_key=True)
    content_type: Mapped[str] = mapped_column()
    status: Mapped[EntryStatus] = mapped_column(default=EntryStatus.PENDING)
    status_message: Mapped[str] = mapped_column(default="")

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name}, {self.name})>"
