# fraud/services.py
from django.utils import timezone
from datetime import timedelta
from transactions.models import Transaction
from django.db.models import Avg

def check_velocity(merchant, window_minutes=10, max_transactions=5):
    """Returns True if merchant has made too many transactions recently."""
    window_start = timezone.now() - timedelta(minutes=window_minutes)
    recent_count = Transaction.objects.filter(
        merchant=merchant,
        created_at__gte=window_start
    ).count()
    return recent_count > max_transactions


def check_amount_anomaly(merchant, current_amount, multiplier=5):
    """Returns True if current amount is way above the merchant's historical average."""
    avg_amount = Transaction.objects.filter(
        merchant=merchant,
        status='Success'
    ).aggregate(avg=Avg('amount'))['avg']

    if avg_amount is None:
        return False  # no history yet — can't judge anomaly, handled by new-account rule instead

    return current_amount > (avg_amount * multiplier)


# def check_new_account_high_value(merchant, current_amount, account_age_hours=48, high_value_threshold=10000):
#     """Returns True if account is new AND transaction is large."""
#     account_age = timezone.now() - merchant.date_joined
#     is_new = account_age < timedelta(hours=account_age_hours)
#     is_high_value = current_amount > high_value_threshold
#     return is_new and is_high_value


def calculate_fraud_score(transaction):
    merchant = transaction.merchant
    amount = transaction.amount
    score = 0
    reasons = []

    if check_velocity(merchant):
        score += 30
        reasons.append("High transaction velocity")

    if check_amount_anomaly(merchant, amount):
        score += 25
        reasons.append("Amount significantly above average")

    # if check_new_account_high_value(merchant, amount):
    #     score += 20
    #     reasons.append("New account with high-value transaction")

    return score, reasons