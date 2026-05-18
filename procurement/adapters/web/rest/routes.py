from typing import List

from fastapi import APIRouter, Depends

from procurement.adapters.web.rest.auth import require_token
from procurement.adapters.web.rest.schemas import RestockRequestSchema
from procurement.config.container import create_prod_container

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_token)])
container = create_prod_container()


@router.get('/restock-requests', response_model=List[RestockRequestSchema])
def list_restock_requests() -> List[RestockRequestSchema]:
    requests = container.restock_request_service.list_restock_requests()
    return [RestockRequestSchema.model_validate(req) for req in requests]
