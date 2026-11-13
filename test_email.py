import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")

def send_test_email():
    if not SENDER_EMAIL or not SENDER_PASSWORD or not NOTIFICATION_EMAIL:
        print("❌ Error: Missing email configuration in your .env file!")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = "🚀 Test Alert: QA Job Agent Notification System"

        body = "Hello! This is a test notification from your QA Job Agent tool. Email alerts are working!"
        msg.attach(MIMEText(body, 'plain'))

        print(f"Connecting via SSL to {SMTP_SERVER}:465...")
        # Using SMTP_SSL on port 465 instead of STARTTLS on 587
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.set_debuglevel(1)  # Prints exact server responses if an error occurs
            print("Logging in...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD.strip())
            print("Sending email...")
            server.send_message(msg)

        print("\n✅ Success! Test email sent successfully. Check your inbox.")
    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication Error: Google rejected the email or App Password. Make sure you generated a 16-character App Password (not your regular Gmail password).")
    except Exception as e:
        print(f"\n❌ Failed to send email. Error: {e}")

if __name__ == "__main__":
    send_test_email()