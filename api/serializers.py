from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer
from .models import Credit, Transactions, Savings
from django.contrib.auth.models import User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class CreditSerializer(ModelSerializer):
    user_id = UserSerializer(read_only=True)
    class Meta:
        model = Credit
        fields = '__all__'

    def create(self, validated_data):
        return Credit.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user_id_id = validated_data.get('user_id', instance.user_id)
        instance.max_credit = validated_data.get('max_credit', instance.max_credit)
        instance.amount_owed = validated_data.get('amount_owed', instance.amount_owed)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.save()
        return instance


class TransactionSerializer(ModelSerializer):
    user_transaction = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Transactions
        fields = '__all__'

    def create(self, validated_data):
        return Transactions.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user_id_id = validated_data.get('user_id', instance.user_id_id)
        instance.source = validated_data.get('source', instance.source)
        instance.type = validated_data.get('type', instance.type)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance


class SavingsSerializer(ModelSerializer):
    user_id = UserSerializer(read_only=True)
    class Meta:
        model = Savings
        fields = '__all__'

    def create(self, validated_data):
        return Savings.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user_id_id = validated_data.get('user_id', instance.user_id_id)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.save()
        return instance


class FullViewSerializer(ModelSerializer):
    user_credit = CreditSerializer()
    user_savings = SavingsSerializer()
    user_transactions = TransactionSerializer(many=True)

    class Meta:
        model = User
        fields = '__all__'
