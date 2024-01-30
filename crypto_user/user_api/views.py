from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from crypto_user.models import *
from crypto_user.user_api.serializer import *
from requests import Request, Session
import json


class UserSignupView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()  # Create a mutable copy of the QueryDict
            # print(data)

            # Check if 'password1' and 'password2' are in the data
            if "password1" not in data or "password2" not in data:
                return Response(
                    {"error": "Both 'password1' and 'password2' are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if 'password1' is equal to 'password2'
            if data["password1"] != data["password2"]:
                return Response(
                    {"error": "Passwords do not match."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Include 'password' in the data
            data["password"] = data["password1"]

            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save(password=make_password(data.get("password")))
                phone_number = data.get("phone_number")

                user_profile = UserProfile.objects.create(
                    user=user, phone_number=phone_number
                )
                print(user_profile)

                UserWallet.objects.create(user_profile=user_profile)

                user = UserProfile.objects.get(user=user)

                user_profile = UserProfileSerializer(user)
                context = {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "message": f"Welcome {user}",
                    "User_serializer": user_profile.data,
                }

                return Response(context)

            # Return serializer errors if not valid
            return Response(
                {
                    "error": "Serializer is not valid",
                    "serializer_errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as E:
            return Response({"error": str(E)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            # print(data)

            user = User.objects.filter(username=data["username"])
            print(user)

            if not user.exists():
                context = {
                    "success": False,
                    "message": "Username not found",
                    "status": status.HTTP_406_NOT_ACCEPTABLE,
                }
                return Response(context)

            user = authenticate(
                request, username=data["username"], password=data["password"]
            )
            # print(user)
            if user is None:
                context = {
                    "success": False,
                    "message": "Password Incorrect",
                    "status": status.HTTP_406_NOT_ACCEPTABLE,
                }
            else:
                login(request, user)
                refresh_token = RefreshToken.for_user(user)
                token = {
                    "refresh_token": str(refresh_token),
                    "access_token": str(refresh_token.access_token),
                }
                context = {
                    "success": True,
                    "message": f"Welcome {user}, you are logged in",
                    "status": status.HTTP_200_OK,
                    "token": token,
                }
                return Response(context)
        except Exception as E:
            return Response({"error": str(E)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserLogoutView(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)
        context = {
            "success": True,
            "message": "Buyer Logout Successfully",
            "status": status.HTTP_200_OK,
        }

        return Response(context)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserKycView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            print(data)
            user = request.user
            print(user)

            user_profile = UserProfile.objects.get(user=user)
            print(user_profile)

            kyc_info = KYCInformation.objects.create(
                user_profile=user_profile,
                document_type=data["document_type"],
                document_number=data["document_number"],
                date_of_birth=data["date_of_birth"],
                address=data["address"],
                document_image=data["document_image"],
            )

            if kyc_info is not None:
                user = UserProfile.objects.get(user=user)
                user.is_kyc = True
                user.save()
                user_kyc = KYCInformation.objects.get(user_profile=user_profile)
                kyc_info = UserKYCSerializer(user_kyc).data
                context = {
                    "success": True,
                    "message": "User KYC Successfully Uploaded",
                    "status": status.HTTP_200_OK,
                    "Kyc Info": kyc_info,
                }

                return Response(context)

        except Exception as E:
            return Response({"error": str(E)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserDashboardView(APIView):
    def post(self, request, *args, **kwargs):
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        parameters = {"start": "1", "limit": "100"}
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": "d4377d6d-c56f-4f09-8d48-bac9bd7a53cc",
        }
        session = Session()
        session.headers.update(headers)
        try:
            # Delete objects with coin_quantity equal to 0.0
            # quntityzero = UserCryptoWallet.objects.filter(coin_quantity=0.0)
            # quntityzero.delete()

            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            api_data = data["data"]
            filtered_api_data = []

            data = request.data
            user = request.user
            coin = data.get("coin")

            if coin is not None:
                for i in api_data:
                    if coin.lower() == i.get("slug"):
                        filtered_api_data.append(i)
                        print(filtered_api_data)

                if filtered_api_data:
                    serializer = CoinDetailsSerializer(
                        data={
                            "success": True,
                            "status": status.HTTP_200_OK,
                            "coin_info": filtered_api_data,
                        }
                    )
            else:
                serializer = CoinDetailsSerializer(
                    data={
                        "success": True,
                        "status": status.HTTP_200_OK,
                        "coin_info": api_data,
                    }
                )

            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)

        except Exception as E:
            return Response({"error": str(E)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserCoinView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user_coins = UserCryptoWallet.objects.filter(
                userwallet=request.user.userprofile.userwallet
            )

            print(user_coins)

            serializer = UserDashboardSerializer(user_coins, many=True)

            if serializer:
                serialized_data = serializer.data
                context = {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "coin_info": serialized_data,
                }
                return Response(context)
            else:
                context = {
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "error": serializer.errors,
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

        except Exception as E:
            return Response({"error": str(E)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
            parameters = {"start": "1", "limit": "100"}
            headers = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": "d4377d6d-c56f-4f09-8d48-bac9bd7a53cc",
            }

            session = Session()
            session.headers.update(headers)

            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            api_data = data["data"]

            user_coins = UserCryptoWallet.objects.filter(
                userwallet=request.user.userprofile.userwallet,
            )

            # coin_price = []
            pro_loss = []
            for api_coin in api_data:
                symbol = api_coin.get("symbol")
                current_price = api_coin.get("quote").get("USD").get("price")

                for coin_info in user_coins:
                    symbol2 = coin_info.coin_name

                    if symbol == symbol2:
                        # coin_info["current_price"] = current_price
                        quantity = coin_info.coin_quantity
                        purchase_price = coin_info.coin_price
                        current_value = quantity * current_price
                        profit_loss = current_value - (quantity * purchase_price)
                        pro_loss.append(profit_loss)
                        # coin_info["profit_loss"] = profit_loss
                        UpdateCoinDetails.objects.create(
                            userwallet=request.user.userprofile.userwallet,
                            user_crypto_wallet=coin_info,
                            current_price=current_price,
                            profitandloss=profit_loss,
                        )
            total_proandloss = sum(pro_loss)

            coinsdata = UpdateCoinDetails.objects.filter(
                userwallet=request.user.userprofile.userwallet
            )
            serializer = UserCoinsSerializer(coinsdata, many=True)

            context = {
                "success": True,
                "status": status.HTTP_200_OK,
                "coin_info": serializer.data,
                "profit_and_loss": total_proandloss,
            }
            return Response(context)

        except Exception as E:
            return Response({"error": str(E)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class OrderExecuteViews(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        userwallet = request.user.userprofile.userwallet

        user_coins = UserCryptoWallet.objects.filter(
            userwallet=user.userprofile.userwallet
        )

        print(user_coins)

        for i in user_coins:
            if i.coin_name == data.get("coin_name"):
                if data.get("coin_status") == "buy":
                    if userwallet.balance >= float(data.get("total_amount")):
                        i.coin_quantity = i.coin_quantity + float(
                            data.get("coin_quantity")
                        )
                        i.total_amount = i.total_amount + float(
                            data.get("total_amount")
                        )
                        i.coin_status = data.get("coin_status")

                        userwallet.balance = userwallet.balance - (
                            float(data.get("coin_price"))
                            * float(data.get("coin_quantity"))
                        )
                        userwallet.save()
                        i.save()

                        CoinTransaction.objects.create(
                            userwallet=i.userwallet,
                            coin_name=data.get("coin_name"),
                            coin_quantity=float(data.get("coin_quantity")),
                            coin_price=float(data.get("coin_price")),
                            total_amount=float(data.get("total_amount")),
                            coin_status=data.get("coin_status"),
                        )

                        serializer = UserDashboardSerializer(i)
                        context = {
                            "success": True,
                            "status": status.HTTP_200_OK,
                            "coin_info": serializer.data,
                        }
                        return Response(context)

                    else:
                        context = {
                            "success": False,
                            "status": status.HTTP_400_BAD_REQUEST,
                        }
                        return Response(context)

                if data.get("coin_status") == "sell":
                    if (
                        i.coin_quantity >= float(data.get("coin_quantity"))
                        and float(data.get("coin_quantity")) >= 0
                    ):
                        i.coin_quantity = i.coin_quantity - float(
                            data.get("coin_quantity")
                        )
                        print("================================")

                        i.total_amount = i.total_amount - float(
                            data.get("total_amount")
                        )
                        i.coin_status = data.get("coin_status")

                        userwallet.balance = userwallet.balance + (
                            float(data.get("coin_price"))
                            * float(data.get("coin_quantity"))
                        )
                        userwallet.save()
                        i.save()

                        CoinTransaction.objects.create(
                            userwallet=i.userwallet,
                            coin_name=data.get("coin_name"),
                            coin_quantity=float(data.get("coin_quantity")),
                            coin_price=float(data.get("coin_price")),
                            total_amount=float(data.get("total_amount")),
                            coin_status=data.get("coin_status"),
                        )

                        serializer = UserDashboardSerializer(i)
                        context = {
                            "success": True,
                            "status": status.HTTP_200_OK,
                            "coin_info": serializer.data,
                        }
                        return Response(context)

                    else:
                        context = {
                            "success": False,
                            "status": status.HTTP_400_BAD_REQUEST,
                        }
                        return Response(context)

        if data.get("coin_status") == "buy":
            if userwallet.balance >= float(data.get("total_amount")):
                userwallet.balance = userwallet.balance - (
                    float(data.get("coin_price")) * float(data.get("coin_quantity"))
                )
                userwallet.save()

                serializer = UserDashboardSerializer(i)

            else:
                context = {
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                return Response(context)

        else:
            if float(data.get("coin_quantity")) > 0.0:
                userwallet.balance = userwallet.balance + (
                    float(data.get("coin_price")) * float(data.get("coin_quantity"))
                )
                userwallet.save()

                serializer = UserDashboardSerializer(i)

            else:
                context = {
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                return Response(context)

        UserCryptoWallet.objects.create(
            userwallet=userwallet,
            coin_name=data.get("coin_name"),
            coin_quantity=data.get("coin_quantity"),
            coin_price=data.get("coin_price"),
            total_amount=data.get("total_amount"),
            coin_status=data.get("coin_status"),
        )

        CoinTransaction.objects.create(
            userwallet=userwallet,
            coin_name=data.get("coin_name"),
            coin_quantity=data.get("coin_quantity"),
            coin_price=data.get("coin_price"),
            total_amount=data.get("total_amount"),
            coin_status=data.get("coin_status"),
        )

        context = {
            "success": True,
            "status": status.HTTP_200_OK,
            "coin_info": serializer.data,
        }
        return Response(context)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserCoinsActivityViews(APIView):
    def get(self, request, *args, **kwargs):
        user_coin_data = CoinTransaction.objects.filter(
            userwallet=request.user.userprofile.userwallet
        )

        serializer = UserCoinActivitySerializer(user_coin_data, many=True)

        context = {
            "success": True,
            "status": status.HTTP_200_OK,
            "coin_info": serializer.data,
        }
        return Response(context)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserFundsActivityViews(APIView):
    def get(self, request, *args, **kwargs):
        user_fund_data = FundTransactions.objects.filter(
            userwallet=request.user.userprofile.userwallet
        )

        serializer = UserFundActivitySerializer(user_fund_data, many=True)

        context = {
            "success": True,
            "status": status.HTTP_200_OK,
            "funds_info": serializer.data,
        }
        return Response(context)

    def post(self, request, *args, **kwargs):
        data = request.data
        userwallet = request.user.userprofile.userwallet

        print(data)

        if data.get("status") == "deposit":
            if float(data.get("amount")) > 0:
                userwallet.balance = userwallet.balance + float(data.get("amount"))
                userwallet.save()

                FundTransactions.objects.create(
                    userwallet=userwallet,
                    amount=float(data.get("amount")),
                    status=data.get("status"),
                )

                context = {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "ammount": float(data.get("amount")),
                    "msg": "Successfully Deposit ",
                    "wallet balance": userwallet.balance,
                }
                return Response(context)
            else:
                context = {
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                return Response(context)
        else:
            if float(data.get("amount")) < userwallet.balance:
                userwallet.balance = userwallet.balance - float(data.get("amount"))
                userwallet.save()

                FundTransactions.objects.create(
                    userwallet=userwallet,
                    amount=float(data.get("amount")),
                    status=data.get("status"),
                )

                context = {
                    "success": True,
                    "status": status.HTTP_200_OK,
                    "ammount": float(data.get("amount")),
                    "msg": "Successfully Withdraw ",
                    "wallet balance": userwallet.balance,
                }
                return Response(context)
            else:
                context = {
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                return Response(context)
