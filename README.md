# About
<br>
<img src="https://github.com/user-attachments/assets/795962a5-3647-4921-abcb-28e7d43124bb" alt="image" width="200"/>
<br><br>

**Alchazar Education** is a unique educational platform designed specifically for alchemists to master their craft.
The platform offers user registration, course enrollment, interactive testing, and a ranking system that highlights the top 10 users based on their performance.

## Technologies

- Python 3.11+
- Django 5.2
- Django REST Framework
- PostgreSQL
- Redis (for cache and Celery broker)
- Celery (for background tasks)
- Simple JWT (JWT authentication)
- drf-spectacular (automatic OpenAPI schema generation)
- django-celery-beat (Celery task scheduler)

## API Endpoints

- **POST** /api/register/ — Register a new user
- **POST** /api/token/ — Obtain JWT token
- **POST** /api/token/refresh/ — Refresh JWT token
- **GET** /api/courses/ — List all courses
- **GET** /api/my-courses/ — List courses enrolled by the user
- **POST** /api/enroll/ — Enroll in a course
- **DELETE** /api/leave/<id>/ — Leave a course
- **GET** /api/courses/<course_id>/lections/ — List lectures in a course
- **GET** /api/lections/<lection_id>/tests/ — List tests for a lecture
- **POST** /api/lections/<lection_id>/take-test/ — Take a test
- **GET** /api/top10-users/ — Get top 10 users by score

## API Documentation

Swagger UI is available at:
- http://your-domain-or-ip:port/api/swagger/
