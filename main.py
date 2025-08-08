
from fastapi import FastAPI, Depends, HTTPException, Request, Form, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional
import uvicorn
from db import get_db, init_db, get_password_hash, verify_password, SessionLocal
from models import Item, Transaction, Alert, User, PurchaseOrder, PurchaseOrderItem
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
import random
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import time



MAIL_USERNAME = "donomyt@gmail.com"  
MAIL_PASSWORD = "zynj qgyp fkuf vozj"  
MAIL_FROM = MAIL_USERNAME
MAIL_PORT = 587
MAIL_SERVER = "smtp.gmail.com"
MAIL_FROM_NAME = "Clinic Inventory"

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


app = FastAPI(title="Clinic Inventory Management System", version="1.0.0")


SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


templates = Jinja2Templates(directory="templates")

def create_access_token(data: dict):
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


def generate_otp():
    return str(random.randint(100000, 999999))

@app.post("/api/signup")
async def signup(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    department: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    otp = generate_otp()
    user = User(
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        department=department,
        is_verified=False,
        otp=otp,
        otp_created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    
    subject = "Your Clinic Inventory OTP Verification Code"
    body = f"Hello {name},<br><br>Your OTP code is: <b>{otp}</b><br><br>Enter this code to verify your email."
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="html"
    )
    fm = FastMail(conf)
    try:
        background_tasks.add_task(fm.send_message, message)
        print(f"[INFO] OTP email scheduled for {email}")
    except Exception as e:
        print(f"[ERROR] Failed to send OTP email to {email}: {e}")

    return {"message": "OTP sent to your email. Please verify to activate your account.", "email": email}


@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please check your email for the OTP.")
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "department": user.department})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "department": user.department, "name": user.name}



@app.post("/api/verify-otp")
def verify_otp(email: str = Form(...), otp: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Account already verified."}
    if not user.otp or user.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if (datetime.utcnow() - user.otp_created_at).total_seconds() > 600:
        raise HTTPException(status_code=400, detail="OTP expired. Please sign up again.")
    user.is_verified = True
    user.otp = None
    user.otp_created_at = None
    db.commit()
    return {"message": "Account successfully created. Please log in."}


@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/test")
def test_route():
    return {"message": "Server is working!"}



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


def ensure_demo_nurse(db: Session):
    nurse_email = "dnvdevx@gmail.com"
    nurse = db.query(User).filter(User.email == nurse_email).first()
    if not nurse:
        nurse = User(
            name="Demo Nurse",
            email=nurse_email,
            password_hash=get_password_hash("password"),
            role="nurse",
            department=None,
            is_verified=True
        )
        db.add(nurse)
        db.commit()

def ensure_demo_alerts(db: Session):
    
    items = db.query(Item).all()
    created_any = False
    if not items:
        
        from datetime import date, timedelta
        demo1 = Item(
            name="Demo Paracetamol",
            category="medication",
            current_stock=3,
            min_threshold=10,
            unit="tablets",
            unit_price=2.0,
            supplier_name="Default Supplier",
            supplier_email="supplier@example.com",
            expiry_date=date.today() + timedelta(days=14),
            location="Main Store",
            department="Internal Medicine",
            brand_name="Dolo"
        )
        demo2 = Item(
            name="Demo Saline",
            category="supplies",
            current_stock=25,
            min_threshold=10,
            unit="bottles",
            unit_price=5.0,
            supplier_name="Default Supplier",
            supplier_email="supplier@example.com",
            expiry_date=date.today() + timedelta(days=10),
            location="Main Store",
            department="Emergency Department (ER/ED)",
            brand_name="Generic"
        )
        db.add_all([demo1, demo2])
        db.commit()
        db.refresh(demo1); db.refresh(demo2)
        check_and_create_alerts(demo1.id, db)
        check_and_create_alerts(demo2.id, db)
        created_any = True
    else:
        from datetime import date, timedelta
    
        low_item = db.query(Item).first()
        if low_item:
            low_item.min_threshold = max(low_item.min_threshold, 5)
            low_item.current_stock = min(low_item.current_stock, low_item.min_threshold - 1 if low_item.min_threshold > 0 else 0)
            if low_item.current_stock >= low_item.min_threshold:
                low_item.current_stock = max(0, low_item.min_threshold - 1)
            db.commit()
            check_and_create_alerts(low_item.id, db)
            created_any = True
        
        exp_item = db.query(Item).offset(1).first() or low_item
        if exp_item:
            exp_item.expiry_date = date.today() + timedelta(days=14)
            db.commit()
            check_and_create_alerts(exp_item.id, db)
            created_any = True
    return created_any

def simulate_stock_drop_after_delay(delay_seconds: int = 60):
    time.sleep(delay_seconds)
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.current_stock > Item.min_threshold).first()
        if not item:
            
            item = db.query(Item).first()
        if item:
            item.current_stock = max(0, (item.min_threshold or 1) - 1)
            item.last_updated = datetime.utcnow()
            db.commit()
            check_and_create_alerts(item.id, db)
    finally:
        db.close()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: Optional[str] = None, background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
   
    if not token:
        token = request.cookies.get("token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            user = db.query(User).filter(User.email == email).first()
        except Exception:
            user = None
    if not user:
        return RedirectResponse("/", status_code=302)
    
    ensure_demo_nurse(db)
    ensure_demo_alerts(db)
    
    if background_tasks is not None:
        background_tasks.add_task(simulate_stock_drop_after_delay, 60)
    
    departments = [
        "Emergency Department (ER/ED)", "Internal Medicine", "Surgery", "Pediatrics", "Obstetrics & Gynecology (OB/GYN)",
        "Orthopedics", "Cardiology", "Neurology", "Oncology", "Radiology", "Anesthesiology", "Pathology",
        "Dermatology", "Psychiatry", "Ophthalmology", "ENT"
    ]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "departments": departments
    })


