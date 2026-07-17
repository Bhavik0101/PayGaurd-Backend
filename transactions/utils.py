import threading
from django.core.mail import send_mail
import time

class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    # Yeh run() function background (alag thread) mein chalega
    def run(self):
        print(f"👨‍🍳 Chef started preparing email for: {self.recipient_list}")
        
        # Simulate network delay (jaise asali Gmail 3 second leta hai)
        time.sleep(3) 
        
        send_mail(
            subject=self.subject,
            message=self.message,
            # Niche wali line ko change kar
            from_email='bhavikagrawal01012006@gmail.com', 
            recipient_list=self.recipient_list,
            fail_silently=False,
        )
        print("✅ Chef finished! Email delivered successfully.")

# Yeh function hamara view call karega
def send_payment_receipt_async(user_email, amount):
    subject = "Payment Successful - Payguard"
    message = f"Hello,\n\nYour payment of ₹{amount} was successfully captured by Payguard.\n\nThank you!"
    
    # Naya thread (Chef) banaya aur usko start kar diya
    EmailThread(subject, message, [user_email]).start()