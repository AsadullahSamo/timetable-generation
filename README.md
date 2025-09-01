# 🗓️ Automated Timetable G### 🏫 Room & Lab Allocation

* Enforces "same-lab" rule for practical blocks
* Guarantees no room overlap and lab-only allocation for practicals
* Enhanced room consistency for theory/practical separationtion System

A web-based class scheduling platform that automates the creation of conflict-free, optimized academic timetables. Built using **Next.js** and **Django REST Framework**, the system leverages a custom constraint-based algorithm to generate schedules while adhering to 19 real-world academic and infrastructure constraints.

---

## 🚀 Key Features

### 🔄 Advanced Timetable Generation

* Constraint-based optimization algorithm
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

* Export generated timetables in PDF format using jsPDF
* Mobile-friendly, responsive UI for on-the-go access

---

## ⚙️ Constraint Highlights

> The system respects **19 academic and room constraints**, including:

#### Academic & Scheduling

1. Subject Frequency - Correct number of classes per week based on credit hours
2. Practical Blocks - 3-hour consecutive blocks for practical subjects
3. No Duplicate Theory Per Day - No section can have multiple theory classes of the same subject on the same day
4. Minimum Daily Classes - No day has only practical or only one class
5. Thesis Day - Wednesday is exclusively reserved for Thesis subjects for final year students
6. Intelligent Teacher Assignment - Matches teachers to their assigned subjects
7. Working Hours - All classes are within 8:00 AM to 3:00 PM
8. Same Theory Subject Distribution - Max 1 class per day, distributed across 5 weekdays
9. Teacher Unavailability - Teachers cannot be scheduled during their unavailable periods (hard constraint)

#### Room Allocation

10. No Room Conflicts - Rooms cannot be double-booked
11. Same Lab Rule - All 3 blocks of practical subjects must use the same lab
12. Practicals in Labs - Practical subjects must be scheduled only in laboratory rooms
13. Room Consistency - Consistent room assignment for theory classes per section

#### Conflict Prevention

14. No Teacher Overlap - Teachers cannot be in multiple places at once
15. Cross-Semester Conflict Detection - Prevents scheduling conflicts across batches
16. Section Conflicts - Prevents multiple simultaneous classes for same section
17. Friday Time Limits - Classes must not exceed 12:00/1:00 PM with practical, 11:00 AM without practical
18. Compact Scheduling - Classes wrap up quickly while respecting Friday constraints
19. Appropriate Distribution - Classes are spread across all 5 days

✅ All constraints have been successfully implemented and tested in real-time use cases.

---

## 🛠️ Tech Stack

### Frontend

* **Next.js 15.1.4**
* **React 19.1.0**
* **Tailwind CSS** for UI styling
* **Axios** for API communication
* **MUI Icons** and **React Icons** for UI elements
* **jsPDF** and **jspdf-autotable** for PDF exports

### Backend

* **Django 4.2.7** with Django REST Framework 3.14.0
* **JWT** (djangorestframework-simplejwt) for secure API authentication
* **SQLite** database

### Development Tools

* **ESLint 9** for code quality
* **Turbopack** for faster development builds

---

## 📦 Getting Started

### Prerequisites

* Python 3.8+
* Node.js 16+

### Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/AsadullahSamo/timetable-generation.git
cd timetable-generation
```

2. **Install Backend Dependencies**

```bash
cd django-backend
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
# Start both backend and frontend concurrently
npm start

# Or start individually:
npm run start:backend
npm run start:frontend
```

---

## 🧪 Development Notes

* Modular architecture with separation between UI, API, and scheduling logic
* Enhanced constraint validator and resolver for complex scheduling requirements
* Supports multiple user roles and access controls

---

## 🧠 Use Case

This system solves the tedious, error-prone, and time-consuming process of manually creating academic timetables. It’s designed for colleges, universities, and institutions looking to automate scheduling while retaining full control over educational and infrastructure constraints.

---

## 🧠 Use Case

This system solves the tedious, error-prone, and time-consuming process of manually creating academic timetables. It's designed for colleges, universities, and institutions looking to automate scheduling while retaining full control over educational and infrastructure constraints.
