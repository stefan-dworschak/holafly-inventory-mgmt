from typing import List

from pydantic import validate_call

from procurement.domain.models.restock_request import RestockRequest
from procurement.domain.ports.repositories.restock_request_repository import (
    RestockRequestRepository,
)


class RestockRequestService:
    def __init__(self, restock_request_repository: RestockRequestRepository):
        self.restock_request_repository = restock_request_repository

    @validate_call(validate_return=True)
    def list_restock_requests(self) -> List[RestockRequest]:
        return self.restock_request_repository.list_restock_requests()

    @validate_call(validate_return=True)
    def register_low_stock_alert(self, sku: str, stock_left: int) -> RestockRequest:
        return self.restock_request_repository.add_restock_request(
            sku=sku, stock_left=stock_left
        )
