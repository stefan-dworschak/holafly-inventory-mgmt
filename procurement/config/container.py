from dataclasses import dataclass

from procurement.adapters.persistence.sqlalchemy.restock_request_adapter import (
    SQLAlchemyRestockRequestAdapter,
)
from procurement.domain.ports.repositories.restock_request_repository import (
    RestockRequestRepository,
)
from procurement.domain.services.restock_request_service import RestockRequestService


@dataclass
class Container:
    restock_request_repository: RestockRequestRepository
    restock_request_service: RestockRequestService


def create_prod_container() -> Container:
    restock_request_repository = SQLAlchemyRestockRequestAdapter()
    restock_request_service = RestockRequestService(restock_request_repository)
    return Container(
        restock_request_repository=restock_request_repository,
        restock_request_service=restock_request_service,
    )