@app.get("/api/items")
def get_all_items(db: Session = Depends(get_db)):
    """Get all inventory items"""
    items = db.query(Item).all()
    return items

@app.get("/api/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get specific item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/api/items")
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    current_stock: int = Form(...),
    min_threshold: int = Form(...),
    unit: str = Form(...),
    unit_price: float = Form(...),
    supplier_name: str = Form(...),
    supplier_email: Optional[str] = Form(None),
    expiry_date: str = Form(...),
    location: str = Form(...),
    brand_name: str = Form(None),
    department: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    rfid_tag: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add new inventory item"""
    
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    
    new_item = Item(
        name=name,
        category=category,
        current_stock=current_stock,
        min_threshold=min_threshold,
        unit=unit,
        unit_price=unit_price,
        supplier_name=supplier_name,
        supplier_email=supplier_email,
        expiry_date=expiry,
        location=location,
        brand_name=brand_name,
        department=department,
        barcode=barcode,
        rfid_tag=rfid_tag
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    
    check_and_create_alerts(new_item.id, db)
    
    return {"message": "Item added successfully", "item_id": new_item.id}

@app.get("/api/items/by-barcode/{code}")
def get_item_by_barcode(code: str, db: Session = Depends(get_db)):
    """Lookup an item by its barcode"""
    item = db.query(Item).filter(Item.barcode == code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/items/{item_id}/barcode")
def set_item_barcode(item_id: int, barcode: str = Form(...), db: Session = Depends(get_db)):
   
    
    existing = db.query(Item).filter(Item.barcode == barcode, Item.id != item_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Barcode already linked to another item")
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.barcode = barcode
    item.last_updated = datetime.utcnow()
    db.commit()
    return {"message": "Barcode linked", "item_id": item.id}

@app.get("/api/items/by-rfid/{tag}")
def get_item_by_rfid(tag: str, db: Session = Depends(get_db)):
    """Lookup an item by RFID tag"""
    item = db.query(Item).filter(Item.rfid_tag == tag).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/items/{item_id}/rfid")
def set_item_rfid(item_id: int, rfid_tag: str = Form(...), db: Session = Depends(get_db)):
    """Attach or update an RFID tag for an existing item"""
    existing = db.query(Item).filter(Item.rfid_tag == rfid_tag, Item.id != item_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="RFID already linked to another item")
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.rfid_tag = rfid_tag
    item.last_updated = datetime.utcnow()
    db.commit()
    return {"message": "RFID linked", "item_id": item.id}


@app.post("/api/purchase-orders/auto")
def create_purchase_orders(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Generate purchase orders for items below threshold, grouped by supplier, and email them."""
    
    suggestions = get_restock_suggestions(db)
    
    groups = {}
    for s in suggestions:
        key = (s["supplier"],)
        groups.setdefault(key, []).append(s)
    created_po_ids = []
    for (supplier_name,), items in groups.items():
        
        supplier_email = None
        for s in items:
            it = db.query(Item).filter(Item.id == s["item_id"]).first()
            if it and it.supplier_email:
                supplier_email = it.supplier_email
                break
        po = PurchaseOrder(
            supplier_name=supplier_name or "Unknown Supplier",
            supplier_email=supplier_email,
            status="draft",
            total_cost=0.0
        )
        db.add(po)
        db.commit()
        db.refresh(po)
        total = 0.0
        for s in items:
            poi = PurchaseOrderItem(
                purchase_order_id=po.id,
                item_id=s["item_id"],
                item_name=s["item_name"],
                quantity=s["suggested_order_quantity"],
                unit_price=db.query(Item).filter(Item.id == s["item_id"]).first().unit_price,
                subtotal=s["estimated_cost"]
            )
            total += poi.subtotal
            db.add(poi)
        po.total_cost = total
        db.commit()
        created_po_ids.append(po.id)
       
        if supplier_email:
            try:
                items_html = "".join([
                    f"<li>{s['item_name']}: {s['suggested_order_quantity']} units</li>" for s in items
                ])
                message = MessageSchema(
                    subject=f"Purchase Order #{po.id}",
                    recipients=[supplier_email],
                    body=f"<p>Hello {supplier_name},</p><p>Please supply the following items:</p><ul>{items_html}</ul><p>Total estimated cost: ${total:.2f}</p>",
                    subtype="html"
                )
                fm = FastMail(conf)
                background_tasks.add_task(fm.send_message, message)
                po.status = "sent"
                po.sent_at = datetime.utcnow()
                db.commit()
            except Exception as e:
                print(f"[ERROR] Failed to email PO {po.id}: {e}")
    return {"message": "Purchase orders generated", "purchase_order_ids": created_po_ids}

