import razorpay
import json
from django.conf import settings
from rest_framework.response import Response
from decimal import Decimal
from rest_framework import viewsets
from .models import Transaction
from rest_framework.views import APIView
from .serializers import TransactionSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from rest_framework.exceptions import ValidationError
from users.models import Wallet
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from fraud.models import FraudCheck
from fraud.services import calculate_fraud_score
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class TransactionView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    # Frontend kiske basis par filter kar sakta hai? (e.g., ?status=Fraud)
    filterset_fields = ['status', 'payment_id']
    
    # Frontend kiske basis par sort kar sakta hai? (e.g., ?ordering=-amount)
    ordering_fields = ['amount']
    def get_queryset(self):
        if self.request.user.is_staff == True:
            return Transaction.objects.all()
        else:
            return Transaction.objects.filter(merchant=self.request.user)

    def perform_create(self, serializer):
        amount = serializer.validated_data['amount']
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=self.request.user)
            if wallet.balance < amount:
                raise ValidationError("Insufficient Balance")
            else:
                wallet.balance -= amount
                wallet.save()
            serializer.save(merchant=self.request.user)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class RazorpayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        razorpay_amount = int(amount) * 100 
        
        data = {
            "amount": razorpay_amount,
            "currency": "INR",
            "payment_capture": "1",
            "notes": {
                "user_id": request.user.id
            }
        }
        
        razorpay_order = client.order.create(data=data)
        return Response(razorpay_order)

@method_decorator(csrf_exempt, name='dispatch')
class WebHookRazorPay(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
        webhook_body = request.body.decode('utf-8')

        try:
            client.utility.verify_webhook_signature(
                webhook_body, 
                webhook_signature, 
                settings.RAZORPAY_KEY_SECRET
            )
            
            data = json.loads(webhook_body)
            event = data.get('event')

            if event == "payment.captured":
                payment_payload = data['payload']['payment']['entity']
                user_id = payment_payload['notes']['user_id']
                payment_id = payment_payload['id']
                
                amount_in_rs = Decimal(payment_payload['amount']) / Decimal(100)
                
                if Transaction.objects.filter(payment_id=payment_id).exists():
                    return Response({"status":"Already Processed"}, status=200)
                
                with transaction.atomic():
                    wallet = Wallet.objects.select_for_update().get(user_id=user_id)    
                    txn = Transaction.objects.create(
                        merchant_id=user_id,
                        amount=amount_in_rs,
                        status="Pending",
                        payment_id=payment_id
                    ) 
                    score, reasons = calculate_fraud_score(txn)
                    FraudCheck.objects.create(
                        transaction=txn,
                        score=score,
                        reasons=reasons
                    )       
                    if score >= 75:
                        txn.status = "Fraud"
                        txn.save()
                    elif score >= 20:
                        txn.status = "Flagged"
                        txn.save()
                    else:
                        wallet.balance += amount_in_rs
                        wallet.save()
                        txn.status = "Success"
                        txn.save()                                                  
            
            return Response({"status": "Success"}, status=200)

        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Invalid signature."}, status=400)