from typing import List, Protocol

from procurement.domain.models.restock_request import RestockRequest


class RestockRequestRepository(Protocol):
    def add_restock_request(self, sku: str, stock_left: int) -> RestockRequest:
        """Persist a new restock request triggered by a low stock alert."""
        ...

    def list_restock_requests(self) -> List[RestockRequest]:
        """Return all known restock requests, most recent first."""
        ...
