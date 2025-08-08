from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  
    department = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)
    otp = Column(String, nullable=True)
    otp_created_at = Column(DateTime, nullable=True)

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String) 
    department = Column(String, nullable=True) 
    brand_name = Column(String, nullable=True) 
    current_stock = Column(Integer, default=0)
    min_threshold = Column(Integer, default=10)
    max_capacity = Column(Integer, default=1000)
    unit = Column(String) 
    unit_price = Column(Float, default=0.0)
    supplier_name = Column(String)
    supplier_email = Column(String, nullable=True)
    expiry_date = Column(Date)
    location = Column(String) 
    barcode = Column(String, unique=True, nullable=True)
    rfid_tag = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String)
    supplier_email = Column(String, nullable=True)
    status = Column(String, default="draft")
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, index=True)
    item_id = Column(Integer, index=True)
    item_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, index=True)
    item_name = Column(String)
    transaction_type = Column(String) 
    quantity = Column(Integer)
    reason = Column(String) 
    staff_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, index=True)
    item_name = Column(String)
    alert_type = Column(String)  
    message = Column(String)
    priority = Column(String)  
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)