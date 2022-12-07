## Setup

Prerequisites: python3, pip

` $ python3 -m venv e`

`$ source env/bin/activate`

`$ pip install -r requirements.txt`

`$ flask --app main run`

The app can be accessed at localhost:5000


## Security Measurements

- Authentication with flask-jwt-extended => token-based, double submit-pattern
- Authorization (user role, admin role)
- Input validation
- Security Headers
  - same site origin policy
  - Content-Security-Policy
  - Strict-Transport-Security'
  - Cross-origin resource sharing
- Cookie policy
- https enforced
- SSL certificate provided by pythonanywhere
- Password security
- XSS protection
- CSRF protection
- Server side request forgery protection
- Preventing Cross-origin resource sharing
- SQL Injection protection


## Deployment

The [flask application](emely3h.pythonanywhere.com) is deployed using pythonanywhere. SQLite is also used on production.

## Thread Model

![thread model](docs/thread_model.png "Thread Model")


## Routing

Routes created in the backend:

  all users
  - GET /
  - GET /book-request
  - GET /auth/login
  - GET /auth/register
  - POST /auth/login
  - POST /auth/register
  - GET /book?id=1
  
  Logged in users only
  - POST /borrow-book
  - POST /reading-list
  - POST /auth/logout
  - GET /my-books
  - POST /my-books/extend
  - POST /book-request
  - DELETE /reading-list
  
  admin(s) only
  - GET /admin
  - POST /admin/add-book
  - POST /admin/book-status # PUT?

## DB doc

![db schema](docs/db_schema.png "DB Schema")


