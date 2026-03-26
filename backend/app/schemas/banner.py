from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BannerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    subtitle: str | None = None
    cta_text: str | None = None
    cta_link: str | None = None
    image_url: str | None = None
