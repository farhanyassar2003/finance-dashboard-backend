# Finance Dashboard Backend

## Overview

This project implements a role-based backend system for managing financial records and generating analytical summaries for dashboard-style applications.

The system provides:

- Secure user registration and authentication using JWT
- Role-based access control (Viewer, Analyst, Admin)
- Financial record management with filtering and validation
- Dashboard summary analytics
- Advanced insights analytics
- Administrator-controlled user management
- Service-layer-based aggregation architecture

The implementation focuses on correctness, maintainability, structured validation, and secure backend authorization.

---

## Key Features

### Authentication & Authorization

- JWT-based authentication (SimpleJWT)
- Strong password validation policy
- Inactive-user login blocking
- Immediate access revocation after account deactivation
- Restricted role assignment during registration
- Admin-controlled role updates

---

## Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Viewer** | Dashboard access only |
| **Analyst** | Dashboard + records read + insights |
| **Admin** | Full system access |

Access rules are enforced using reusable permission classes.

---

## Architecture Overview

The backend follows a modular app-based architecture:

- `authentication` → login & registration
- `users` → role management
- `records` → financial CRUD operations
- `dashboard` → summary analytics and insights analytics
- `services` → aggregation logic layer
- `permissions` → reusable authorization rules

Analytics logic is implemented using:
- `DashboardService`
- `InsightsService`

*Note: Insights functionality is implemented inside the dashboard module instead of a separate Django app because it represents an extension of analytics logic rather than an independent domain component.*

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python |
| **Framework** | Django |
| **API Layer** | Django REST Framework |
| **Authentication** | JWT (SimpleJWT) |
| **Database** | SQLite |
| **Authorization** | Custom permission classes |
| **Validation** | Serializer-based validation |

---

## Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/farhanyassar2003/finance-dashboard-backend
   cd finance-dashboard-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

---

## Authentication Flow

### Register User
`POST /api/register/`

**Validations:**
- First and last names must contain only letters.
- Username must be alphanumeric with underscores, between 4-150 characters.
- Username and email uniqueness checks.
- Strong password policy: Minimum 8 characters, at least one uppercase, one lowercase, one number, and one special character. No spaces allowed.
- Password mismatch rejection.
- Role and department assignment blocked during registration.
- Strict invalid-field rejection.

New users are assigned the default role: `viewer`.
Role assignment can only be modified through admin APIs.

### Login
`POST /api/login/`

**Validations:**
- Username and password are required.
- Strict invalid-field rejection.
- Validates user existence and password correctness.
- Inactive-user login blocking.

Returns:
- user details
- access token
- refresh token

Use the token in headers:
```http
Authorization: Bearer <access_token>
```

---

## JWT Token Lifecycle

| Token | Purpose | Lifetime |
|------|---------|----------|
| **Access Token** | Access protected endpoints | 15 minutes |
| **Refresh Token** | Used to generate a new access token without re-login | 7 day |

A refresh endpoint is available:

`POST /api/token/refresh/`

This endpoint accepts a refresh token and returns a new access token when the previous access token expires.

Inactive users cannot access protected APIs even if their token has not expired.

---

## Immediate Access Revocation for Inactive Users

If an administrator deactivates a user account while the user is logged in:
- Existing tokens immediately stop working
- Protected endpoints become inaccessible
- The user must be reactivated before logging in again

This is enforced using a custom authentication layer that validates `user.is_active == True` on every request.

---

## Global Exception Handling

The project uses a centralized global exception handling mechanism to ensure consistent error responses across all API endpoints.

A custom exception handler is used to process:
- Validation errors
- Authentication failures
- Permission errors
- Object-not-found errors
- Unexpected server exceptions

Instead of returning default framework error responses, the system returns a standardized response structure:

```json
{
  "message": "Request failed.",
  "errors": {
    "detail": "You do not have permission to perform this action."
  }
}
```

For validation errors, field-level details are returned inside the `errors` object:

```json
{
  "message": "Request failed.",
  "errors": {
    "username": ["This field may not be blank."]
  }
}
```

This improves:
- API response consistency
- Frontend integrations
- Debugging clarity
- Maintainability
- Separation of concerns

---

## User Management

### Custom User Model
Extends Django `AbstractUser` with:
- `role`
- `department`
- `updated_at`

**Role Choices:** `viewer`, `analyst`, `admin`  
**Department Choices:** `finance`, `operations`, `marketing`, `hr`

### Role Assignment Rules

