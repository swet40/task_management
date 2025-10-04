# Task Management REST API

A FastAPI-based REST API for task management with JWT authentication, similar to simplified Trello/Asana.

##  Features

- **User Authentication**: JWT-based registration and login
- **Task Management**: Full CRUD operations for tasks
- **Categories**: Organize tasks into categories
- **Filtering**: Filter tasks by status, category, or due date
- **Validation**: Pydantic input validation
- **Containerized**: Docker support for easy deployment
- **Documentation**: Auto-generated Swagger UI

##  API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token

### Categories
- `POST /categories` - Create category (Auth required)
- `GET /categories` - List user's categories (Auth required)

### Tasks
- `POST /tasks` - Create task (Auth required)
- `GET /tasks` - List tasks with filters (Auth required)
- `GET /tasks/{id}` - Get single task (Auth required)
- `PUT /tasks/{id}` - Update task (Auth required)
- `DELETE /tasks/{id}` - Delete task (Auth required)

### Filter Parameters for GET /tasks
- `status` - pending, in_progress, completed
- `category_id` - Filter by category ID
- `due_date` - Filter by due date (YYYY-MM-DD)

##  Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

# Access API documentation
# http://localhost:8000/docs

##  Docker Deployment

# Build the image
docker build -t task-management-api .

# Run the container
docker run -d -p 8000:8000 --name task-api task-management-api

# Test the API
curl http://localhost:8000/

## Docker Compose

docker-compose up -d