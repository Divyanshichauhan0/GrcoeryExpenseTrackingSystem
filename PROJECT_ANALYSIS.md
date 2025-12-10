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

---

## 🎤 Interview Explanation Script

### **Opening Statement:**
"I developed RashanScheduler, a web application that simplifies shared expense management for roommates or families sharing grocery costs. The application tracks who bought what, calculates fair splits, and suggests optimal payment settlements."

### **Technical Deep Dive:**
"On the backend, I used Flask with Python because of its simplicity and rapid development capabilities. For data persistence, I chose MySQL as it perfectly suits the relational nature of the data - users, items, and payments are interconnected. 

The most interesting part was implementing the expense settlement algorithm. It calculates each person's net balance by considering their spending, their fair share, and any payments already made. Then, using a greedy algorithm, it determines the minimum transactions needed to settle all debts. For example, if person A owes $50 and person B is owed $30 and person C is owed $20, the algorithm finds that A should pay B $30 and C $20 - just two transactions instead of potentially more complex scenarios."

### **Challenges Overcome:**
"One challenge was handling edge cases in the settlement calculation - like when someone has already made partial payments or when expenses are perfectly balanced. I solved this using SQL aggregation with COALESCE to handle NULL values and implemented thorough balance recalculation logic."

### **Results:**
"The application successfully reduces the mental overhead of splitting expenses and eliminates the awkwardness of tracking who owes whom. It's production-ready for small groups and could easily scale with additional features like receipt uploads or mobile responsiveness."

---

## ❓ Interview Follow-Up Questions & Answers

### **Q1: How would you scale this application for 1000+ users?**

**Answer:**
"Currently, the app is designed for small groups (3-10 users). To scale to 1000+ users:

1. **Database Optimization:**
   - Add indexes on frequently queried columns (purchased_by, payer_id, receiver_id, date_added)
   - Implement database connection pooling (SQLAlchemy with connection pools)
   - Consider read replicas for analysis queries

2. **Application Architecture:**
   - Move from synchronous Flask to asynchronous framework (FastAPI)
   - Implement caching (Redis) for analysis calculations
   - Add pagination to item listings

3. **Multi-tenancy:**
   - Redesign schema to support multiple groups
   - Add group_id to all tables
   - Implement user authentication with JWT tokens

4. **Infrastructure:**
   - Deploy on cloud platform (AWS/GCP) with load balancing
   - Use CDN for static assets
   - Implement horizontal scaling with multiple app servers"

---

### **Q2: What security vulnerabilities exist and how would you fix them?**

**Answer:**
"Current vulnerabilities and fixes:

1. **SQL Injection:**
   - Currently using parameterized queries (✓ already secure)
   - Could improve by using an ORM like SQLAlchemy for additional abstraction

2. **No Authentication:**
   - Anyone can access any data
   - Fix: Implement Flask-Login or JWT-based authentication
   - Add role-based access control (RBAC)

3. **No Authorization:**
   - Users can edit/delete anyone's items
   - Fix: Add ownership checks before allowing modifications

4. **Password in .env:**
   - .env file could be committed to Git
   - Fix: Add .env to .gitignore, use environment variables in production
   - Consider using vault services (AWS Secrets Manager)

5. **No CSRF Protection:**
   - Forms are vulnerable to cross-site request forgery
   - Fix: Implement Flask-WTF with CSRF tokens

6. **No Input Validation:**
   - Could enter negative prices or invalid data
   - Fix: Add server-side validation with constraints and Pydantic models"

---

### **Q3: Walk me through the algorithm for calculating who owes whom.**

**Answer:**
"It's a classic debt settlement problem solved with a greedy algorithm:

**Step 1:** Calculate net balance for each person
```
balance = total_spent - fair_share - payments_made + payments_received
```

**Step 2:** Separate into two groups
- Creditors: positive balance (owed money)
- Debtors: negative balance (owe money)

**Step 3:** Match debtors with creditors
- Start with first creditor and first debtor
- Transaction amount = minimum of creditor's balance and absolute debtor's balance
- Reduce both balances by transaction amount
- Move to next creditor/debtor when balance reaches zero

**Example:**
- Alice spent ₹300, fair_share = ₹200 → balance = +₹100 (creditor)
- Bob spent ₹100, fair_share = ₹200 → balance = -₹100 (debtor)
- Result: Bob pays Alice ₹100 (one transaction)

**Complexity:** O(n²) in worst case, but typically O(n) for small groups."

---

### **Q4: How would you add a feature to support multiple expense groups (like different friend circles)?**

**Answer:**
"I would implement multi-tenancy:

**Database Changes:**
1. Add new table: `groups`
   - id, name, created_date

2. Add `group_id` foreign key to:
   - users → user_groups (many-to-many junction table)
   - groceryitem
   - payments

