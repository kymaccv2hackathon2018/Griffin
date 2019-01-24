from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
import json
import logging
from .serializers import OrderSerializer, StockLevelSerializer
from .models import Product, StockLevel, Order
from time import time
from django.forms.models import model_to_dict
from .utils import start_order, get_stock
from django.conf import settings


# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# TODO Make root url an environment variable
ROOT_URL = (
    settings.ROOT_URL
)

OCC_PATH = settings.OCC_PATH


@api_view(["GET", "POST"])
def add_stock(request):
    if request.method == "POST":
        payload = request.data
        product = Product.objects.get(productId__exact=payload["productCode"])
        stock_level = {"productId": product.id, "amount": payload["amount"]}
        stock = StockLevel.objects.filter(productId__exact=product.id)[0]
        if stock:
            serializer = StockLevelSerializer(stock, data=stock_level)
        else:
            serializer = StockLevelSerializer(data=stock_level)
        if serializer.is_valid():
            logger.info(f"Setting stock level to:{stock_level['amount']}")
            serializer.save()
        else:
            logger.error("Error with the payload")
            logger.error(f"Payload: {payload}")

        return HttpResponse(json.dumps(stock_level), content_type="application/json")
    else:
        stock_level = StockLevel.objects.all()
        response = "/n".join([str(i) for i in stock_level])
        return HttpResponse(response, content_type="text")


class StockDetail(APIView):
    def get(self, request, p_id, format=None):
        stock = get_stock(p_id)
        serializer = StockLevelSerializer(stock)
        return Response(serializer.data)

    def post(self, request, p_id, format=None):
        stock = get_stock(p_id)
        payload = request.data
        stock.amount = payload["quantity"]
        stock.save()
        product = Product.objects.get(productId=p_id)
        orders = Order.objects.filter(placed=False, productCode=product.id)
        for order in orders:
            start_order(order, ROOT_URL, OCC_PATH)
        return HttpResponse(
            json.dumps(model_to_dict(stock)), content_type="application/json"
        )


@api_view(["POST", "GET"])
def kyma_order(request):

    payload = request.data
    product = Product.objects.get(productId__exact=payload["productCode"])
    print(product)
    order = {"productCode": product.id, "order_amount": payload["quantity"]}
    t_stamp = time()
    print(t_stamp)
    order["created_at"] = t_stamp
    if payload["quantity"] > get_stock(payload["productCode"]).amount:
        order["placed"] = False
    else:
        order["placed"] = True
    serializer = OrderSerializer(data=order)
    print(serializer.initial_data)
    if serializer.is_valid():
        print("Saving Order")
        serializer.save()
    else:
        print(serializer.errors)
        print("Bad order")
    if not order["placed"]:
        return HttpResponse("Product out of stock, order not placed")
    # start_order(serializer)
    order = Order.objects.get(created_at__exact=t_stamp)
    order_placed = start_order(order, ROOT_URL, OCC_PATH)
    return HttpResponse(order_placed, content_type="application/json")
