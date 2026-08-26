# AI-Powered Full Stack E-Commerce Project Using Python

## Project Overview

The AI-Powered Full Stack E-Commerce Project is a web-based online shopping application developed using Python and Django.

The application is designed to provide a complete e-commerce experience, including product browsing, category-based navigation, product search, shopping cart management, wishlist management, checkout, order management, and user profile management.

The project follows a structured full-stack architecture with Django as the backend framework, HTML, CSS, and JavaScript for the frontend, and SQLite as the database.

AI-based capabilities are planned as part of the project's future development to enhance product discovery and provide a more personalized shopping experience.

## Key Features

### User Features

- User registration and authentication
- User login and logout
- User profile management
- Product browsing
- Category-based product navigation
- Product search
- Product detail pages
- Shopping cart management
- Wishlist management
- Checkout
- Order placement
- Order history
- Order detail view

### Admin Features

- Admin authentication
- Admin dashboard
- Product management
- Product creation and editing
- Product image management
- Category management
- Order management
- Order status management

### Application Features

- Responsive user interface
- Product image handling
- Structured service and repository layers
- Database-driven product and order management
- Modular Django application structure

## Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Django

### Database

- SQLite

### Development Tools

- Visual Studio Code
- Git
- GitHub

## Project Architecture

The project follows a modular structure that separates application responsibilities into different components such as models, views, services, repositories, templates, and static resources.

```text
FashionStore_Project/
│
├── fashionstore/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── shop/
│   ├── migrations/
│   ├── repositories/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── media/
├── manage.py
├── requirements.txt
├── .gitignore
├── db.sqlite3
└── README.md


## Installation and Setup

### 1. Clone the Repository
```git clone https://github.com/Monika-Tech-Source/AI-powered-Full-Stack-E-commerce-Project.git

Navigate to the project directory:
```cd AI-powered-Full-Stack-E-commerce-Project

### 2. Create a Virtual Environment
```python -m venv .venv

### 3. Activate the Virtual Environment
    on windows:
```.venv\Scripts\activate

    On macOS or Linux:
```source .venv/bin/activate

### 4. Install Dependencies
```pip install -r requirements.txt

### 5. Apply Database Migrations
```python manage.py migrate

### 6. Start the Development Server
    http://127.0.0.1:8000/


Development Workflow
After making changes to the project, check the current Git status:

git status
Stage the changes:
```git add .

Create a commit describing the changes:
```git commit -m "Describe your changes"

Push the changes to GitHub:
```git push


Future Enhancements
The following features are planned for future development:
- AI-powered product recommendations
- Personalized product discovery
- AI-based customer support chatbot
- Intelligent product search
- Personalized shopping suggestions
- Online payment gateway integration
- Advanced analytics and reporting
- Cloud deployment
Project Goals
The primary goals of this project are to:
- Build a complete full-stack e-commerce application using Python and Django
- Implement a structured and maintainable application architecture
- Develop practical user and administrator workflows
- Integrate AI capabilities into the e-commerce experience
- Gain practical experience with Git, GitHub, backend development, frontend development, and database management


Author
Monika-Tech-Source
GitHub: https://github.com/Monika-Tech-Source
