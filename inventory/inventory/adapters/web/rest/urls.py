
from django.urls import path, re_path

from inventory.adapters.web.rest.views import ProductDetail, ProductList 

urlpatterns = [
    re_path("^$", ProductList.as_view(), name="product_list"),
    path("<uuid:product_id>", ProductDetail.as_view(), name="product_detail"), 
]
