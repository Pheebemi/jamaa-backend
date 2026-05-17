# Jamaa Backend

> REST API for the Jamaa Offline-First AI Case Management Platform
> Built with Django REST Framework — deployed on PythonAnywhere

**Live API:** https://jamaa.pythonanywhere.com/api  
**Admin Panel:** https://jamaa.pythonanywhere.com/admin

---

## Overview

This is the server-side component of Jamaa — an open-source humanitarian case management platform built for West Africa. The backend handles:

- JWT authentication with role-based access control
- Offline sync (push/pull) for mobile devices
- AI case analysis via Google Gemini (background threaded, non-blocking)
- Emergency alert broadcasting
- Organisation-scoped data isolation

---

## Tech Stack

| Concern | Technology |
|---|---|
| Framework | Django 5.x + Django REST Framework |
| Authentication | djangorestframework-simplejwt |
| Database | SQLite (development) → PostgreSQL (production) |
| AI | Google Gemini 2.0 Flash |
| CORS | django-cors-headers |
| Deployment | PythonAnywhere |

---

## Getting Started

### Prerequisites
- Python 3.12+
- pip

### Installation

```bash
git clone https://github.com/Pheebemi/jamaa-backend.git
cd jamaa-backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your-gemini-api-key
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=30
```

### Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login/` | Login — returns access + refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current user profile |
| POST | `/api/auth/logout/` | Logout |

### Cases

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cases/` | List cases (org-scoped) |
| POST | `/api/cases/` | Create case |
| GET | `/api/cases/{id}/` | Case detail |
| PATCH | `/api/cases/{id}/` | Update case |

### Sync

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/sync/push/` | Push pending local records to server |
| GET | `/api/sync/pull/?last_sync={timestamp}` | Pull server changes since timestamp |

### Alerts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/alerts/` | List alerts for user's organisation |
| POST | `/api/alerts/broadcast/` | Broadcast alert (org_admin+ only) |

---

## Sync Protocol

### Push
The mobile app sends all locally modified records in a single request:

```json
{
  "cases": [
    {
      "local_id": "local-uuid",
      "server_id": null,
      "updated_at": "2026-05-13T12:00:00Z",
      "data": { ... }
    }
  ],
  "notes": [ ... ]
}
```

Response:
```json
{
  "created": [{ "local_id": "...", "server_id": "..." }],
  "updated": [],
  "conflicts": []
}
```

### Pull
Returns all records updated since the given timestamp, scoped to the user's organisation:

```json
{
  "cases": [ ... ],
  "notes": [ ... ],
  "alerts": [ ... ],
  "server_time": "2026-05-13T12:05:00.000000Z"
}
```

---

## AI Integration

After a case is created via sync, AI analysis runs automatically in a background thread (no Celery required):

```python
import threading
t = threading.Thread(target=analyze_case, args=(case_id,), daemon=True)
t.start()
```

Gemini 2.0 Flash analyzes the case and populates:
- `ai_summary` — plain English summary
- `ai_category` — classification
- `ai_priority` — risk level
- `ai_urgency_score` — 1 to 10
- `ai_suggested_action` — one actionable sentence

Sensitive cases (`is_sensitive=True`) are never sent to the AI — only case type and priority are analyzed.

---

## Data Models

### Organisation
```
id, name, type (ngo/school/clinic/government), country, created_at
```

### Case
```
id, organisation, title, description, type, priority, status,
assigned_to, created_by, is_sensitive, location_lat, location_lng,
ai_summary, ai_category, ai_priority, ai_urgency_score, ai_suggested_action,
created_at, updated_at, deleted_at
```

### User
```
id, email, name, role, organisation, created_at
```

### Alert
```
id, organisation, type, message, sent_by, created_at
```

### AuditLog
```
id, user, case, action, ip_address, timestamp
```
Every access to a sensitive case is recorded here.

---

## User Roles & Permissions

| Role | Cases | Sensitive Cases | Alerts | Dashboard |
|---|---|---|---|---|
| `super_admin` | All orgs | ✅ | Broadcast | All orgs |
| `org_admin` | Own org | ✅ | Broadcast | Own org |
| `field_officer` | Own org | Only if assigned | View only | ❌ |
| `school_staff` | Own org | ❌ | View only | ❌ |
| `clinic_staff` | Own org | ❌ | View only | ❌ |

---

## Security

- All endpoints require JWT authentication
- Organisation-scoped queries — users can never access another org's data
- Sensitive cases require `org_admin` or explicit assignment to view
- Every sensitive case access is logged in `AuditLog`
- Tokens stored in mobile `expo-secure-store` — never in plain storage

---

## Deployment (PythonAnywhere)

```bash
git clone https://github.com/Pheebemi/jamaa-backend.git
cd jamaa-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Edit with your values
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Configure the WSGI file on PythonAnywhere:

```python
import os, sys
sys.path.insert(0, '/home/jamaa/jamaa-backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'jamaa.settings.production'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Add static files mapping in the Web tab:
- URL: `/static/`
- Directory: `/home/jamaa/jamaa-backend/staticfiles`

---

## Mobile Repository

The Expo React Native mobile app is available at:
**https://github.com/Pheebemi/jamaa-mobile**

---

## License

MIT — Open source, free to deploy by any school, clinic, NGO, or government.

---

*Jamaa — Because every community deserves a system that works.*
