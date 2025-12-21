import csv
from io import TextIOWrapper
from .models import Property

DISTRESS_KEYWORDS = ['urgent', 'auction', 'must sell']

def process_csv(file):
    """
    Process uploaded CSV and create Property entries.
    Expected columns: title, description, location, price
    """
    csv_file = TextIOWrapper(file, encoding='utf-8')
    reader = csv.DictReader(csv_file)

    created_count = 0
    for row in reader:
        # Basic validation
        if 'title' not in row or 'location' not in row or 'price' not in row:
            continue

        # Convert price
        try:
            price = float(row['price'])
        except ValueError:
            continue

        # Distress scoring (simple example)
        distress_score = 0
        description_lower = row.get('description', '').lower()
        for kw in DISTRESS_KEYWORDS:
            if kw in description_lower:
                distress_score += 1

        Property.objects.create(
            title=row['title'],
            description=row.get('description', ''),
            location=row['location'],
            price=price,
            distress_score=distress_score,
            source='csv'
        )
        created_count += 1

    return created_count
def process_csv(file):
    reader = csv.DictReader(file.read().decode('utf-8').splitlines())
    return list(reader)

def process_csv_file(file):
    return process_csv(file)