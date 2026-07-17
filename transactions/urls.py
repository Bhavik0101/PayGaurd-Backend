
from django.urls import path,include

from .import views
from rest_framework.routers import DefaultRouter 
#because in the views I have used modelviewsets that is why I have to use router 
router=DefaultRouter()
router.register('transactions',views.TransactionView,basename='transaction')

urlpatterns = [
  
     path('',include(router.urls)),
    path('create-order/',views.RazorpayView.as_view()),
    path('webhook/',views.WebHookRazorPay.as_view())
 

]
