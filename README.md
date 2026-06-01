# IT Helpdesk & Security Incident Tracker

🚀 **Live Demo:** [https://it-helpdesk-security-incident-tracker.onrender.com](https://it-helpdesk-security-incident-tracker.onrender.com)

An enterprise-grade Django application for logging IT support tickets and security breaches, strictly adhering to the NIST Incident Response Life Cycle.

## Features
- **NIST Life Cycle Compliance**: Tickets follow Preparation, Detection, Containment, Recovery, and Post-Incident stages.
- **Enterprise RBAC (Role-Based Access Control)**: 
  - Backend permissions are locked to three strict tiers (`MANAGER`, `RESPONDER`, `USER`).
  - Frontend Job Titles are completely dynamic (e.g., "Security Analyst", "IT Technician") allowing business flexibility without sacrificing system security.
- **Security & Forensics**:
  - `django-axes` for brute-force lockout protection.
  - `django-ratelimit` on ticket submission (API & UI).
  - Advanced Diff-Tracking Audit Logger for a strict **Chain of Custody** (Tracks precise field changes even if a ticket is deleted).
  - JWT Authentication for secure machine-to-machine monitoring.
- **Advanced Dashboard**: Interactive filters for ticket types, stages, priority, and real-time audit log parsing.
- **Cloud Ready**: Configured for Cloudinary (ephemeral-safe media storage) and WhiteNoise (static files).

## Tech Stack
- Django 5.x
- Django REST Framework + SimpleJWT
- TailwindCSS (Premium Glassmorphism UI)
- PostgreSQL (ready via `dj-database-url`)
- WhiteNoise & Cloudinary

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the root directory. Ensure `CLOUDINARY_URL` is set if deploying to Render's Free Tier.

3. **Database Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## API & External Integrations
- **Auth Token**: `POST /api/token/` (JWT)
- **SOC Metrics**: `GET /api/metrics/` (Live dashboard statistics)
> *Note: A custom `test_api.py` script is included in the root directory to instantly simulate and demonstrate the secure API connection for your panel.*

## Audit Logging
All authentication events and ticket modifications (including before/after diffs) are permanently burned into `audit.log` for strict compliance tracking.

## Admin Credentials
- **Username**: `admin`
- **Password**: `adminpassword123` (Change immediately in production)
