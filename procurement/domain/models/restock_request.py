from dataclasses import asdict, dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RestockRequest:
    id: UUID
    sku: str
    stock_left: int
    created_at: datetime

    def as_dict(self) -> dict:
        return asdict(self)
