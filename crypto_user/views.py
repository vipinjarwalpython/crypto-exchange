from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import (
    UserCryptoWallet,
    UserProfile,
    KYCInformation,
    UserProfile,
    UserWallet,
    CoinTransaction,
    FundTransactions,
)
from django.shortcuts import render
from requests import Request, Session
import json


# Create your views here.


def crypto_user_signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        print(
            first_name,
            last_name,
            email,
            phone_number,
        )
        print(username)
        print(password1, password2)
        if password1 != password2:
            messages.error(request, "Both Password not match")
            return redirect("/signup/")

        user = User.objects.filter(username=username)
        print(user)
        if user:
            messages.error(request, "Username already exists")
            return redirect("/signup/")

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password1,
        )
        userprofile = UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
        )
        userprofile.save()

        userwallet = UserWallet.objects.create(user_profile=userprofile)
        userwallet.save()
        print(userwallet)
        return redirect("/user/login/")

    return render(request, "register.html")


def crypto_user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username).exists()
        print(user)

        if user is None:
            messages.error(request, "User not found")
            return redirect("/user/login/")

        user = authenticate(request, username=username, password=password)
        print(user)

        if user is None:
            messages.error(request, "Password Incorrect")

        else:
            login(request, user)
            return redirect("/dashboard/")
    return render(request, "login.html")


def user_kyc(request):
    if request.method == "POST":
        user = request.user
        document_type = request.POST.get("document_type")
        document_number = request.POST.get("document_number")
        document_image = request.FILES.get("document_image")
        address = request.POST.get("address")
        date_of_birth = request.POST.get("date_of_birth")

        print(
            user, document_type, document_number, document_image, address, date_of_birth
        )
        user_pro = UserProfile.objects.get(user=user)
        print(user_pro)
        kyc_info = KYCInformation.objects.create(
            user_profile=user_pro,
            document_type=document_type,
            document_number=document_number,
            date_of_birth=date_of_birth,
            address=address,
            document_image=document_image,
        )
        kyc_info.save()
        if kyc_info is not None:
            user = UserProfile.objects.get(user=user)
            user.is_kyc = True
            user.save()
            return redirect("/dashboard/")
    return render(request, "kyc.html")


def crypto_user_logout(request):
    logout(request)
    return redirect("/dashboard/")


url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
parameters = {"start": "1", "limit": "100"}
headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": "d4377d6d-c56f-4f09-8d48-bac9bd7a53cc",
}

session = Session()
session.headers.update(headers)


def user_dashboard(request):
    try:
        # Delete objects with coin_quantity equal to 0.0
        quntityzero = UserCryptoWallet.objects.filter(coin_quantity=0.0)
        quntityzero.delete()

        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        api_data = data["data"]
        filtered_api_data = []

        # Search Engine
        if request.method == "POST":
            coin = request.POST.get("coin").lower()
            if coin is not None:
                # print("==========================", coin)

                for i in api_data:
                    if coin == i.get("slug"):
                        print(i)
                        filtered_api_data.append(i)

                if filtered_api_data:
                    return render(
                        request, "user_dashboard.html", {"api_data": filtered_api_data}
                    )

            else:
                return render(
                    request,
                    "error.html",
                    {"api_data": api_data, "error_message": "No results found"},
                )

        user_coins = UserCryptoWallet.objects.filter(
            userwallet=request.user.userprofile.userwallet
        )

        coin_price = []
        pro_loss = []
        for i in user_coins:
            dict_price = {"coin": i, "current_price": "", "profit_loss": ""}
            # print(dict_price)
            coin_price.append(dict_price)

        for api_coin in api_data:
            symbol = api_coin.get("symbol")
            current_price = api_coin.get("quote").get("USD").get("price")

            for coin_info in coin_price:
                symbol2 = coin_info["coin"].coin_name

                if symbol == symbol2:
                    coin_info["current_price"] = current_price
                    quantity = coin_info["coin"].coin_quantity
                    purchase_price = coin_info["coin"].coin_price
                    current_value = quantity * current_price
                    profit_loss = current_value - (quantity * purchase_price)
                    pro_loss.append(profit_loss)
                    coin_info["profit_loss"] = profit_loss
        total_proandloss = sum(pro_loss)
        # print(coin_price)

        return render(
            request,
            "user_dashboard.html",
            {
                "api_data": api_data,
                "user_coins": coin_price,
                "total_proandloss": total_proandloss,
            },
        )
    except Exception as e:
        # Handle exceptions appropriately, e.g., log the error
        print(e)
        return render(request, "error.html")


