from pydantic import BaseModel, Field


class TextPart(BaseModel):
    text: str = Field(..., description="Text content.")


class FilePartData(BaseModel):
    file_uri: str = Field(description="URI of the file.", alias="fileUri")
    mime_type: str = Field(description="MIME type of the file.", alias="mimeType")

    class Config:
        populate_by_name = True


class FilePart(BaseModel):
    file_data: FilePartData = Field(
        alias="fileData", description="Information about the file."
    )

    class Config:
        populate_by_name = True
