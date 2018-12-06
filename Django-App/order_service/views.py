from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, Http404
import requests
import json
import logging
from .serializers import OrderSerializer, StockLevelSerializer
from .models import Product, StockLevel, Order
from time import time
from django.forms.models import model_to_dict
from django.utils.timezone import utc


# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# TODO Make root url an environment variable
root_url = (
    "https://electronics.cqz1m-softwarea1-d6-public.model-t.cc.commerce.ondemand.com"
)

occ_path = "rest/v2/electronics/users"


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
            start_order(order)
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
    order_placed = start_order(order)
    return HttpResponse(order_placed, content_type="application/json")


def start_order(serialized_order):
    token = get_bearer_token()
    cart = get_cart(token)
    product = serialized_order.productCode

    quantity = serialized_order.order_amount

    add_to_cart(token, product.productId, quantity, cart)
    address = add_address(token)
    assign_address_to_cart(token, cart, address)
    set_delivery_mode(token, cart)
    add_payment_to_cart(token, cart)
    order = place_order(token, cart)
    stock_level = product.stocklevel
    stock_level.amount -= quantity
    stock_level.save()
    serialized_order.placed = True
    serialized_order.save()
    return order


def get_bearer_token():
    url = f"{root_url}/authorizationserver/oauth/token"
    data = {
        "client_id": "eic",
        "client_secret": "secret",
        "grant_type": "password",
        "username": "devin.mens@sap.com",
        "password": "welcome",
    }
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    print(url)
    req = requests.post(url=url, data=data, headers=header)
    j = json.loads(req.text)
    print(j)
    return j["access_token"]


def get_cart(token):
    headers = {"authorization": f"Bearer {token}"}
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts"
    req = requests.post(url=url, headers=headers)
    res = json.loads(req.text)
    print(res["code"])
    return res["code"]


def add_to_cart(token, code, quantity, cart):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/entries"
    headers = {"authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"product": {"code": code}, "quantity": quantity}
    req = requests.post(url=url, headers=headers, data=json.dumps(data))
    print(req.text)


def add_address(token):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/addresses"
    headers = {"authorization": f"Bearer {token}", "Content-Type": "application/json"}
    address = {
        "country": {"isocode": "US"},
        "defaultAddress": True,
        "titleCode": "mr",
        "firstName": "Devin",
        "id": "8796165636119",
        "lastName": "Mens",
        "line1": "1 fifth avenue",
        "line2": "",
        "phone": "",
        "postalCode": "10003",
        "region": {"isocode": "US-NY"},
        "town": "New York City",
    }
    req = requests.post(url=url, headers=headers, data=json.dumps(address))
    res = json.loads(req.text)
    print(res)
    return res["id"]


def assign_address_to_cart(token, cart, addressId):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/addresses/delivery"
    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"addressId": addressId}
    req = requests.put(url=url, headers=headers, data=data)
    print(req.status_code)


def set_delivery_mode(token, cart):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/deliverymode"
    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"deliveryModeId": "standard-net"}
    req = requests.put(url=url, headers=headers, data=data)
    print(req.status_code)


def add_payment_to_cart(token, cart):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/paymentdetails"
    headers = {"authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payment = {
        "accountHolderName": "Devin Mens",
        "cardNumber": "4586316481054884",
        "cardType": {"code": "visa"},
        "expiryMonth": "11",
        "expiryYear": "2022",
        "defaultPayment": True,
        "billingAddress": {
            "country": {"isocode": "US"},
            "defaultAddress": True,
            "titleCode": "mr",
            "firstName": "Devin",
            "id": "8796165636119",
            "lastName": "Mens",
            "line1": "1 fifth avenue",
            "line2": "",
            "phone": "",
            "postalCode": "10003",
            "region": {"isocode": "US-NY"},
            "town": "New York City",
        },
    }
    req = requests.post(url=url, headers=headers, data=json.dumps(payment))
    print(req.status_code)


def place_order(token, cart):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/orders"
    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"cartId": cart, "securityCode": "658"}

    req = requests.post(url=url, headers=headers, data=data)
    print(req.status_code)
    res = req.text
    return res


def get_stock(p_id):
    try:
        print(p_id)
        product = Product.objects.get(productId=p_id)
        print(product)
        return StockLevel.objects.get(productId=product.id)
    except Exception:
        raise Http404
