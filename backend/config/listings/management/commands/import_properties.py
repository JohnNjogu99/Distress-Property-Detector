import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from listings.models import Property

class Command(BaseCommand):
    help = "Import properties from a CSV file with validation and header mapping"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="demo_properties.csv",
            help="CSV filename inside listings/data/"
        )

    def handle(self, *args, **options):
        file_name = options["file"]
        data_path = Path(__file__).resolve().parent.parent.parent / "data" / file_name

        if not data_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {data_path}"))
            return

        total, imported, skipped = 0, 0, 0
        required_fields = ["title", "location", "price", "distress_score"]

        # Header mapping for messy CSVs
        header_map = {
            "price (kes)": "price",
            "distress score": "distress_score",
        }

        with open(data_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            # Normalize headers
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

            # Apply header mapping
            reader.fieldnames = [header_map.get(h, h) for h in reader.fieldnames]

            self.stdout.write(self.style.WARNING(f"Headers normalized: {reader.fieldnames}"))

            for row in reader:
                total += 1
                clean_row = {header_map.get(k.strip().lower(), k.strip().lower()): v.strip() for k, v in row.items()}

                # Check required fields
                missing = [field for field in required_fields if not clean_row.get(field)]
                if missing:
                    skipped += 1
                    self.stderr.write(self.style.ERROR(f"Row {total} skipped: missing {missing} → {row}"))
                    continue

                # Convert numeric fields safely
                try:
                    price = float(clean_row["price"].replace(",", ""))  # handle commas in numbers
                    distress_score = float(clean_row["distress_score"])
                except ValueError as ve:
                    skipped += 1
                    self.stderr.write(self.style.ERROR(f"Row {total} skipped: invalid numeric → {row} ({ve})"))
                    continue

                # Skip duplicates
                if Property.objects.filter(title=clean_row["title"], location=clean_row["location"]).exists():
                    skipped += 1
                    self.stdout.write(self.style.WARNING(f"Row {total} duplicate skipped: {clean_row['title']} in {clean_row['location']}"))
                    continue

                try:
                    Property.objects.create(
                        title=clean_row["title"],
                        location=clean_row["location"],
                        price=price,
                        distress_score=distress_score,
                    )
                    imported += 1
                except Exception as e:
                    skipped += 1
                    self.stderr.write(self.style.ERROR(f"Row {total} skipped: error saving → {row} ({e})"))

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {imported} added, {skipped} skipped, out of {total} rows."
        ))
