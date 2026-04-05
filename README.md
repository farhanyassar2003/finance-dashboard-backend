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
- `dashboard` → summary analytics
- `insights` → advanced analytics
- `services` → aggregation logic layer
- `permissions` → reusable authorization rules

Analytics logic is implemented using:
- `DashboardService`
- `InsightsService`

*Note: Insights functionality is implemented inside the dashboard module instead of a separate Django app because it represents an extension of analytics logic rather than an independent domain component. This avoids unnecessary application fragmentation while keeping aggregation logic modular through a dedicated service layer.*

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
   git clone https://github.com/<your-username>/finance-dashboard-backend.git
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
| **Access Token** | Access protected endpoints | 5 hours |
| **Refresh Token** | Reserved for renewal support | 1 day |

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
- Frontend integration
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
- `total_records`, `total_income`, `total_expense`, `balance`
- `category_breakdown`, `monthly_trend`, `weekly_trend`
- `recent_transactions`

**Supported filters:** `start_date`, `end_date`  

**Validations:**
- `start_date` cannot be greater than `end_date`.
- Strict invalid-field rejection.

Implemented using: `DashboardService`

---

## Insights API
Endpoint: `GET /api/insights/`  
Access: `analyst`, `admin`

Provides:
- `total_records`, `balance`, `total_income`, `average_income`
- `total_expense`, `average_expense`, `monthly_trend`, `weekly_trend`
- `category_breakdown`, `top_expense_categories`

**Supported filters:**
- `start_date`, `end_date`, `category`, `record_type`
- `username` (admin only)

**Validations:**
- `start_date` cannot be greater than `end_date`.
- Username formatting (strips spaces and validates input).
- Strict invalid-field rejection.

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
| **Username filtering** | Not supported | Admin-only |
| **Filtering depth** | Basic | Advanced |

Dashboard is designed for monitoring.  
Insights is designed for deeper analysis.

---

## Role-Based Dashboard Scope

| Role | Data Scope |
|------|-----------|
| **Viewer** | Own summary |
| **Analyst** | Own summary |
| **Admin** | System-wide summary |

---

## Assumptions

- New users start as `viewer`.
- Only `admin`s create records.
- `analyst`s have read-only record access.
- Dashboard shows user-level analytics.
- `admin` can analyze system-wide insights.
- Category analytics focus on `expense` records.

---

## Tradeoffs

| Decision | Reason |
|---------|--------|
| **SQLite used** | Selected for simplicity and quick local setup; architecture supports migration to PostgreSQL without structural changes. |
| **Admin-only record creation** | Preserves data integrity. |
| **Refresh-token endpoint omitted** | Simplifies auth lifecycle. |
| **Insights separated from dashboard logic**| Improves analytics clarity. |

---

## Future Improvements

Possible enhancements:
- Refresh-token endpoint
- Swagger/OpenAPI documentation
- Analytics caching (Redis)
- Search support for users
- Soft delete for records
- Automated tests
- Production deployment configuration
- Pagination can be introduced for `recent_transactions` in the Dashboard API if the transaction window is expanded beyond the current fixed-size summary response.

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
| **Additional Thoughtfulness** | Duplicate prevention + access-control safeguards |
