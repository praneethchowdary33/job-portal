# Job Portal

A full-stack job portal built with Django where recruiters post jobs and job seekers search, filter and apply with their resume.

## Features

- Role-based authentication: Job Seeker and Recruiter
- Recruiters: post jobs, view applicants, view resumes, mark Shortlisted / Rejected
- Job Seekers: search jobs by role, skill and location, apply with resume upload, track application status
- Job detail pages, recruiter dashboard, admin panel

## Tech Stack

- Backend: Python, Django
- Frontend: HTML, Bootstrap 5 (Django templates)
- Database: SQLite

## Setup

```bash
git clone https://github.com/praneethchowdary33/job-portal.git
cd job-portal
python -m venv venv
venv\Scripts\activate
pip install django pillow
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000

## Usage

1. Register as a Recruiter and post a job.
2. Register as a Job Seeker, open the job and apply with a PDF resume.
3. Log in as the Recruiter, open Dashboard, view applicants and update status.

## Screenshots

(Add screenshots here)

## Author

Kovuru Praneeth