**Application Changes:**
1. Add authentication system to identify current user
2. Add group selection/creation interface
3. Modify all queries to filter by current group_id
4. Update analysis calculations to work per-group

**SQL Example:**
```sql
SELECT u.name, SUM(g.price) as total
FROM groceryitem g
JOIN users u ON g.purchased_by = u.id
WHERE g.group_id = ?
GROUP BY u.name
```

**UI Changes:**
- Add group selector in navigation
- Dashboard shows active group name
- Option to switch between groups"

---

### **Q5: How would you test this application?**

**Answer:**
"I would implement a comprehensive testing strategy:

**1. Unit Tests (pytest):**
```python
def test_balance_calculation():
    # Test fair share calculation
    assert calculate_fair_share(600, 3) == 200
    
def test_settlement_algorithm():
    # Test payment generation
    balances = [
        {'name': 'Alice', 'balance': 100},
        {'name': 'Bob', 'balance': -100}
    ]
    transactions = generate_settlements(balances)
    assert len(transactions) == 1
    assert transactions[0]['amount'] == 100
```

**2. Integration Tests:**
- Test database CRUD operations
- Test Flask routes with test client
- Mock database connections

**3. End-to-End Tests (Selenium/Playwright):**
- Test complete user flows
- Add item → view analysis → settle payment

**4. Load Testing (Locust):**
- Simulate multiple concurrent users
- Identify bottlenecks

**5. Manual Testing:**
- Edge cases: zero items, single user, equal spending
- UI responsiveness on different devices"

---

### **Q6: What would be the first three features you'd add next?**

**Answer:**
"Prioritized by user value:

**1. User Authentication & Profiles**
- Why: Currently anyone can see/edit all data
- Implementation: Flask-Login with password hashing (bcrypt)
- Impact: Enables privacy and personalization

**2. Expense Categories & Charts**
- Why: Users want to see spending patterns
- Implementation: Add category field to groceryitem (vegetables, dairy, snacks)
- Visualization: Chart.js pie/bar charts for category breakdown
- Impact: Better financial insights

**3. Mobile Responsive Design**
- Why: Most users will access from phones while shopping
- Implementation: CSS media queries and mobile-first design
- Touch-friendly buttons and forms
- Impact: Improved accessibility and usage

**Bonus Feature:** 
Push notifications or email alerts when someone owes money or when you're owed money - improves engagement and settlement rates."

---

### **Q7: Explain your choice of Flask over Django.**

**Answer:**
"I chose Flask for several reasons:

**Advantages of Flask for this project:**
1. **Simplicity:** Microframework without unnecessary features for a small app
2. **Flexibility:** Can choose exact components needed (MySQL connector, not Django ORM)
3. **Learning curve:** Faster to set up and understand
4. **Lightweight:** Less overhead for simple CRUD operations
5. **Control:** More explicit control over request/response cycle

**When Django would be better:**
- Built-in admin panel needed
- Built-in authentication required from start
- Larger application with many interconnected features
- Team prefers convention-over-configuration

**In this case:**
The app has 7 routes and 3 database tables - Flask's minimalist approach was perfect. If this grew to 50+ routes with complex business logic, I'd consider migrating to Django or using Flask with blueprints for better organization."

---

### **Q8: How is the fair share calculation fair if people eat different amounts?**

**Answer:**
"Great observation! The current implementation uses **equal split**, which assumes equal consumption. This is a design decision with trade-offs:

**Current Approach (Equal Split):**
- Pros: Simple, transparent, reduces conflicts
- Cons: Unfair if consumption varies significantly

**Alternative Approaches:**

**1. Weighted Split by Consumption:**
- Add `consumption_ratio` to users table
- Example: Alice: 1.5, Bob: 1.0, Charlie: 0.5
- Fair share = (total × your_ratio) / sum_of_all_ratios
- Implementation:
```python
total_weight = sum(user['ratio'] for user in users)
fair_share = (total_spent * user['ratio']) / total_weight
```

**2. Item-level Splitting:**
- Add `consumers` many-to-many relationship to groceryitem
- Each item specifies who consumed it
- Only those people split that item's cost

**3. Hybrid Approach:**
- Some items are shared (milk, bread) - equal split
- Some items are personal (specific snacks) - individual cost
- Add `split_type` field to groceryitem

I would discuss with users to understand their preference and implement accordingly. For most roommate situations, equal split works well as an average over time."

---

### **Q9: How would you deploy this application to production?**

**Answer:**
"Step-by-step deployment process:

**1. Preparation:**
```bash
# Create requirements.txt
pip freeze > requirements.txt

# Add production WSGI server
# Add: gunicorn==21.2.0
```

**2. Configuration:**
- Set `app.run(debug=False)` for production
- Use environment variables instead of .env file
- Configure production database (not localhost)

**3. Cloud Deployment (AWS example):**

**Option A: EC2 + RDS**
- EC2 instance for Flask app
- RDS MySQL for database
- Nginx as reverse proxy
- Gunicorn as WSGI server

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Setup app
git clone <repo>
pip install -r requirements.txt

