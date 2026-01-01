import csv
import os
from io import TextIOWrapper
from django.db.models import Avg
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

# =========================
# DISTRESS SCORING LOGIC
# =========================

DISTRESS_KEYWORDS = {
    "urgent": 2,
    "must sell": 3,
    "auction": 3,
    "distress": 2,
    "quick sale": 2,
    "price reduced": 1,
}


def keyword_distress_score(description: str) -> float:
    if not description:
        return 0.0

    description = description.lower()
    score = 0.0

    for keyword, weight in DISTRESS_KEYWORDS.items():
        if keyword in description:
            score += weight

    return score


def price_deviation_score(price: float, market_average: float) -> float:
    if not market_average or market_average <= 0:
        return 0.0

    deviation = (market_average - price) / market_average

    if deviation <= 0:
        return 0.0
    elif deviation >= 0.3:
        return 5.0
    elif deviation >= 0.2:
        return 4.0
    elif deviation >= 0.1:
        return 2.0
    else:
        return 1.0


def calculate_distress_score(price: float, description: str, market_average: float = 0) -> float:
    keyword_score = keyword_distress_score(description)
    price_score = price_deviation_score(price, market_average)
    return round(keyword_score + price_score, 2)


def get_market_average_price(location: str) -> float:
    """
    Calculate average property price for a given location.
    Uses lazy import to avoid circular dependency.
    """
    from .models import Property  # ✅ lazy import

    avg_price = (
        Property.objects
        .filter(location__iexact=location)
        .aggregate(avg=Avg("price"))
        .get("avg")
    )

    return float(avg_price) if avg_price else 0.0


# =========================
# CSV PROCESSING
# =========================

def process_csv(file):
    from .models import Property  # ✅ lazy import

    csv_file = TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(csv_file)

    created_count = 0

    for row in reader:
        try:
            price = float(row.get("price", 0))
        except ValueError:
            continue

        location = row.get("location", "").strip()
        description = row.get("description", "")

        market_average = get_market_average_price(location)

        distress_score = calculate_distress_score(
            price=price,
            description=description,
            market_average=market_average,
        )

        Property.objects.create(
            title=row.get("title", ""),
            description=description,
            location=location,
            price=price,
            distress_score=distress_score,
            source="csv",
        )

        created_count += 1

    return created_count


# =========================
# NOTIFICATIONS
# =========================

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def send_email_alert(to_email, subject, content):
    if not SENDGRID_API_KEY:
        return

    message = Mail(
        from_email="no-reply@propertyalert.com",
        to_emails=to_email,
        subject=subject,
        html_content=content,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"SendGrid error: {e}")


def send_sms_alert(to_number, content):
    if not TWILIO_SID or not TWILIO_AUTH_TOKEN:
        return

    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    try:
        client.messages.create(
            body=content,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number,
        )
    except Exception as e:
        print(f"Twilio error: {e}")


def notify_users(property_obj, threshold=5):
    """
    Notify users if property distress score exceeds threshold.
    """
    if property_obj.distress_score < threshold:
        return

    from .models import NotificationPreference  # ✅ lazy import

    users = NotificationPreference.objects.all()
    subject = f"Distress Property Alert: {property_obj.title}"
    content = f"""
    <p>A property is flagged as distressed:</p>
    <ul>
        <li>Title: {property_obj.title}</li>
        <li>Location: {property_obj.location}</li>
        <li>Price: {property_obj.price}</li>
        <li>Distress Score: {property_obj.distress_score}</li>
    </ul>
    """

    for pref in users:
        if pref.email_alert:
            send_email_alert(pref.user.email, subject, content)
        if pref.sms_alert and pref.phone_number:
            send_sms_alert(
                pref.phone_number,
                f"{subject}\nPrice: {property_obj.price}\nScore: {property_obj.distress_score}",
            )
