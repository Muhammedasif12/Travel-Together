
# 🌍 Travel Together

Travel Together is a Django-based web application that allows users to discover, book, and experience travel with strangers. The platform focuses on social travel by combining trip booking with group interaction features.

---

## 🚀 Features

### 👤 User System
- User registration and login
- Profile management
- Authentication system

### 🧳 Travel Packages
- View and explore travel packages
- Trip details including duration (trip days)
- Admin can manage packages

### 🛒 Booking System
- Add trips to cart
- Enter booking details (name, address, email, pincode)
- Payment status tracking
- Upload payment proof

### 💬 Group Chat (GChat)
- Chat system for users in the same trip
- Enables communication and coordination

### ❤️ Wishlist
- Save trips for later
- Easy access to preferred packages

### 📝 Feedback
- Users can submit feedback
- Helps improve platform experience

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite
- **Architecture:** MVT (Model-View-Template)

---

## 📂 Project Structure


Traveltogether/
│── Craftify/ # Main project settings
│── CraftifyApp/ # Core application
│ ├── models.py # Database models (User, Products, Cart, Chat, etc.)
│ ├── views.py # Application logic
│ ├── urls.py # Routing
│ ├── templates/ # HTML templates
│ └── migrations/ # Database migrations
│── manage.py


---

## ⚙️ Installation & Setup

1. Clone repository:
```bash
git clone https://github.com/yourusername/travel-together.git
cd travel-together

---

Create virtual environment:
python -m venv venv
venv\Scripts\activate   # Windows

---

Install dependencies:
pip install django

---


Run migrations:
python manage.py makemigrations
python manage.py migrate

---

Start server:
python manage.py runserver

---

Open browser:
http://127.0.0.1:8000/

---

