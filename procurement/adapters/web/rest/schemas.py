from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RestockRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sku: str
    stock_left: int
    created_at: datetime