@app.put("/api/items/{item_id}/stock")
def update_stock(
    item_id: int,
    quantity_change: int,
    transaction_type: str,
    reason: str,
    staff_name: str,
    notes: str = "",
    db: Session = Depends(get_db)
):
    """Update item stock (add/remove inventory)"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    
    if transaction_type == "in":
        new_stock = item.current_stock + quantity_change
    elif transaction_type == "out":
        new_stock = item.current_stock - quantity_change
        if new_stock < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")
    else:  
        new_stock = quantity_change
    
    
    item.current_stock = new_stock
    item.last_updated = datetime.utcnow()
    
       
    transaction = Transaction(
        item_id=item_id,
        item_name=item.name,
        transaction_type=transaction_type,
        quantity=quantity_change,
        reason=reason,
        staff_name=staff_name,
        notes=notes
    )
    
    db.add(transaction)
    db.commit()
    
    
    check_and_create_alerts(item_id, db)
    
    return {"message": "Stock updated successfully", "new_stock": new_stock}

@app.get("/api/alerts")
def get_alerts(show_resolved: bool = False, db: Session = Depends(get_db)):
    """Get all alerts (unresolved by default)"""
    query = db.query(Alert)
    if not show_resolved:
        query = query.filter(Alert.is_resolved == False)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    return alerts

@app.get("/api/low-stock")
def get_low_stock_items(db: Session = Depends(get_db)):
    """Get items with stock below minimum threshold"""
    items = db.query(Item).filter(Item.current_stock <= Item.min_threshold).all()
    return items

@app.get("/api/expiring-soon")
def get_expiring_items(days_ahead: int = 30, db: Session = Depends(get_db)):
    """Get items expiring within specified days"""
    future_date = date.today() + timedelta(days=days_ahead)
    items = db.query(Item).filter(Item.expiry_date <= future_date).all()
    return items

@app.get("/api/restock-suggestions")
def get_restock_suggestions(db: Session = Depends(get_db)):
    """Get restocking suggestions based on usage patterns"""
    
    low_stock_items = db.query(Item).filter(Item.current_stock <= Item.min_threshold).all()
    
    suggestions = []
    for item in low_stock_items:
        
        recent_transactions = db.query(Transaction).filter(
            Transaction.item_id == item.id,
            Transaction.transaction_type == "out",
            Transaction.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        total_used = sum(t.quantity for t in recent_transactions)
        avg_daily_usage = total_used / 30 if recent_transactions else 1
        
       
        suggested_quantity = max(int(avg_daily_usage * 60), item.min_threshold * 2)
        
        suggestions.append({
            "item_id": item.id,
            "item_name": item.name,
            "current_stock": item.current_stock,
            "suggested_order_quantity": suggested_quantity,
            "supplier": item.supplier_name,
            "estimated_cost": suggested_quantity * item.unit_price,
            "avg_daily_usage": avg_daily_usage
        })
    
    return suggestions

def check_and_create_alerts(item_id: int, db: Session):
    """Check item and create alerts if needed"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return
    
    
    if item.current_stock <= item.min_threshold:
        existing_alert = db.query(Alert).filter(
            Alert.item_id == item_id,
            Alert.alert_type == "low_stock",
            Alert.is_resolved == False
        ).first()
        if not existing_alert:
            alert = Alert(
                item_id=item_id,
                item_name=item.name,
                alert_type="low_stock",
                message=f"{item.name} is low on stock ({item.current_stock} {item.unit} remaining)",
                priority="high" if item.current_stock == 0 else "medium"
            )
            db.add(alert)
           
            staff_emails = [u.email for u in db.query(User).filter(User.role != 'doctor', User.is_verified == True).all()]
            if staff_emails:
                subject = f"Low Stock Alert: {item.name}"
                body = f"<b>{item.name}</b> is low on stock: <b>{item.current_stock} {item.unit}</b> remaining. Please restock soon."
                message = MessageSchema(
                    subject=subject,
                    recipients=staff_emails,
                    body=body,
                    subtype="html"
                )
                try:
                    fm = FastMail(conf)
                    fm.send_message(message)
                except Exception as e:
                    print(f"[ERROR] Failed to send low stock alert email: {e}")
    
   
    days_to_expiry = (item.expiry_date - date.today()).days
    if days_to_expiry <= 120:
        existing_alert = db.query(Alert).filter(
            Alert.item_id == item_id,
            Alert.alert_type.in_(["expiring", "expired"]),
            Alert.is_resolved == False
        ).first()
        if not existing_alert:
            if days_to_expiry < 0:
                alert_type = "expired"
                message = f"{item.name} has expired ({abs(days_to_expiry)} days ago)"
                priority = "critical"
            else:
                alert_type = "expiring"
                message = f"{item.name} expires in {days_to_expiry} days"
                priority = "high" if days_to_expiry <= 30 else "medium"
            alert = Alert(
                item_id=item_id,
                item_name=item.name,
                alert_type=alert_type,
                message=message,
                priority=priority
            )
            db.add(alert)
            
            staff_emails = [u.email for u in db.query(User).filter(User.role != 'doctor', User.is_verified == True).all()]
            if staff_emails:
                subject = f"Expiry Alert: {item.name}"
                body = f"<b>{item.name}</b> expires in <b>{days_to_expiry}</b> days. Please take action."
                message = MessageSchema(
                    subject=subject,
                    recipients=staff_emails,
                    body=body,
                    subtype="html"
                )
                try:
                    fm = FastMail(conf)
                    fm.send_message(message)
                except Exception as e:
                    print(f"[ERROR] Failed to send expiry alert email: {e}")
    
    db.commit()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
