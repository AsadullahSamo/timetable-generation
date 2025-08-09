# 🗓️ Automated Timetable Generation System

A web-based, AI-powered class scheduling platform that automates the creation of conflict-free, optimized academic timetables. Built using **Next.js** and **Django REST**, the system leverages a custom **genetic algorithm** to generate schedules while adhering to over 18 real-world academic and infrastructure constraints.

---

## 🚀 Key Features

### 🔄 AI-Powered Timetable Generation

* Genetic algorithm-based optimization
* Real-time generation with progress tracking
* Generates compact, practical, and conflict-free schedules

### 📋 Comprehensive Constraint Management

* Handles academic, infrastructure, and institutional rules
* Avoids common conflicts like teacher overlaps or double-booked rooms
* Ensures practical classes are in labs, with consistent room usage

### 🧠 Intelligent Scheduling Logic

* Smart teacher-subject matching
* Friday-aware scheduling (early dismissal rules)
* Reserved thesis days for final-year students
* Distribution of sessions across all weekdays

### 🏫 Room & Lab Allocation

* Enforces “same-lab” rule for practical blocks
* Guarantees no room overlap and lab-only allocation for practicals
* Adaptive assignment for senior batches with flexible lab preferences

### 🔐 User Management & Auth

* Firebase Authentication integration
* Multi-user access for administrators, faculty, and staff

### 📤 Export & Accessibility

* Export generated timetables in multiple formats (PDF, Excel, etc.)
* Mobile-friendly, responsive UI for on-the-go access

---

## ⚙️ Constraint Highlights

> The system currently respects **18+ academic and room constraints**, including:

#### Academic & Scheduling

1. Subject-wise frequency per week (based on credit hours)
2. 3-hour practical blocks (auto-grouped)
3. No duplicate theory classes of the same subject per day
4. Minimum number of classes per day enforced
5. Thesis scheduling on Wednesdays (final year only)
6. Intelligent subject-teacher mapping
7. Avoids scheduling classes beyond institutional working hours (8AM–3PM)

#### Room Allocation

8. No room overlaps or double-bookings
9. Same-lab rule for practical subjects
10. Practical subjects scheduled **only** in lab rooms
11. Room consistency for theory classes
12. Flexible room usage for senior batches (labs preferred)

#### Conflict Prevention

13. No teacher overlaps across classes
14. Cross-semester conflict detection
15. Section-level conflict prevention
16. Friday constraints (earlier cutoff for classes)
17. Compact and student-friendly scheduling
18. Balanced subject distribution throughout the week

✅ All constraints have been successfully implemented and tested in real-time use cases.

---

## 🛠️ Tech Stack

### Frontend

* **Next.js 15.1.4**
* **Tailwind CSS** for UI styling
* **Axios** for API communication
* **Font Awesome** for icons

### Backend

* **Django 4.2.7** with Django REST Framework
* **Celery** for asynchronous task processing
* **JWT** for secure API authentication
* **SQLite** (default DB, can scale to PostgreSQL/MySQL)

### Infrastructure

* **Firebase Authentication** for user login and management
* **Docker-ready** backend for easy deployment

---

## 📦 Getting Started

### Prerequisites

* Python 3.8+
* Node.js 16+

### Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/timetable-gen.git
cd timetable-gen
```

2. **Install Backend Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**

```bash
cd frontend
npm install
```

4. **Set Environment Variables**
   Create `.env` files for both backend and frontend with required Firebase and Django secrets.

5. **Run the App**

```bash
# Start backend
cd backend
python manage.py runserver

# Start frontend
cd frontend
npm run dev
```

---

## 🧪 Development Notes

* Modular architecture with separation between UI, API, and scheduling logic
* Easily extendable for additional constraints or calendar export formats
* Supports real-time progress updates during timetable generation

---

## 🧠 Use Case

This system solves the tedious, error-prone, and time-consuming process of manually creating academic timetables. It’s designed for colleges, universities, and institutions looking to automate scheduling while retaining full control over educational and infrastructure constraints.

---

## 📄 License

MIT License — open to contributions and customization for institutional use.

---

Let me know if you want a **multi-institute version description**, **deployment instructions**, or a short version for a GitHub profile summary!
