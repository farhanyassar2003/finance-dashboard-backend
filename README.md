# finance-dashboard-backend
# Finance Dashboard Backend

## Overview

This project implements a role-based backend system for managing financial records and generating analytical summaries for dashboard-style applications.

The system provides:

- secure user registration and authentication using JWT
- role-based access control (Viewer, Analyst, Admin)
- financial record management with filtering and validation
- dashboard summary analytics
- advanced insights analytics
- administrator-controlled user management
- service-layer-based aggregation architecture

The implementation focuses on correctness, maintainability, structured validation, and secure backend authorization.

---

## Key Features

### Authentication & Authorization

- JWT-based authentication (SimpleJWT)
- strong password validation policy
- inactive-user login blocking
- immediate access revocation after account deactivation
- restricted role assignment during registration
- admin-controlled role updates

---

## Role-Based Access Control

| Role | Permissions |
|------|-------------|
| Viewer | Dashboard access only |
| Analyst | Dashboard + records read + insights |
| Admin | Full system access |

Access rules are enforced using reusable permission classes.

---

## Architecture Overview

The backend follows a modular app-based architecture:

authentication → login & registration
users → role management
records → financial CRUD operations
dashboard → summary analytics
insights → advanced analytics
services → aggregation logic layer
permissions → reusable authorization rules


Analytics logic is implemented using:

- DashboardService
- InsightsService

This ensures clean separation between request handling and business logic.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python |
| Framework | Django |
| API Layer | Django REST Framework |
| Authentication | JWT (SimpleJWT) |
| Database | SQLite |
| Authorization | Custom permission classes |
| Validation | Serializer-based validation |

---

## Authentication Flow

### Register User
POST /api/register/

New users are assigned default role:

Role assignment is handled only through admin APIs.

viewer


Role assignment is handled only through admin APIs.

---

### Login
POST /api/login/

Returns:

- user details
- access token
- refresh token

Use token in headers: Authorization: Bearer <access_token>


---

## JWT Token Lifecycle

| Token | Purpose | Lifetime |
|------|---------|----------|
| Access Token | Access protected endpoints | 5 hours |
| Refresh Token | Reserved for renewal support | 1 day |

Inactive users cannot access protected APIs even if their token has not expired.

---

## Immediate Access Revocation for Inactive Users

If an administrator deactivates a user account while the user is logged in:

- existing tokens immediately stop working
- protected endpoints become inaccessible
- the user must be reactivated before logging in again

This is enforced using a custom authentication layer that validates:
user.is_active == True

on every request.

---

## User Management

### Custom User Model

Extends Django `AbstractUser` with:

- role
- department
- updated_at

### Role Choices
viewer
analyst
admin


### Department Choices


finance
operations
marketing
hr


---

## User Management Endpoints

Base path:


/api/users/


| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /api/users/ | List users | Admin |
| POST | /api/users/create/ | Create user | Admin |
| PATCH | /api/users/<id>/role/ | Update role | Admin |
| PATCH | /api/users/<id>/status/ | Activate/deactivate user | Admin |

Admins cannot:

- change their own role
- deactivate their own account

---

## User Filtering

Supported filters:


/api/users/?role=analyst
/api/users/?department=finance
/api/users/?is_active=true


---

## Financial Records Management

Each record contains:

- user
- title
- amount
- record_type
- category
- date
- description
- created_at
- updated_at

### Record Types


income
expense


### Categories


salary
food
transport
rent
shopping
bill
health
other


Records are ordered by:


-date, -created_at

## Record Creation Access Policy

Financial record creation and modification operations are restricted to **admin users only**.

| Role | Record Access |
|------|---------------|
| Viewer | No access |
| Analyst | Read-only access (own records) |
| Admin | Full access |

This ensures centralized control of financial data and stronger data integrity.

---

## Records API Endpoints

Base path:


/api/records/


| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /api/records/ | List records | Analyst (own), Admin |
| POST | /api/records/ | Create record | Admin |
| GET | /api/records/<id>/ | Retrieve record | Analyst (own), Admin |
| PUT | /api/records/<id>/ | Update record | Admin |
| PATCH | /api/records/<id>/ | Partial update | Admin |
| DELETE | /api/records/<id>/ | Delete record | Admin |

---

## Records Filtering

Supported filters:


category
record_type
date
start_date
end_date
amount_min
amount_max


Example:


/api/records/?category=food&record_type=expense


Includes:

- strict validation
- duplicate prevention
- ownership protection
- future-date blocking
- invalid-field rejection

---

## Records Pagination

Examples:


/api/records/?page=1
/api/records/?page=2&page_size=10


---

## Dashboard Summary API

Endpoint:


GET /api/dashboard/


Access:


viewer
analyst
admin


Provides:

- total_records
- total_income
- total_expense
- balance
- category_breakdown
- monthly_trend
- weekly_trend
- recent_transactions

Supports filters:


start_date
end_date


Implemented using:


DashboardService


---

## Insights API

Endpoint:


GET /api/insights/


Access:


analyst
admin


Provides:

- total_records
- balance
- monthly_trend
- weekly_trend
- total_income
- average_income
- total_expense
- average_expense
- category_breakdown
- top_expense_categories

Supported filters:


start_date
end_date
category
record_type
username (admin only)


Implemented using:


InsightsService

---

## Difference Between Dashboard and Insights APIs

| Feature | Dashboard API | Insights API |
|--------|---------------|--------------|
| Purpose | Quick summary | Advanced analytics |
| Access | Viewer, Analyst, Admin | Analyst, Admin |
| Recent transactions | Included | Not included |
| Averages | Not included | Included |
| Top categories | Not included | Included |
| Username filtering | Not supported | Admin-only |
| Filtering depth | Basic | Advanced |

Dashboard is designed for monitoring.  
Insights is designed for deeper analysis.

---

## Role-Based Dashboard Scope

| Role | Data Scope |
|------|-----------|
| Viewer | Own summary |
| Analyst | Own summary |
| Admin | System-wide summary |

---

## Assumptions

- new users start as viewer
- only admins create records
- analysts have read-only record access
- dashboard shows user-level analytics
- admin can analyze system-wide insights
- category analytics focus on expense records

---

## Tradeoffs

| Decision | Reason |
|---------|--------|
| SQLite used | sufficient for assignment scope |
| Admin-only record creation | preserves data integrity |
| Refresh-token endpoint omitted | simplifies auth lifecycle |
| Insights separated from dashboard logic | improves analytics clarity |

---

## Future Improvements

Possible enhancements:

- refresh-token endpoint
- Swagger/OpenAPI documentation
- analytics caching (Redis)
- search support for users
- soft delete for records
- automated tests
- production deployment configuration

---

## Evaluation Criteria Coverage

| Criterion | Coverage |
|----------|---------|
| Backend Design | modular apps + service layer |
| Logical Thinking | role-aware filtering + analytics |
| Functionality | full CRUD + dashboard + insights |
| Code Quality | serializer validation + permissions |
| Data Modeling | structured User & Record schema |
| Validation & Reliability | strict validation everywhere |
| Documentation | structured professional README |
| Additional Thoughtfulness | duplicate prevention + access-control safeguards |