def order_execute(request):
    if request.method == "POST":
        coin_name = request.POST.get("coin_name")
        coin_quantity = float(request.POST.get("coin_quantity"))
        coin_price = float(request.POST.get("coin_price"))
        total_amount = float(request.POST.get("total_ammount"))
        userwallet = request.user.userprofile.userwallet
        coin_status = request.POST.get("coin_status")

        user_coins = UserCryptoWallet.objects.filter(
            userwallet=request.user.userprofile.userwallet
        )

        for i in user_coins:
            if i.coin_name == coin_name:
                if coin_status == "buy":
                    if userwallet.balance >= i.total_amount:
                        i.coin_quantity = i.coin_quantity + coin_quantity
                        i.total_amount = i.total_amount + total_amount
                        i.coin_status = coin_status

                        userwallet.balance = userwallet.balance - (
                            coin_price * coin_quantity
                        )
                        userwallet.save()
                    else:
                        messages.error(
                            request,
                            f"Insufficient balance. Please deposit {i.total_amount} {i.coin_name} to your wallet",
                        )
                        return redirect("/user/dashboard/")

                if coin_status == "sell":
                    if i.coin_quantity >= coin_quantity and coin_quantity >= 0:
                        i.coin_quantity = i.coin_quantity - coin_quantity
                        i.total_amount = i.total_amount - total_amount
                        i.coin_status = coin_status

                        userwallet.balance = userwallet.balance + (
                            coin_price * coin_quantity
                        )
                        userwallet.save()
                    else:
                        messages.error(
                            request,
                            f"Sell only coin name - {coin_name} quantity - {i.coin_quantity}",
                        )
                        return redirect("/user/dashboard/")
                i.save()

                CoinTransaction.objects.create(
                    userwallet=i.userwallet,
                    coin_name=i.coin_name,
                    coin_quantity=i.coin_quantity,
                    coin_price=i.coin_price,
                    total_amount=i.total_amount,
                    coin_status=i.coin_status,
                )

                return redirect("/user/dashboard/")

        print(userwallet.balance)
        print(total_amount)
        if coin_status == "buy":
            if userwallet.balance >= total_amount:
                userwallet.balance = userwallet.balance - (coin_price * coin_quantity)
                userwallet.save()
            else:
                messages.error(
                    request,
                    f"Insufficient balance. Please deposit {total_amount}  -  {coin_name} to your wallet",
                )
                return redirect("/user/dashboard/")

        else:
            if coin_quantity > 0.0:
                userwallet.balance = userwallet.balance + (coin_price * coin_quantity)
                userwallet.save()
            else:
                messages.error(
                    request,
                    f"Sell only this - {coin_name} - {coin_quantity}",
                )
                return redirect("/user/dashboard/")

        UserCryptoWallet.objects.create(
            userwallet=userwallet,
            coin_name=coin_name,
            coin_quantity=coin_quantity,
            coin_price=coin_price,
            total_amount=total_amount,
            coin_status=coin_status,
        )

        CoinTransaction.objects.create(
            userwallet=userwallet,
            coin_name=coin_name,
            coin_quantity=coin_quantity,
            coin_price=coin_price,
            total_amount=total_amount,
            coin_status=coin_status,
        )

        return redirect("/user/dashboard/")


def coin_activity(request):
    user_coin_data = CoinTransaction.objects.filter(
        userwallet=request.user.userprofile.userwallet
    )
    print(user_coin_data)

    funds_activity = FundTransactions.objects.filter(
        userwallet=request.user.userprofile.userwallet
    )
    return render(
        request,
        "activity.html",
        {"user_coin_data": user_coin_data, "funds_activity": funds_activity},
    )


def funds_activity(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        status = request.POST.get("status")
        userwallet = request.user.userprofile.userwallet

        if status == "deposit":
            if float(amount) > 0:
                userwallet.balance = userwallet.balance + float(amount)
                userwallet.save()
            else:
                messages.error(
                    request,
                    f"Please enter a valid amount to deposit",
                )
                return redirect("/user/activity/")
        else:
            if float(amount) < userwallet.balance:
                userwallet.balance = userwallet.balance - float(amount)
                userwallet.save()
            else:
                messages.error(
                    request,
                    f"Please enter a valid amount to withdraw",
                )
                return redirect("/user/activity/")
        FundTransactions.objects.create(
            userwallet=userwallet, amount=float(amount), status=status
        )

        return redirect("/user/activity/")
