import logging

from typing import List
from uuid import UUID

from procurement.adapters.persistence.sqlalchemy.db import SessionLocal
from procurement.adapters.persistence.sqlalchemy.models import RestockRequestORM
from procurement.domain.models.restock_request import RestockRequest
from procurement.domain.ports.repositories.restock_request_repository import (
    RestockRequestRepository,
)


class SQLAlchemyRestockRequestAdapter(RestockRequestRepository):
    @staticmethod
    def _to_domain(row: RestockRequestORM) -> RestockRequest:
        return RestockRequest(
            id=UUID(row.id),
            sku=row.sku,
            stock_left=row.stock_left,
            created_at=row.created_at,
        )

    def add_restock_request(self, sku: str, stock_left: int) -> RestockRequest:
        logging.info("Adding Restock Request")
        with SessionLocal() as session:
            row = RestockRequestORM(sku=sku, stock_left=stock_left)
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def list_restock_requests(self) -> List[RestockRequest]:
        with SessionLocal() as session:
            rows = (
                session.query(RestockRequestORM)
                .order_by(RestockRequestORM.created_at.desc())
                .all()
            )
            return [self._to_domain(row) for row in rows]
