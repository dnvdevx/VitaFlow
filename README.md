# 🏥 VitaFlow - Clinic Inventory Management System

A comprehensive, modern inventory management solution designed specifically for healthcare facilities. Built with FastAPI, SQLAlchemy, and a beautiful responsive UI, VitaFlow streamlines inventory tracking, automates reordering, and ensures critical medical supplies are always available.

![VitaFlow Logo](https://img.shields.io/badge/VitaFlow-Clinic%20Inventory-blue?style=for-the-badge&logo=medical)

## 🚀 Features

### 📊 **Core Inventory Management**
- **Real-time Stock Tracking** - Monitor current stock levels across all departments
- **Multi-Department Support** - Organized inventory by medical departments (ER, Cardiology, Pediatrics, etc.)
- **Brand Management** - Track multiple brands for the same medication
- **Location Tracking** - Know exactly where items are stored
- **Expiry Date Monitoring** - Automatic alerts for expiring medications

### 🔔 **Smart Alert System**
- **Low Stock Alerts** - Automatic notifications when items fall below threshold
- **Expiry Warnings** - Proactive alerts for items nearing expiration
- **Email Notifications** - Instant email alerts to relevant staff
- **Priority-based Alerts** - Critical, high, medium priority classifications

### 📱 **Modern Technology Integration**
- **Barcode Scanning** - Quick item lookup and stock updates
- **RFID Tag Support** - Advanced tracking capabilities
- **Mobile-Responsive UI** - Works seamlessly on all devices
- **Real-time Updates** - Live dashboard with instant data refresh

### 🛒 **Automated Procurement**
- **Smart Reordering** - AI-powered restock suggestions based on usage patterns
- **Purchase Order Generation** - Automatic PO creation grouped by supplier
- **Email Integration** - Direct supplier communication
- **Cost Tracking** - Monitor inventory costs and budgets

### 👥 **User Management & Security**
- **Role-based Access** - Different permissions for doctors, nurses, administrators
- **Email Verification** - Secure OTP-based account activation
- **JWT Authentication** - Secure API access
- **Department-specific Views** - Users see relevant inventory for their department

### 📈 **Analytics & Reporting**
- **Transaction History** - Complete audit trail of all stock movements
- **Usage Analytics** - Track consumption patterns
- **Cost Analysis** - Monitor inventory expenses
- **Department Performance** - Compare usage across departments

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database (easily upgradable to PostgreSQL/MySQL)
- **JWT** - Secure authentication
- **Passlib** - Password hashing and verification

### Frontend
- **HTML5/CSS3** - Modern, responsive design
- **JavaScript (ES6+)** - Dynamic client-side functionality
- **Font Awesome** - Professional icons
- **Google Fonts** - Beautiful typography

### Email & Notifications
- **FastAPI-Mail** - Email integration for alerts and notifications
- **SMTP (Gmail)** - Reliable email delivery

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Modern web browser
- Email account for notifications (Gmail recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Clinic_Inventory
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy passlib python-jose[cryptography] python-multipart fastapi-mail jinja2
```

### 4. Configure Email Settings
Edit `main.py` and update the email configuration:
```python
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "your-app-password"  # Use Gmail App Password
MAIL_FROM = "your-email@gmail.com"
```

### 5. Initialize Database
```bash
python main.py
```

### 6. Seed Sample Data (Optional)
```bash
python seed_important_products.py
```

### 7. Run the Application
```bash
python main.py
```

### 8. Access the Application
Open your web browser and navigate to:
```
http://localhost:8000
```

The application will be available at `http://localhost:8000`

## 📖 Usage Guide

### 🔐 Authentication
1. **Sign Up**: Create a new account with your email
2. **Email Verification**: Check your email for OTP code
3. **Login**: Use your credentials to access the dashboard

### 📦 Adding Inventory Items
1. Navigate to the "Add Item" section
2. Fill in item details:
   - Name and category
   - Current stock and minimum threshold
   - Unit price and supplier information
   - Expiry date and location
   - Optional: Barcode or RFID tag
3. Save the item

### 📊 Managing Stock
- **Add Stock**: Increase inventory levels
- **Remove Stock**: Decrease inventory (with reason tracking)
- **Barcode Scan**: Quick stock updates using barcode scanner
- **RFID Tags**: Advanced tracking with RFID technology

### 🔔 Monitoring Alerts
- View all active alerts on the dashboard
- Low stock alerts appear automatically
- Expiry warnings show days remaining
- Email notifications sent to relevant staff

### 🛒 Automated Reordering
- System suggests restock quantities based on usage
- Purchase orders generated automatically
- Emails sent to suppliers with order details
- Cost tracking and budget monitoring

## 🏗️ Project Structure

```
Clinic_Inventory/
├── main.py                      # FastAPI application entry point
├── models.py                    # SQLAlchemy database models
├── db.py                        # Database configuration and utilities
├── seed_important_products.py   # Sample data seeder
├── requirements.txt             # Python dependencies
├── clinic_inventory.db          # SQLite database
├── templates/                   # HTML templates
│   ├── index.html              # Main dashboard
│   ├── auth.html               # Authentication pages
│   └── usage_api.js            # Frontend JavaScript
└── venv/                       # Virtual environment
```

## 🔧 API Endpoints

### Authentication
- `POST /api/signup` - User registration
- `POST /api/login` - User authentication
- `POST /api/verify-otp` - Email verification

### Inventory Management
- `GET /api/items` - Get all inventory items
- `POST /api/items` - Add new item
- `PUT /api/items/{id}/stock` - Update stock levels
- `GET /api/items/by-barcode/{code}` - Lookup by barcode
- `GET /api/items/by-rfid/{tag}` - Lookup by RFID

### Alerts & Monitoring
- `GET /api/alerts` - Get all alerts
- `GET /api/low-stock` - Get low stock items
- `GET /api/expiring-soon` - Get expiring items
- `GET /api/restock-suggestions` - Get restock recommendations

### Procurement
- `POST /api/purchase-orders/auto` - Generate purchase orders

## 🎨 UI Features

### Modern Design
- **Gradient Backgrounds** - Beautiful visual appeal
- **Card-based Layout** - Clean, organized information display
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Smooth Animations** - Professional user experience

### Interactive Elements
- **Real-time Updates** - Live data without page refresh
- **Modal Dialogs** - Clean form interactions
- **Toast Notifications** - User feedback and alerts
- **Search & Filter** - Easy item discovery

## 🔒 Security Features

- **Password Hashing** - Secure password storage with bcrypt
- **JWT Tokens** - Stateless authentication
- **Email Verification** - Account security
- **Role-based Access** - Permission management
- **Input Validation** - Data integrity protection

## 📊 Database Schema

### Core Tables
- **Users** - User accounts and authentication
- **Items** - Inventory items with full details
- **Transactions** - Stock movement history
- **Alerts** - System notifications
- **PurchaseOrders** - Procurement management
- **PurchaseOrderItems** - Order line items

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Use process manager (systemd, supervisor)
5. Configure SSL certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙏 Acknowledgments

- **FastAPI** - For the excellent web framework
- **SQLAlchemy** - For robust database operations
- **Font Awesome** - For beautiful icons
- **Google Fonts** - For typography

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for better healthcare management**

*VitaFlow - Streamlining clinic inventory, one item at a time.*
