# Markwave Live Services - Architecture

## 📁 Project Structure

```
markwave_live_services/
├── app.py                 # Main FastAPI application
├── models/                # Pydantic models
│   └── __init__.py       # Request/Response models
├── routers/               # API route modules
│   ├── __init__.py
│   ├── users.py          # User management endpoints
│   ├── products.py       # Product endpoints
│   └── purchases.py      # Purchase endpoints
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── database.py       # Neo4j connection
│   └── user_helpers.py   # User-related helpers
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables

```

## 🎯 Module Breakdown

### **app.py** - Main Application
- FastAPI app initialization
- CORS middleware configuration
- Router registration
- Root and health endpoints

### **models/** - Data Models
All Pydantic models for request validation and response schemas:
- `UserCreate`, `UserUpdate`, `UserVerify`
- `Purchase`
- Response models: `UserCreateResponse`, `UserListResponse`, `ProductResponse`, etc.

### **routers/** - API Endpoints

#### **users.py** - User Management (8 endpoints)
- `POST /users` - Create or fetch user
- `PUT /users/{mobile}` - Update by mobile
- `PUT /users/id/{user_id}` - Update by UUID
- `GET /users/referrals` - List unverified users
- `GET /users/customers` - List verified customers
- `GET /users/{mobile}` - Get user by mobile
- `GET /users/id/{user_id}` - Get user by UUID
- `POST /users/verify` - Verify user and issue OTP

#### **products.py** - Product Management (2 endpoints)
- `GET /products` - List all buffalo products
- `GET /products/{product_id}` - Get product details

#### **purchases.py** - Purchase Management (1 endpoint)
- `POST /purchases/` - Record a purchase

### **utils/** - Utilities

#### **database.py**
- `get_driver()` - Neo4j driver connection

#### **user_helpers.py**
- `build_update_clauses()` - Build Cypher SET clauses
- `format_dob()` - Format date of birth

## 🚀 Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Or use the built-in runner
python3 app.py
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Environment Variables

Required in `.env`:
- `NEO4J_URI` - Neo4j database URI
- `NEO4J_PASSWORD` - Neo4j password

## 🎨 Benefits of Modular Structure

1. **Separation of Concerns** - Each module has a single responsibility
2. **Maintainability** - Easy to locate and update specific functionality
3. **Scalability** - Simple to add new routers/modules
4. **Testability** - Each module can be tested independently
5. **Reusability** - Shared models and utilities across routers
6. **Clean Code** - Main app.py is now ~80 lines instead of 900+

## 📝 Adding New Features

### Add a new router:
1. Create `routers/new_module.py`
2. Define router: `router = APIRouter(prefix="/new", tags=["New"])`
3. Add endpoints with decorators
4. Import and register in `app.py`: `app.include_router(new_module.router)`

### Add new models:
1. Add to `models/__init__.py`
2. Import in relevant router

### Add new utilities:
1. Create in `utils/` directory
2. Import where needed
