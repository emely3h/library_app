## Setup

Prerequisites: python3, pip

` $ python3 -m venv e`

`$ source env/bin/activate`

`$ pip install -r requirements.txt`

`$ flask --app main run`

The app can be accessed at localhost:5000


## Security Measurements

- Authentication with flask-jwt-extended => token-base, double submit-pattern
- Authorization (user role, admin role)
- Input validation in the backend
- Security Headers
  - same site origin policy
  - Content-Security-Policy
  - Cross-origin resource sharing
- https enforced
- TLS certificate
- Password security, appropiate complexity, hashed before (using a salt) before saved
- XSS protection
- CSRF protection
- Server side request forgery protection
- Preventing Cross-origin resource sharing
- SQL Injection protection
- Content-Security-Policy
- Strict-Transport-Security'


## Thread Model

![thread model](docs/thread_model.png "Thread Model")


## Backend Doc

Routes created in the backend:

  all users
  - GET /
  - GET /book-request
  - GET /auth/login
  - GET /auth/register
  - POST /auth/login
  - POST /auth/register
  - GET /book/<id>
  
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
  - POST /admin/book-status





## DB doc

![db schema](docs/db_schema.png "DB Schema")


