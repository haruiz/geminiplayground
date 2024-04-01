import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .orm_registry import mapper_registry as reg


@reg.mapped_as_dataclass
class FileEntry:
    """
    Project model.
    """

    __tablename__ = "file"

    name: Mapped[str] = mapped_column(primary_key=True)
    mime_type: Mapped[str] = mapped_column()
    uri: Mapped[str] = mapped_column()
    part_id: Mapped[str] = mapped_column(ForeignKey("part.name"))
    part: Mapped["MultimodalPartEntry"] = relationship(
        "MultimodalPartEntry", back_populates="files", default=None
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name}, {self.name})>"


@reg.mapped_as_dataclass
class MultimodalPartEntry:
    """
    Multimodal part model.
    """

    __tablename__ = "part"

    name: Mapped[str] = mapped_column(primary_key=True)
    content_type: Mapped[str] = mapped_column()
    files: Mapped[typing.List["FileEntry"]] = relationship(
        "FileEntry",
        back_populates="part",
        default_factory=list,
        cascade="all, delete-orphan",
    )

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name}, {self.name})>"
