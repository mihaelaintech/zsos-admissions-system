# ZSOS Internal Admissions Management System

## Overview

This project presents the design and implementation of an Internal Admissions Management System developed for ZSOS as part of an MSc consultancy project.

The system addresses inefficiencies in the current admissions workflow, where student data is captured through fragmented communication channels and manually re-entered into external systems. The developed solution introduces a centralised internal platform to improve workflow efficiency, data consistency, and operational visibility.

---

## Objectives

- Analyse the existing admissions workflow and identify inefficiencies  
- Design and implement a structured admissions management system  
- Reduce manual data handling and duplication  
- Improve applicant tracking and workflow visibility  
- Evaluate system performance using simulated scenarios  

---

## Key Features

### User Management
- Student registration and login  
- Staff login with role-based access  
- Role differentiation: Manager and Student Adviser  

### Applicant Management
- Add, edit, delete applicants  
- View detailed applicant profiles  
- Assign ownership of applicants to staff  

### Workflow Pipeline
- Structured status progression:
  - New Lead  
  - Documents Received  
  - Documents Verified  
  - Interview Scheduled  
  - Application Submitted  
  - Offer Received  

### Document Tracking
- Track document submission:
  - CV  
  - Passport  
  - Transcript  
  - Personal Statement  

### Dashboard & Reporting
- Overview of total applicants  
- Status distribution  
- Pending documents tracking  

### Data Validation
- Structured form inputs  
- Required field validation  
- Improved data consistency  

---

## Technologies Used

- **Backend:** Python (Flask)  
- **Database:** SQLite  
- **Frontend:** HTML, CSS, Jinja Templates  
- **Version Control:** Git & GitHub  

---

## System Architecture

The system follows a simple web application architecture:

- Flask backend handling routes and logic  
- SQLite database storing user and applicant data  
- HTML templates rendered using Jinja  
- Static assets (CSS, images) for UI design  

---

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/mihaelaintech/zsos-admissions-system.git
