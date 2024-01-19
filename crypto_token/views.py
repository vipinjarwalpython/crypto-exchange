from django.shortcuts import render
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
parameters = {"start": "1", "limit": "100"}
headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": "d4377d6d-c56f-4f09-8d48-bac9bd7a53cc",
}

session = Session()
session.headers.update(headers)


def dashboard_view(request):
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        api_data = data["data"]
        filtered_api_data = []

        # Search Engine
        if request.method == "POST":
            coin = request.POST.get("coin").lower()
            print("==========================", coin)
            for i in api_data:
                if coin == i.get("slug"):
                    print(i)
                    filtered_api_data.append(i)

            if filtered_api_data:
                return render(request, "index.html", {"api_data": filtered_api_data})
            else:
                return render(
                    request,
                    "index.html",
                    {"api_data": api_data, "error_message": "No results found"},
                )

        return render(request, "index.html", {"api_data": api_data})
    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error
        print(e)
        return render(request, "error.html")  # You can create a custom error template


def calculator(request):
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        api_data = data["data"]
        filtered_api_data = []

        if request.method == "GET":
            ammount = int(request.GET.get("ammount"))
            coin = request.GET.get("coin").lower()
            print(ammount)

            for i in api_data:
                if coin == i.get("slug"):
                    if ammount:
                        calculate_ammount = ammount * i.get("quote").get("USD").get(
                            "price"
                        )
                        print(calculate_ammount)
                        return render(request, "index.html")

        return render(request, "index.html")

    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error
        print(e)
        return render(request, "error.html")
