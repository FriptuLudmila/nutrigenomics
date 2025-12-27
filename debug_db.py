"""Quick diagnostic for database issues"""
from app.database import init_db, get_db
from app.models import Session
from datetime import datetime

print("Testing database connection...")
if init_db():
    print("[OK] Database connected")

    # Try to create a test session
    print("\nTesting session save...")
    db = get_db()
    test_session = Session.create_new(
        filepath="/test/path.txt",
        filename="test.txt",
        file_size=1000
    )

    print(f"Session ID: {test_session.session_id}")
    print(f"Session dict: {test_session.to_dict()}")

    try:
        from app.models import save_session
        result = save_session(db, test_session)
        print(f"\nSave result: {result}")

        if result:
            print("[OK] Session saved successfully!")

            # Try to retrieve it
            from app.models import get_session
            retrieved = get_session(db, test_session.session_id)
            if retrieved:
                print(f"[OK] Session retrieved: {retrieved.session_id}")
            else:
                print("[ERROR] Could not retrieve session")
        else:
            print("[ERROR] Save returned False")

    except Exception as e:
        print(f"[ERROR] Exception during save: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[ERROR] Database connection failed")
