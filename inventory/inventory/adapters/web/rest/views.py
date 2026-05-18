from uuid import UUID

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from inventory.config.container import create_prod_container
from inventory.domain.exceptions import (
    NotEnoughStockException,
    ProductNotFoundException,
    MultipleProductsFoundException,
    UpdateFailedException
)
from inventory.adapters.web.rest.serializers import (
    ProductSerializer,
    ProductUpdateSerializer,
)


class ProductList(APIView):
    """
    List all products, or create a new product.
    """

    container = create_prod_container()

    def get(self, request: Request) -> Response:
        products = self.container.inventory_service.list_stock_levels()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = self.container.inventory_service.add_product_to_stock(**serializer.data)
            return Response(product.as_dict(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(APIView):
    """
    Retrieve, update or delete a product instance.
    """

    container = create_prod_container()

    def get(self, request: Request, product_id: UUID) -> Response:
        product = self.container.inventory_service.get_stock_product(product_id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request: Request, product_id: UUID) -> Response:
        product = self.container.inventory_service.get_stock_product(product_id=product_id)
        serializer = ProductUpdateSerializer(product, data=request.data)
        if serializer.is_valid():
            try:
                updated_product = self.container.inventory_service.update_stock_for_product(
                    product_id=product_id,
                    quantity=request.data["quantity"],
                )
            except (
                NotEnoughStockException,
                ProductNotFoundException,
                MultipleProductsFoundException,
                UpdateFailedException
                ) as error:
                return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(updated_product.as_dict())
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id: UUID) -> Response:
        deleted = self.container.inventory_service.delete_product_from_stock(product_id=product_id)
        if not deleted:
            return Response({"error": f"Product with ID {product_id} could not be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

