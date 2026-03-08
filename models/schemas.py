from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class LinkCreateRequest(BaseModel):
    original_url: HttpUrl
    length: int
    alias: Optional[str] = None


class DeadLink(BaseModel):
    alias: str
    expires_at: datetime
