# Parlay App

A full-stack sports betting parlay application built with FastAPI (Python) backend, React (TypeScript) frontend, and PostgreSQL database, all containerized with Docker.

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: React with TypeScript and Material-UI
- **Database**: PostgreSQL with Alembic migrations
- **Containerization**: Docker and Docker Compose

## 📁 Project Structure

```
parlay_app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   └── token.py
│   │   └── main.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── init-db.sh
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd parlay_app
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🛠️ Development Setup

### Backend Development

1. **Start only the database**
   ```bash
   docker-compose -f docker-compose.dev.yml up db
   ```

2. **Set up Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

## 🗄️ Database

### Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts with authentication
  - id (Primary Key)
  - email (Unique)
  - hashed_password
  - full_name
  - is_active
  - created_at
  - updated_at

### Database Migrations

Database migrations are handled by Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://parlay_user:parlay_password@localhost:5432/parlay_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://frontend:3000"]
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/users/` - User registration

### Users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users/` - Create new user

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

## 🐳 Docker Commands

### Build and Run
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Development
```bash
# Start only database for development
docker-compose -f docker-compose.dev.yml up db

# Run ingestion inside backend container
docker-compose exec backend python3 ingestion_api/ingestion.py

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Production Deployment

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.yml build
   ```

2. **Set production environment variables**
   - Update `.env` with production values
   - Set secure `SECRET_KEY`
   - Configure production database URL

3. **Deploy**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS configuration
- SQL injection protection via SQLAlchemy ORM
- Input validation with Pydantic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Database connection errors**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify database exists and user has permissions

2. **Port conflicts**
   - Change ports in `docker-compose.yml` if 3000, 8000, or 5432 are in use

3. **Frontend build errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

4. **Backend import errors**
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

### Getting Help

- Check the logs: `docker-compose logs -f [service-name]`
- Review the API documentation at http://localhost:8000/docs
- Ensure all services are healthy: `docker-compose ps`
