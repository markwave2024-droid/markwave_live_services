# Markwave Live Services - Flask API

A Flask-based REST API for managing users, products, and purchases with Neo4j database integration.

## Features

- **User Management**: Create, update, and verify users
- **Product Catalog**: Manage buffalo products and inventory
- **Purchase Tracking**: Record and track user purchases
- **Neo4j Integration**: Graph database for complex relationships
- **CORS Support**: Cross-origin resource sharing enabled
- **Input Validation**: Simple Python validation functions
- **Static File Serving**: Frontend dashboard included

## Quick Start

### Prerequisites

- Python 3.8+
- Neo4j Database
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd markwave_live_services
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j credentials
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`

## Environment Configuration

Create a `.env` file with the following variables:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=your_neo4j_password_here
FLASK_ENV=development
FLASK_DEBUG=True
```

## API Endpoints

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/` | Create a new user |
| PUT | `/users/{mobile}` | Update user by mobile |
| PUT | `/users/id/{user_id}` | Update user by ID |
| GET | `/users/{mobile}` | Get user by mobile |
| GET | `/users/id/{user_id}` | Get user by ID |
| GET | `/users/referrals` | Get unverified referrals |
| GET | `/users/customers` | Get verified customers |
| POST | `/users/verify` | Verify user with device info |

### Product Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | Get all products |
| GET | `/products/{product_id}` | Get product details |

### Purchase Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/purchases/` | Create a purchase record |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Dashboard homepage |

## Request/Response Examples

### Create User
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "9876543210",
    "first_name": "John",
    "last_name": "Doe",
    "refered_by_mobile": "9876543211",
    "refered_by_name": "Jane Doe"
  }'
```

### Update User
```bash
curl -X PUT http://localhost:8000/users/9876543210 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "verified": true,
    "city": "Mumbai"
  }'
```

### Verify User
```bash
curl -X POST http://localhost:8000/users/verify \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "9876543210",
    "device_id": "device123",
    "device_model": "iPhone 12"
  }'
```

## Data Models

### User Schema
- `mobile` (required): User's mobile number
- `first_name` (required): User's first name
- `last_name` (required): User's last name
- `refered_by_mobile` (required): Referrer's mobile number
- `refered_by_name` (optional): Referrer's name
- `email`: Email address
- `verified`: Verification status
- `dob`: Date of birth (MM-DD-YYYY format)
- `address`, `city`, `state`: Location details
- `aadhar_number`: Aadhar card number
- `custom_fields`: Additional custom data

### Product Schema
- `id`: Product identifier
- `breed`: Buffalo breed
- `age`: Age in years
- `milkYield`: Daily milk yield in liters
- `price`: Price in INR
- `inStock`: Availability status
- `insurance`: Insurance amount
- `buffalo_images`: Array of image URLs

## Development

### Project Structure
```
markwave_live_services/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── static/            # Static files
│   └── index.html     # Dashboard homepage
└── README.md          # Documentation
```

### Key Changes from FastAPI

1. **Framework**: Converted from FastAPI to Flask
2. **Validation**: Replaced Pydantic with simple Python validation functions
3. **Responses**: Using `jsonify()` instead of direct dict returns
4. **Routing**: Flask decorators instead of FastAPI decorators
5. **CORS**: Using Flask-CORS extension
6. **Static Files**: Flask's `send_from_directory()` for static serving

### Error Handling

The API returns standardized error responses:

```json
{
  "statuscode": 400,
  "status": "error",
  "message": "Validation error",
  "errors": {
    "field_name": ["Error description"]
  }
}
```

## Deployment

### Production Considerations

1. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask's development server
2. **Environment**: Set `FLASK_ENV=production`
3. **Security**: Configure proper CORS origins instead of "*"
4. **Database**: Ensure Neo4j is properly secured and backed up
5. **Logging**: Implement proper logging for production monitoring

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.