The system follows a strict role-based access control (RBAC) structure:

- Users registered through the public registration endpoint are automatically assigned the default role `viewer`.
- Only administrators can promote users to `analyst` or `admin` using dedicated role-management APIs.
- Superusers created using Django’s `createsuperuser` command are automatically assigned the `admin` role to maintain consistency with the system’s access control design.

This ensures predictable privilege control and prevents unauthorized role escalation during registration.

### User Management Endpoints
Base path: `/api/users/`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/users/` | List users | Admin |
| `POST` | `/api/users/create/` | Create user | Admin |
| `PATCH` | `/api/users/<id>/role/` | Update role | Admin |
| `PATCH` | `/api/users/<id>/status/` | Activate/deactivate user | Admin |

*Note: Admins cannot change their own role or deactivate their own account.*

### User Filtering
Supported filters: `role`, `department`, `is_active`, `username`

Examples:
- `/api/users/?role=analyst`
- `/api/users/?department=finance`
- `/api/users/?is_active=true`
- `/api/users/?username=john`

### User Validations
- First name and last name must contain only letters if provided.
- Username must be at least 4 characters long.
- Duplicate username and email prevention.
- Strong password policy: Must contain uppercase, lowercase, number, special character, and no spaces.
- Passwords mismatch rejection.
- Admin role restriction: Admins cannot change their own role or deactivate their own account.
- Strict invalid-field rejection.

---

## Financial Records Management

Each record contains:
`user`, `title`, `amount`, `record_type`, `category`, `date`, `description`, `created_at`, `updated_at`

**Record Types:** `income`, `expense`  
**Categories:** `salary`, `food`, `transport`, `rent`, `shopping`, `bill`, `health`, `other`  
**Ordering:** `-date`, `-created_at`

### Record Creation Access Policy

Financial record creation and modification operations are restricted to **admin users only**.

| Role | Record Access |
|------|---------------|
| **Viewer** | No access |
| **Analyst** | Read-only access (own records) |
| **Admin** | Full access |

This ensures centralized control of financial data and stronger data integrity.

### Records API Endpoints
Base path: `/api/records/`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/records/` | List records | Analyst (own), Admin |
| `POST` | `/api/records/` | Create record | Admin |
| `GET` | `/api/records/<id>/` | Retrieve record | Analyst (own), Admin |
| `PUT` | `/api/records/<id>/` | Update record | Admin |
| `PATCH`| `/api/records/<id>/` | Partial update | Admin |
| `DELETE`| `/api/records/<id>/` | Delete record | Admin |

### Records Filtering
Supported filters: `category`, `record_type`, `date`, `start_date`, `end_date`, `amount_min`, `amount_max`

Example: `/api/records/?category=food&record_type=expense`

### Records Validations
- **Title**: Cannot be empty.
- **Amount**: Must be greater than 0.
- **Date**: Future-date blocking (cannot be in the future).
- **Ownership protection**: Changing record ownership is not allowed. Read-only fields cannot be altered.
- **Duplicate prevention**: Cannot create duplicate records with the exact same details for a user.
- **Admin-only creation**: Requires target user `username` which must exist.
- **Filter validation**: `start_date` <= `end_date`, `amount_min` / `max` >= 0, `amount_min` <= `amount_max`.
- **Invalid-field rejection**: Strict validation rejecting any unallowed parameters.

---

## Pagination Support

Pagination is implemented using a reusable `StandardPagination` class shared across list endpoints.

Pagination is currently applied to:
- `/api/records/`
- `/api/users/`

Supported query parameters:
- `?page=1`
- `?page_size=10`

Examples:
- `/api/records/?page=2&page_size=10`
- `/api/users/?role=analyst&page=1`

---

## Dashboard Summary API
Endpoint: `GET /api/dashboard/`  
Access: `viewer`, `analyst`, `admin`

Provides:
- `total_records` (number of records in the filtered dataset)
- `total_income` (sum of income records)
- `total_expense` (sum of expense records)
- `balance` (total_income − total_expense)
- `category_breakdown`, `monthly_trend`, `weekly_trend`
- `recent_transactions` (latest 5 transactions ordered by date)

**Supported filters:** `start_date`, `end_date`, `username`(admin only)


## Role-Based Dashboard Scope

| Role | Data Scope |
|------|-----------|
| **Viewer** | Own summary |
| **Analyst** | Own summary |
| **Admin** | System-wide summary |

