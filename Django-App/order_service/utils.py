import json

import requests
from django.http import Http404

from order_service.models import Product, StockLevel


def start_order(serialized_order, root_url, occ_path):
    token = get_bearer_token(root_url)
    cart = get_cart(token, root_url, occ_path)
    product = serialized_order.productCode

    quantity = serialized_order.order_amount

    add_to_cart(token, product.productId, quantity, cart, root_url, occ_path)
    address = add_address(token, root_url, occ_path)
    assign_address_to_cart(token, cart, address, root_url, occ_path)
    set_delivery_mode(token, cart, root_url, occ_path)
    add_payment_to_cart(token, cart, root_url, occ_path)
    order = place_order(token, cart)
    stock_level = product.stocklevel
    stock_level.amount -= quantity
    stock_level.save()
    serialized_order.placed = True
    serialized_order.save()
    return order


def get_bearer_token(root_url):
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


def get_cart(token, root_url, occ_path):
    headers = {"authorization": f"Bearer {token}"}
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts"
    req = requests.post(url=url, headers=headers)
    res = json.loads(req.text)
    print(res["code"])
    return res["code"]


def add_to_cart(token, code, quantity, cart, root_url, occ_path):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/entries"
    headers = {"authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"product": {"code": code}, "quantity": quantity}
    req = requests.post(url=url, headers=headers, data=json.dumps(data))
    print(req.text)


def add_address(token, root_url, occ_path):
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


def assign_address_to_cart(token, cart, addressId, root_url, occ_path):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/addresses/delivery"
    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"addressId": addressId}
    req = requests.put(url=url, headers=headers, data=data)
    print(req.status_code)


def set_delivery_mode(token, cart, root_url, occ_path):
    url = f"{root_url}/{occ_path}/devin.mens@sap.com/carts/{cart}/deliverymode"
    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"deliveryModeId": "standard-net"}
    req = requests.put(url=url, headers=headers, data=data)
    print(req.status_code)


def add_payment_to_cart(token, cart, root_url, occ_path):
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


def place_order(token, cart, root_url, occ_path):
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
