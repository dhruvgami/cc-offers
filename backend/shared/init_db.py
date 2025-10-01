"""Database initialization script"""
from .database import init_db, get_db_context, DatabaseClient
from .models import Hotel, DiscountCode


def seed_initial_data():
    """Seed database with initial data"""
    with get_db_context() as db:
        db_client = DatabaseClient(db)

        # Create sample hotels
        hotels_data = [
            {
                "name": "Marriott Times Square",
                "chain": "Marriott",
                "city": "New York",
                "state": "NY",
                "address": "1535 Broadway, New York, NY 10036"
            },
            {
                "name": "Hilton Midtown",
                "chain": "Hilton",
                "city": "New York",
                "state": "NY",
                "address": "1335 Avenue of the Americas, New York, NY 10019"
            },
            {
                "name": "Holiday Inn Times Square",
                "chain": "IHG",
                "city": "New York",
                "state": "NY",
                "address": "585 8th Ave, New York, NY 10018"
            }
        ]

        print("Creating sample hotels...")
        for hotel_data in hotels_data:
            existing = db_client.get_hotel_by_name_city(hotel_data["name"], hotel_data["city"])
            if not existing:
                hotel = db_client.create_hotel(**hotel_data)
                print(f"  ✅ Created: {hotel.name}")
            else:
                print(f"  ⏭️  Skipped (exists): {hotel_data['name']}")

        # Create discount codes
        discount_codes_data = [
            {"code": "ZA9", "type": "aarp", "hotel_chain": "Marriott", "requirements": "AARP membership"},
            {"code": "ZAA", "type": "aaa", "hotel_chain": "Marriott", "requirements": "AAA membership"},
            {"code": "ZA9", "type": "senior", "hotel_chain": "Marriott", "requirements": "Age 62+"},

            {"code": "AARP", "type": "aarp", "hotel_chain": "Hilton", "requirements": "AARP membership"},
            {"code": "AAA", "type": "aaa", "hotel_chain": "Hilton", "requirements": "AAA membership"},
            {"code": "SEN", "type": "senior", "hotel_chain": "Hilton", "requirements": "Age 60+"},

            {"code": "AARP", "type": "aarp", "hotel_chain": "IHG", "requirements": "AARP membership"},
            {"code": "AAA", "type": "aaa", "hotel_chain": "IHG", "requirements": "AAA membership"},
            {"code": "SEN", "type": "senior", "hotel_chain": "IHG", "requirements": "Age 62+"},
        ]

        print("\nCreating discount codes...")
        for code_data in discount_codes_data:
            # Check if code already exists
            existing_codes = db_client.get_discount_codes(
                code_data["hotel_chain"],
                code_data["type"]
            )
            if not any(c.code == code_data["code"] for c in existing_codes):
                code = db_client.create_discount_code(**code_data)
                print(f"  ✅ Created: {code.hotel_chain} - {code.type} ({code.code})")
            else:
                print(f"  ⏭️  Skipped (exists): {code_data['hotel_chain']} - {code_data['type']}")

        print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nSeeding initial data...")
    seed_initial_data()
    print("\n🎉 Database setup complete!")
