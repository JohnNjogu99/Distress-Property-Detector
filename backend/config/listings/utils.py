import csv
from io import TextIOWrapper
from .models import Property
from django.db.models import Avg

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
    """
    avg_price = (
        Property.objects
        .filter(location__iexact=location)
        .aggregate(avg=Avg('price'))
        .get('avg')
    )

    return float(avg_price) if avg_price else 0.0

def process_csv(file):
    csv_file = TextIOWrapper(file, encoding='utf-8')
    reader = csv.DictReader(csv_file)

    created_count = 0

    for row in reader:
        try:
            price = float(row['price'])
        except (KeyError, ValueError):
            continue

        location = row.get('location', '').strip()
        description = row.get('description', '')

        market_average = get_market_average_price(location)

        distress_score = calculate_distress_score(
            price=price,
            description=description,
            market_average=market_average
        )

        Property.objects.create(
            title=row.get('title', ''),
            description=description,
            location=location,
            price=price,
            distress_score=distress_score,
            source='csv'
        )

        created_count += 1

    return created_count

