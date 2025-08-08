from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, User
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

SQLALCHEMY_DATABASE_URL = "sqlite:///./clinic_inventory.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    create_tables()
    # Lightweight migration: ensure new columns exist
    with engine.connect() as conn:
        # Add rfid_tag and supplier_email to items if missing
        res = conn.execute(text("PRAGMA table_info(items)")).mappings().all()
        existing_cols = {row['name'] for row in res}
        if 'rfid_tag' not in existing_cols:
            try:
                conn.execute(text("ALTER TABLE items ADD COLUMN rfid_tag VARCHAR"))
            except Exception:
                pass
        if 'supplier_email' not in existing_cols:
            try:
                conn.execute(text("ALTER TABLE items ADD COLUMN supplier_email VARCHAR"))
            except Exception:
                pass
        # Create purchase_orders and purchase_order_items tables if missing
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY,
                supplier_name VARCHAR,
                supplier_email VARCHAR,
                status VARCHAR,
                total_cost FLOAT,
                created_at DATETIME,
                sent_at DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS purchase_order_items (
                id INTEGER PRIMARY KEY,
                purchase_order_id INTEGER,
                item_id INTEGER,
                item_name VARCHAR,
                quantity INTEGER,
                unit_price FLOAT,
                subtotal FLOAT
            )
        """))
    print("Database initialized successfully!")