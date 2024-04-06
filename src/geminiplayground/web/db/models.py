import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .orm_registry import mapper_registry as reg


@reg.mapped_as_dataclass
class MultimodalPartEntry:
    """
    Multimodal part model.
    """

    __tablename__ = "part"

    name: Mapped[str] = mapped_column(primary_key=True)
    content_type: Mapped[str] = mapped_column()

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name}, {self.name})>"