**Validations:**
- `start_date` cannot be greater than `end_date`
- strict invalid-field rejection

Implemented using: `DashboardService`

---

## Insights API
Endpoint: `GET /api/insights/`  
Access: `analyst`, `admin`

Provides:
- `total_records` (number of records in the filtered dataset)
- `balance` (total_income − total_expense)
- `total_income` (sum of income records)
- `average_income` (average value of income records)
- `total_expense` (sum of expense records)
- `average_expense` (average value of expense records)
- `monthly_trend`, `weekly_trend`
- `category_breakdown` (expense category distribution)
- `top_expense_categories` (top expense categories by total amount)

**Supported filters:** `start_date`, `end_date`, `category`, `record_type`, `username` (admin only)


## Role-Based Insights Scope

| Role | Data Scope |
|------|-----------|
| **Analyst** | Own insights summary |
| **Admin** | System-wide insights summary |

**Validations:**
- `start_date` cannot be greater than `end_date`
- username formatting (trims extra spaces before validation)
- strict invalid-field rejection

Implemented using: `InsightsService`

---

## Difference Between Dashboard and Insights APIs

| Feature | Dashboard API | Insights API |
|--------|---------------|--------------|
| **Purpose** | Quick summary | Advanced analytics |
| **Access** | Viewer, Analyst, Admin | Analyst, Admin |
| **Recent transactions**| Included | Not included |
| **Averages** | Not included | Included |
| **Top categories** | Not included | Included |
| **Username filtering** | Admin-only | Admin-only |
| **Filtering depth** | Basic | Advanced |

Dashboard is designed for monitoring overall financial activity at a glance.  
Insights is designed for deeper analytical exploration of financial patterns and trends.

---

## Assumptions

- New users start as `viewer`.
- Only `admin`s create records.
- `Analyst`s have read-only record access.
- Dashboard shows user-level analytics.
- `admin` can analyze system-wide insights.
- Category analytics focus on `expense` records.

---

## Tradeoffs

| Decision | Reason |
|---------|--------|
| **SQLite used** | Selected for simplicity and quick local setup; the architecture supports migration to PostgreSQL without major structural changes. |
| **Admin-only record creation and modification** | Improves financial data integrity, though it reduces flexibility for non-admin users. |
| **JWT refresh support using SimpleJWT** | Improves session continuity for users, while adding a small amount of authentication flow complexity. |
| **Insights separated from dashboard logic** | Avoids unnecessary Django app fragmentation while still keeping analytics logic modular through a dedicated service layer. |

---

## Additional Thoughtfulness

The backend includes several design decisions beyond the core assignment requirements to improve reliability, security, and analytical clarity:

- Duplicate financial record prevention to maintain data consistency
- Ownership protection preventing reassignment of records between users
- Immediate access revocation for inactive users even if JWT tokens are still valid using a custom authentication layer
- Centralized global exception handling for consistent API error responses
- Strict invalid-field rejection across filtering endpoints
- Reusable global pagination system implemented via StandardPagination for consistent list responses
- Custom JWT authentication extension (`authentication.py`) to enforce real-time user active-status validation
- Service-layer-based analytics architecture using DashboardService and InsightsService
- Expense-focused category analytics aligned with real-world financial dashboards
- Clear separation between Dashboard (summary monitoring) and Insights (advanced analytics exploration) APIs

---

## Future Improvements

Possible enhancements:
- Swagger/OpenAPI documentation
- Analytics caching (Redis)
- Search support for users
- Soft delete for records
- Automated tests
- Production deployment configuration
- Pagination can be introduced for `recent_transactions` in the Dashboard API if the transaction window is expanded beyond the current fixed-size summary response.
- Add API versioning support (e.g., /api/v1/) for backward compatibility
- Introduce background task processing (e.g., Celery) for scalable analytics computation
- Add database indexing on frequently filtered fields such as date, category, and record_type to improve query performance

---

## Evaluation Criteria Coverage

| Criterion | Coverage |
|----------|---------|
| **Backend Design** | Modular apps + service layer |
| **Logical Thinking** | Role-aware filtering + analytics |
| **Functionality** | Full CRUD + dashboard + insights |
| **Code Quality** | Serializer validation + permissions |
| **Data Modeling** | Structured User & Record schema |
| **Validation & Reliability** | Strict validation everywhere |
| **Documentation** | Structured professional README |
| **Additional Thoughtfulness** | Duplicate prevention + inactive-user access blocking + service-layer analytics + global pagination |
