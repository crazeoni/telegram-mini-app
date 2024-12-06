from sqlalchemy import create_engine

DATABASE_URI = "postgresql://scream_user:ozioma235@telegram-mini-app-7nu1.onrender.com:5433/scream_db"
engine = create_engine(DATABASE_URI)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
