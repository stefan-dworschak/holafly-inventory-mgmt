from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.adapters.web.rest.serializers import (
    ProductSerializer,
    ProductUpdateSerializer,
)
from inventory.config.container import create_prod_container
from inventory.domain.exceptions import (
    DuplicateSkuException,
    InvalidProductDataException,
    MultipleProductsFoundException,
    NotEnoughStockException,
    ProductNotFoundException,
    UpdateFailedException,
)


class ProductList(APIView):
    """
    List all products, or create a new product.
    """

    container = create_prod_container()
    serializer_class = ProductSerializer

    @extend_schema(responses=ProductSerializer(many=True))
    def get(self, request: Request) -> Response:
        products = self.container.inventory_service.list_stock_levels()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(request=ProductSerializer, responses={201: ProductSerializer})
    def post(self, request: Request) -> Response:
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = self.container.inventory_service.add_product_to_stock(
                **serializer.data
            )
        except DuplicateSkuException as error:
            return Response({"error": str(error)}, status=status.HTTP_409_CONFLICT)
        return Response(product.as_dict(), status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    """
    Retrieve, update or delete a product instance.
    """

    container = create_prod_container()
    serializer_class = ProductSerializer

    @extend_schema(responses=ProductSerializer)
    def get(self, request: Request, product_id: UUID) -> Response:
        try:
            product = self.container.inventory_service.get_stock_product(product_id=product_id)
        except ProductNotFoundException as error:
            return Response({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @extend_schema(request=ProductUpdateSerializer, responses=ProductSerializer)
    def patch(self, request: Request, product_id: UUID) -> Response:
        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_product = self.container.inventory_service.update_stock_for_product(
                product_id=product_id,
                deduct_quantity=serializer.validated_data["deduct_quantity"],
            )
        except ProductNotFoundException as error:
            return Response({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)
        except NotEnoughStockException as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except (
            MultipleProductsFoundException,
            UpdateFailedException,
            InvalidProductDataException,
        ) as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(updated_product.as_dict())

    @extend_schema(responses={204: None})
    def delete(self, request, product_id: UUID) -> Response:
        try:
            deleted = self.container.inventory_service.delete_product_from_stock(
                product_id=product_id
            )
        except ProductNotFoundException as error:
            return Response({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)
        if not deleted:
            return Response(
                {"error": f"Product with ID {product_id} could not be deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
