from django.urls import path
from order_service import views

app_name = "order_service"


urlpatterns = [
    path("rest/v1/orders", views.kyma_order, name="place_order"),
    path("rest/v1/stock", views.add_stock, name="add_stock"),
    path("rest/v1/stock/<str:p_id>/", views.StockDetail.as_view(), name="stock_detail"),
]