# Configure Nginx
location / {
    proxy_pass http://localhost:5000;
}

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Option B: Platform-as-a-Service (Heroku/Railway)**
- Push to Git repository
- Add Procfile: `web: gunicorn app:app`
- Configure DATABASE_URL environment variable
- Automatic deployment on push

**4. Additional Production Considerations:**
- SSL certificate (Let's Encrypt)
- Domain name setup
- Backup strategy for database
- Monitoring (Sentry for errors, CloudWatch for logs)
- CI/CD pipeline (GitHub Actions)"

---

### **Q10: What performance bottlenecks exist and how would you optimize?**

**Answer:**
"Identified bottlenecks and solutions:

**1. Analysis Page - Multiple Queries**
- Current: 3 separate queries for spent/paid/received
- Fix: Single query with JOINs and subqueries
```sql
SELECT 
    u.id, u.name,
    COALESCE(SUM(g.price), 0) as spent,
    COALESCE(paid.total, 0) as paid,
    COALESCE(received.total, 0) as received
FROM users u
LEFT JOIN groceryitem g ON g.purchased_by = u.id
LEFT JOIN (SELECT payer_id, SUM(amount) as total FROM payments GROUP BY payer_id) paid
    ON paid.payer_id = u.id
LEFT JOIN (SELECT receiver_id, SUM(amount) as total FROM payments GROUP BY receiver_id) received
    ON received.receiver_id = u.id
GROUP BY u.id
```

**2. No Database Indexes**
- Add: `CREATE INDEX idx_purchased_by ON groceryitem(purchased_by)`
- Add: `CREATE INDEX idx_date ON groceryitem(date_added)`

**3. Recalculating Everything on Every Load**
- Cache analysis results with Redis
- TTL: 5 minutes or invalidate on new item/payment
```python
@cache.cached(timeout=300, key_prefix='analysis')
def get_analysis():
    # ... calculation logic
```

**4. N+1 Query Problem (if expanded)**
- Use eager loading if using ORM
- Fetch all related data in single query

**5. Large Data Sets**
- Pagination on home page (currently only shows 10)
- Date range filters for analysis
- Archive old transactions

**Measurement:**
- Add logging for query execution time
- Use Flask-DebugToolbar in development
- Monitor with APM tools (New Relic, DataDog) in production"

---

## 🎯 Strengths to Highlight

1. ✅ **Clean Code Structure:** Separation of concerns, DRY principles
2. ✅ **Practical Problem Solving:** Real-world applicable solution
3. ✅ **Algorithm Implementation:** Settlement algorithm shows CS fundamentals
4. ✅ **Full-Stack Skills:** Backend (Python/MySQL) + Frontend (HTML/CSS/JS)
5. ✅ **Database Design:** Proper normalization and relationships
6. ✅ **Security Awareness:** Using parameterized queries prevents SQL injection
7. ✅ **User Experience Focus:** Confirmations, clear UI, helpful messages

---

## 🚀 Potential Enhancements for Discussion

- Receipt image upload with OCR for automatic item entry
- Mobile app (React Native/Flutter)
- Recurring expenses (monthly subscriptions)
- Budget limits and alerts
- Export data to CSV/PDF
- Integration with payment apps (UPI, PayPal)
- Bill splitting with percentages/ratios
- Multi-currency support
- Analytics dashboard with charts

---

## 📝 Code Quality Improvements to Mention

1. **Current:** Direct SQL queries → **Better:** Use SQLAlchemy ORM
2. **Current:** No validation → **Better:** Add Pydantic models or Flask-WTF forms
3. **Current:** No error handling → **Better:** Add try-catch blocks and error pages
4. **Current:** Hardcoded strings → **Better:** Configuration file or constants
5. **Current:** No logging → **Better:** Add logging for debugging and monitoring

---

## 🎓 Key Takeaways for Interview

**What You Learned:**
- Full-stack web development with Flask
- Database design and SQL optimization
- Algorithm implementation (debt settlement)
- User interface design principles
- Working with environment variables for security

**What You Would Do Differently:**
- Start with authentication from day one
- Use an ORM instead of raw SQL for better abstraction
- Write tests alongside development (TDD)
- Add more comprehensive error handling
- Implement proper logging from the start

**Business Value:**
- Reduces friction in shared living situations
- Increases financial transparency among roommates
- Saves time compared to manual calculations
- Reduces potential conflicts over money

---

## 💼 Closing Statement for Interview

"RashanScheduler demonstrates my ability to identify a real-world problem, design a complete solution, and implement it using modern web technologies. It showcases my understanding of both frontend and backend development, database design, and algorithmic thinking. I'm excited about the opportunity to apply these skills to larger, more complex projects and continue learning from experienced developers on your team."

---

**Good luck with your interview! 🎯**