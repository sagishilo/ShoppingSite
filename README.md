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
* Available stock
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
* Favorite items
* Shopping patterns

Then provides insights such as:

* Product recommendations
* Shopping behavior analysis
* Personalized suggestions

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
| Products | Opens product catalog   |

---

## 👤 Logged-In User Header

| Button       | Function                                 |
| ------------ | ---------------------------------------- |
| Home         | Returns to the home page                 |
| Products     | Opens the product catalog                |
| Cart         | Opens the current cart                   |
| Favorites    | Opens favorites page                     |
| Orders       | Displays order history                   |
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

| Button         | Function               |
| -------------- | ---------------------- |
| Remove Item    | Removes item from cart |
| Complete Order | Closes the order       |

---

## 🤖 AI Assistant Page

| Button       | Function                      |
| ------------ | ----------------------------- |
| Ask Question | Sends a question to the AI    |
| Clear Chat   | Resets assistant conversation |

---

# 🧠 Technologies Used

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

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
git clone https://github.com/yourusername/ai-shopping-assistant.git
cd ai-shopping-assistant
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
DATABASE_URL=mysql+pymysql://user:password@localhost/shopping_db
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
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── routes/
│   └── services/
│
├── UI/
│   └── streamlit_app.py
│
├── requirements.txt
└── README.md
```

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
