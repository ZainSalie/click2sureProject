from django.urls import path
from .views import TransactionView, CreditViewset, SavingsViewset, FullView, CreditDetailsViewset, SavingsDetailsViewset, RegisterViewSet, CsvView, fillDB

urlpatterns = [
    path('', TransactionView.as_view(), name='transactions'),
    path('<int:pk>', TransactionView.as_view()),
    path('credit/', CreditViewset.as_view(), name='credit'),
    path('credit/<int:pk>', CreditDetailsViewset.as_view()),
    path('savings/', SavingsViewset.as_view(), name='savings'),
    path('savings/<int:pk>', SavingsDetailsViewset.as_view()),
    path('view/', FullView.as_view(), name='full_view'),
    path('register/', RegisterViewSet.as_view()),
    path('csv/', CsvView.as_view()),
    path('autofill/', fillDB)
]
