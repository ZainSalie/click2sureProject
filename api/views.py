import csv
import random
import mimetypes
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import *
import requests
from django.db import IntegrityError
from itertools import chain
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class RegisterViewSet(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionView(GenericAPIView):
    queryset = Transactions.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            queryset = Transactions.objects.filter(user_id_id=pk).values()

        else:
            queryset = Transactions.objects.all().values()[:10]

        return Response(queryset, status=status.HTTP_200_OK)

    def post(self, request):
        auth = ('user1', 'click2sure')
        auth_user = request.data['user_id']
        # auth_user = User.objects.filter(username=user).values()[0]["id"]
        # request.data['user_id'] = auth_user
        serializer = TransactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # print(pk)

        if request.data['source'] == 'CREDIT':
            url = f'http://localhost:5000/transaction/credit/{auth_user}'
            credit_user = Credit.objects.get(user_id_id=auth_user)
            max_credit = credit_user.max_credit
            if request.data['type'] == 'BUY':
                amount_owed = float(credit_user.amount_owed) + float(request.data['amount'])

                if amount_owed > max_credit:
                    return Response(data={'msg': 'Not enough Credit'}, status=status.HTTP_402_PAYMENT_REQUIRED)
            else:
                amount_owed = float(credit_user.amount_owed) - float(request.data['amount'])

            balance = float(max_credit) - float(amount_owed)
            data = {
                'max_credit': max_credit,
                'amount_owed': amount_owed,
                'balance': balance
            }
            res = requests.put(url, data=data, auth=auth)

            if res.status_code != 202:
                raise IntegrityError

        elif request.data['source'] == 'SAVINGS':
            url = f'http://localhost:5000/transaction/savings/{auth_user}'
            savings_user = Savings.objects.get(user_id_id=auth_user)
            balance = savings_user.balance
            if request.data['type'] == 'BUY':
                balance = float(balance) - float(request.data['amount'])
                if balance < 50:
                    return Response(data={'msg': 'Balance too low'}, status=status.HTTP_402_PAYMENT_REQUIRED)
            else:
                balance = float(balance) + float(request.data['amount'])

            data = {
                'balance': balance
            }
            res = requests.put(url, data=data, auth=auth)
            if res.status_code != 202:
                raise IntegrityError

        serializer.validated_data['user_id_id'] = auth_user
        serializer.save()
        return Response(data=request.data, status=status.HTTP_201_CREATED)


class CreditViewset(GenericAPIView):
    queryset = Credit.objects.all()
    serializer_class = CreditSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):

        queryset = Credit.objects.all()
        serializer = CreditSerializer(queryset, many=True, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data['user_id'])
        serializer = CreditSerializer(data=request.data)
        credit_user = User.objects.filter(username=request.data['user_id']).values()[0]["id"]
        # return Response(credit_user.values()[0]["id"])
        if serializer.is_valid():
            serializer.validated_data['user_id_id'] = credit_user
            serializer.validated_data['balance'] = serializer.validated_data['max_credit'] - \
                                                       serializer.validated_data['amount_owed']
            serializer.save()
            return Response(data=request.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavingsViewset(GenericAPIView):
    queryset = Savings.objects.all()
    serializer_class = SavingsSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk is not None:
            queryset = Savings.objects.filter(user_id_id=pk).values()

        else:
            queryset = Savings.objects.all().values()

        return Response(queryset, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SavingsSerializer(data=request.data)
        user_id = User.objects.filter(username=request.data['user_id']).values()[0]["id"]
        if serializer.is_valid():
            serializer.validated_data['user_id_id'] = user_id
            serializer.save()
            return Response(data=request.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FullView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(username=request.user)
        savings = Savings.objects.filter(user_id_id=user.id).values()
        creds = Credit.objects.filter(user_id_id=user.id).values()
        transactions = Transactions.objects.filter(user_id_id=user.id).values()[:10]
        res = chain(savings, creds, transactions)
        return Response(data=res, status=status.HTTP_200_OK)


class CreditDetailsViewset(GenericAPIView):
    queryset = Credit.objects.all()
    serializer_class = CreditSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        queryset = Credit.objects.get(pk=pk)
        serializer = CreditSerializer(queryset, context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        credit_user = Credit.objects.get(pk=pk)

        serializer = CreditSerializer(credit_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        cred = Credit.objects.get(pk=pk)
        cred.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SavingsDetailsViewset(GenericAPIView):
    queryset = Savings.objects.all()
    serializer_class = SavingsSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        queryset = Savings.objects.get(pk=pk)
        serializer = SavingsSerializer(queryset, context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        savings_user = Savings.objects.get(pk=pk)
        serializer = SavingsSerializer(savings_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors)

    def delete(self, pk):
        cred = Savings.objects.get(pk=pk)
        cred.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CsvView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = User.objects.all().values()
        fields = ['UID', 'Savings', 'Credit', 'Transactions']
        all_info = []
        for user in users:
            uid = user['id']
            data = [uid]
            try:
                data.append(Savings.objects.filter(pk=uid).values())
            except:
                pass

            try:
                data.append(Credit.objects.filter(pk=uid).values())
            except:
                pass
            try:
                data.append(Transactions.objects.filter(user_id_id=uid).values())
            except:
                pass
            all_info.append(data)

        with open('./all.csv', 'w') as f:

            # using csv.writer method from CSV package
            write = csv.writer(f)

            write.writerow(fields)
            write.writerows(all_info)
        # filename =
        filepath = "./all.csv"
        path = open(filepath, 'r')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filepath
        return response


def fillDB(request):
    try:
        User.objects.create_superuser('user1', 'user1@test.com', 'click2sure')
    except:
        pass
    auth = ('user1', 'click2sure')
    url = "http://localhost:5000/transaction/"
    user_list = ['user1']
    for i in range(2, 11):
        user_list.append(f'user{i}')
        data = {
            'username': f'user{i}',
            'email': f'user{i}@test.com',
            'password': 'click2sure'
        }
        if User.objects.filter(username=f'user{i}').exists():
            pass
        else:
            res = requests.post(url+"register/", data=data, auth=auth)

    for i in range(10):
        data = {
            'user_id': user_list[i],
            'amount_owed': 0,
            'max_credit': 20000,
            'balance': 20000
        }
        res = requests.post(url + "credit/", data=data, auth=auth)
        data = {
            'user_id': user_list[i],
            'balance': 20000
        }
        res = requests.post(url + "savings/", data=data, auth=auth)

        for _ in range(20):
            uid = User.objects.filter(username=user_list[i]).values()[0]['id']
            data = {
                'user_id': uid,
                'amount': random.randint(1, 20000),
                'type': random.choice(['BUY', 'SELL']),
                'source': random.choice(['CREDIT', 'SAVINGS'])
            }
            serializer = TransactionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                print('not valid')
    return HttpResponse(content="Success")
