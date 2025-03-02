# Smart Queue Management System

## Overview
This is a **Flask-based Smart Queue Management System** that allows users to join queues, manage their positions, and receive notifications via SMS and email. The system is built using Flask, SQLAlchemy, and Flask-Login for authentication.

## Features
- **User Authentication** (Flask-Login based, session-based authentication)
- **Queue Management** (Create, join, and leave queues)
- **Admin Controls** (Only admins can delete queues and process queue actions)
- **Notifications** (Users receive SMS and email notifications about their queue status)
- **Web Interface** (Flask with Bootstrap for UI)
- **REST API** (Fetch queue details programmatically)

## Technologies Used
- **Flask** (Web framework)
- **Flask-Login** (Session-based user authentication)
- **Flask-SQLAlchemy** (ORM for database management)
- **SQLite** (Database for storing user and queue data)
- **Flask-Mail** (Email notifications)
- **Twilio API** (SMS notifications)
- **Flask-Bootstrap & Flask-CKEditor** (Frontend UI enhancements)

## Installation & Setup
### 1. Clone the repository:
```bash
git clone https://github.com/your-repo/smart-queue-system.git
cd smart-queue-system
```

### 2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Configure environment variables:
Create a `.env` file and add:
```bash
SECRET_KEY='your_secret_key'
MAIL_USERNAME='your_email@gmail.com'
MAIL_PASSWORD='your_email_password'
TWILIO_ACCOUNT_SID='your_twilio_sid'
TWILIO_AUTH_TOKEN='your_twilio_token'
TWILIO_PHONE_NUMBER='your_twilio_number'
```

### 4. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

### 5. Run the application:
```bash
flask run
```

## API Endpoints
### **Get Queue Details**
```http
GET /api/queue/<queue_id>
```
#### Response Example:
```json
{
  "id": 1,
  "name": "Customer Support Queue",
  "users": [
    {"id": 101, "position": 1, "status": "waiting"},
    {"id": 102, "position": 2, "status": "waiting"}
  ]
}
```

## Authentication Method
This project uses **Flask-Login for session-based authentication**. Users must log in to join or manage queues. **JWT authentication is NOT used in this system yet ;).**


---
**Contributors:**
- Walid Hasan (CioFlingar)
- Open to contributions! Feel free to fork and improve the project.

