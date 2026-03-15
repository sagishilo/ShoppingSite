# 🛒 AI Shopping Assistant Web App - Smart Basket

A full-stack **AI-powered shopping website** that allows users to browse products, manage orders, save favorites, and interact with an **AI shopping assistant** that analyzes their shopping habits and provides insights.

The system combines:

* **FastAPI backend**
* **Streamlit frontend**
* **MySQL database**
* **OpenAI GPT integration**

The platform simulates a modern e-commerce experience with analytics and personalized AI insights.

---

# 📦 Main Features

## 👤 User System

Users can:

* Register for an account
* Log in securely
* View and update personal details
* Delete their account
* Manage their shopping activity

### Important Limitation

Certain features require being logged in.

Examples:

* Adding items to cart
* Adding items to favorites
* Viewing order history
* Using the AI assistant

---

# 🛍️ Product System

Users can browse products displayed in a grid layout.

Each product includes:

* Image
* Name
* Price
* Add to cart button
* Favorite button

### Product Actions

| Button          | Action                                            |
| --------------- | ------------------------------------------------- |
| 🛒 Add to Cart  | Adds the product to the user's current open order |
| ❤️ Favorite     | Adds the product to the user's favorites list     |
| 🔍 Product Card | Displays product details                          |

---

# 🛒 Shopping Cart

The shopping cart contains all items added to the current open order.

Users can:

* View items in the cart
* Increase or decreas amount
* Remove items
* Complete the order

### Cart Limitations

* Cart exists only when a user is logged in
* Each user can have **one open order at a time**

---

# 📦 Orders System

The system supports two types of orders:

### Open Orders

Orders that are currently being filled (shopping cart).

### Closed Orders

Orders that were completed by the user.

Users can:

* View order history
* See products in previous orders
* Analyze shopping behavior

---

# ⭐ Favorites System

Users can mark products as favorites.

Features:

* Add/remove favorite items
* View all favorites in a dedicated page
* Favorites persist per user

---

# 🤖 AI Shopping Assistant

One of the main features of the system is the **AI assistant**.

It analyzes the user’s:

* Order history
* Shopping patterns
* Products info


### AI Assistant Limitations

* Users can ask **up to 5 questions**
* The assistant works only when the user is logged in
* The assistant uses the **OpenAI API**

---

# 🔘 Website Navigation & Buttons

Below is a breakdown of the main UI buttons and their functionality.

---

## 🏠 Home Page

| Button   | Function                |
| -------- | ----------------------- |
| Login    | Opens login page        |
| Register | Opens registration page |
| Home page| Opens product catalog   |

---

## 👤 Logged-In User Header

| Button       | Function                                 |
| ------------ | ---------------------------------------- |
| Home         | Returns to the home page                 |
| Cart         | Opens the current cart                   |
| Personal page| Opens personal page                      |
| AI Assistant | Opens the AI analysis page               |
| Logout       | Logs the user out and clears the session |

---

## 🛍️ Product Page Buttons

| Button      | Function                            |
| ----------- | ----------------------------------- |
| Add to Cart | Adds product to open order          |
| Favorite ❤️ | Adds/removes product from favorites |

---

## 🛒 Cart Page Buttons

| Button         | Function                 |
| -------------- | -------------------------|
| Remove Item    | Removes item from cart   |
| Increase Item  | Add 1 to the amount      |
| Decreas Item   | Removes 1 from the amount|
| Complete Order | Closes the order         |

---

## 🤖 AI Assistant Page

| Button       | Function                      |
| ------------ | ----------------------------- |
| Ask Question | Sends a question to the AI    |


---

# 🧠 Technologies Used

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

## Cathing
* Redis

## Frontend

* Streamlit

## Database

* MySQL

## AI Integration

* OpenAI API

---

# 📊 Data Used by the AI Assistant

The AI assistant receives structured information including:

* User favorites
* Closed orders
* Temp order
* Purchased items
* Shopping statistics

The backend processes the data before sending it to the AI model.

---

# ⚠️ Important: OpenAI API Key

This project **does not include the OpenAI API key**.

Anyone running the project must add their own key.

### Setup

Create an environment variable:

```
OPENAI_API_KEY=your_api_key_here
```

Or configure it inside your local environment.

---

# 🚀 Installation Guide

## 1️⃣ Clone the repository

```
git clone https://github.com/sagishilo/ShoppingSite
cd gpt_service
```

---

## 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

## 3️⃣ Setup the Database

Create a MySQL database and update the connection configuration in the backend.

Example:

```
DATABASE_URL = mysql+aiomysql://"user":"password"@"localhost":"3306"/"main"
```

---

## 4️⃣ Run the Backend

```
uvicorn main:app --reload
```

---

## 5️⃣ Run the Frontend

```
streamlit run streamlit_app.py
```

---

# 🧱 Project Structure

```
project/
│
├── backend/
│
├── config/            # Configuration files (database connection, settings, etc.)
│
├── controller/        # API endpoints and request handling (FastAPI routes)
│
├── model/             # Data models and schemas used in the application
│
├── photos/            # Images used by the website
│
├── repository/        # Database queries and data access layer
│
├── resources/         # Additional resources used by the backend
│
├── service/           # Business logic and application services
│
├── UI/                # Streamlit frontend application
│
├── .env               # Environment variables (API keys, database credentials)
│
├── .gitignore         # Files ignored by Git
│
├── docker-compose.yaml # Docker configuration for running services
│
└── main.py            # Main FastAPI application entry point

└── README.md

---

# Active Users (test users)

#16
* user_name: aaa
* password: aaa

#17
* user_name: ש
* password: ש
---



---

# 🔒 Security Notes

* API keys are **not stored in the repository**
* Sensitive configuration should be stored in environment variables
* Database credentials should not be committed to GitHub

---

# 📈 Future Improvements

Possible future features:

* Product recommendation engine using Machine Learning
* Admin dashboard
* Product reviews and ratings
* Advanced analytics
* Smart product suggestions based on purchase patterns
* Email notifications for orders

---

# 👨‍💻 Author

Developed by **Sagi Shilo**

Project created as part of a software development learning project focusing on:

* Full-stack development
* API architecture
* AI integration
* Data analysis

---
