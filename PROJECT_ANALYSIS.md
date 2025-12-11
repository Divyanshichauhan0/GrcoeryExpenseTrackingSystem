# RashanScheduler - Project Analysis & Interview Guide

## 📋 Executive Summary

**RashanScheduler** is a web-based expense splitting application designed for shared household grocery management. It allows roommates or family members to track grocery purchases, calculate fair share amounts, and settle payments between users. The name "Rashan" is Hindi for "rations/groceries," making this a culturally relevant solution for Indian households.

---

## 🎯 Project Overview

### Purpose
The application solves a common problem: **tracking and splitting shared expenses fairly among multiple people**. Instead of manual calculations or awkward conversations about who owes whom, this app:
- Records all grocery purchases with the buyer's name
- Automatically calculates each person's fair share
- Shows who owes money to whom
- Tracks settlement payments to maintain accurate balances

### Core Problem Solved
When multiple people share groceries, different people buy items at different times. This creates an imbalance where some people spend more than others. The app calculates the fair split and generates the minimum number of transactions needed to balance everything out.

---

## 🏗️ Technical Architecture

### Technology Stack

**Backend:**
- **Flask** (Python web framework) - Lightweight, easy to use, perfect for small to medium applications
- **MySQL** - Relational database for structured data storage
- **Python-dotenv** - Environment variable management for secure configuration
- **MySQL Connector** - Python driver for MySQL database connection

**Frontend:**
- **HTML5** with Jinja2 templating
- **CSS3** for styling with modern design (gradients, animations, responsive layout)
- **Vanilla JavaScript** for client-side interactions

**Database:**
- MySQL relational database with 3 core tables (users, groceryitem, payments)

---

## 📊 Database Schema

### Tables

**1. users**
```
- id (Primary Key)
- name
```
Stores information about all users/roommates in the system.

**2. groceryitem**
```
- id (Primary Key)
- item_name
- price
- purchased_by (Foreign Key → users.id)
- date_added
```
Tracks every grocery item purchased, who bought it, and when.

**3. payments**
```
- id (Primary Key)
- payer_id (Foreign Key → users.id)
- receiver_id (Foreign Key → users.id)
- amount
- date_paid
```
Records settlement transactions between users.

### Relationships
- `groceryitem.purchased_by` → `users.id` (Many-to-One)
- `payments.payer_id` → `users.id` (Many-to-One)
- `payments.receiver_id` → `users.id` (Many-to-One)

---

## 🔧 Key Features & Functionality

### 1. **Dashboard (Home Page) - `/`**
- Displays the 10 most recent grocery purchases
- Shows person name, item name, price, and date
- Quick access buttons to add items and view analysis
- Edit/Delete functionality for each item

### 2. **Add New Item - `/add`**
- Form to add a new grocery item
- Fields: Item name, price, purchaser
- Dropdown populated from users table
- Redirects to home after successful addition

### 3. **Analysis Page - `/analysis`**
- **Most Complex Feature** - This is the heart of the application
- Calculates and displays:
  - Total group spending
  - Fair share per person (total ÷ number of users)
  - Each person's total spending
  - Net balance for each person (spent - fair_share - paid + received)
  - Optimized payment suggestions (who owes whom)

**Algorithm Explanation:**
1. Calculate total spending per user from groceryitem table
2. Determine fair share: `total_spending / number_of_users`
3. Fetch all previous payments made and received
4. Calculate net balance: `total_spent - fair_share - payments_made + payments_received`
5. Separate users into creditors (positive balance) and debtors (negative balance)
6. Use a greedy algorithm to generate minimum transactions
7. Match debtors with creditors until all balances settle

### 4. **Settle Payment - `/settle`**
- Allows users to record when someone has paid their debt
- Inserts record into payments table
- Automatically recalculates balances on analysis page

### 5. **Edit Item - `/edit/<item_id>`**
- Modify existing grocery item details
- Pre-fills form with current values
- Updates database on submission

### 6. **Delete Item - `/delete/<item_id>`**
- Removes grocery item from database
- Includes JavaScript confirmation to prevent accidental deletion

---

## 💡 Technical Highlights

### 1. **Environment Configuration**
- Uses `.env` file for sensitive database credentials
- Follows security best practices by not hardcoding passwords

### 2. **Database Connection Pooling**
- `get_db_connection()` function centralizes database connection logic
- Opens and closes connections properly to prevent leaks

### 3. **Type Safety**
- Uses Python's `typing` module (TypedDict) for better code documentation
- Helps catch errors during development

### 4. **SQL Optimization**
- Uses JOIN queries to fetch related data in a single call
- COALESCE function handles NULL values gracefully
- Aggregation functions (SUM, GROUP BY) for efficient calculations

### 5. **Balance Settlement Algorithm**
- Implements a greedy algorithm for minimizing transactions
- Time complexity: O(n²) where n is number of users
- Space complexity: O(n) for storing balances

### 6. **User Experience**
- Clean, modern UI with animations
- Responsive design principles
- Clear call-to-action buttons
- Confirmation dialogs for destructive actions
