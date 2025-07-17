# Timetable Generation System

A comprehensive web-based timetable generation system built with Django REST API backend and Next.js frontend. This system uses advanced genetic algorithms to automatically generate optimal class schedules while respecting various constraints.

## Features

- **Advanced Timetable Generation**: Uses genetic algorithms to create optimal schedules
- **Constraint Management**: Supports teacher availability, classroom assignments, and subject requirements
- **Real-time Generation**: Fast and efficient timetable generation with progress tracking
- **Responsive UI**: Modern, user-friendly interface built with Next.js
- **RESTful API**: Clean Django REST API for all operations
- **Multi-user Support**: Firebase authentication integration
- **Export Capabilities**: Generate and export timetables in various formats

## Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Django REST Framework**: API development
- **SQLite**: Database (can be easily migrated to PostgreSQL/MySQL)
- **Celery**: Background task processing
- **JWT**: Authentication

### Frontend
- **Next.js 15.1.4**: React framework
- **Tailwind CSS**: Styling
- **Font Awesome**: Icons
- **Axios**: HTTP client

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd django-backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Start the backend server:**
   ```bash
   python manage.py runserver 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Usage

### 1. School Configuration
- Set up school details, working days, and time periods
- Configure lesson duration and break times

### 2. Add Data
- **Subjects**: Add courses with credit hours and practical indicators
- **Teachers**: Assign teachers to subjects with availability constraints
- **Classrooms**: Add classrooms and labs with capacity
- **Class Groups**: Create student groups for scheduling

### 3. Generate Timetable
- Navigate to the Constraints page
- Set any additional constraints (optional)
- Click "Generate Timetable" to create an optimal schedule
- View the generated timetable on the Timetable page

## API Endpoints

### Core Endpoints
- `GET /api/timetable/` - List all timetables
- `GET /api/timetable/latest/` - Get latest timetable
- `POST /api/timetable/generate-timetable/` - Generate new timetable
- `GET /api/timetable/subjects/` - List subjects
- `GET /api/timetable/teachers/` - List teachers
- `GET /api/timetable/classrooms/` - List classrooms
- `GET /api/timetable/class-groups/` - List class groups

### Configuration Endpoints
- `GET /api/timetable/configs/` - List schedule configurations
- `POST /api/timetable/configs/` - Create schedule configuration

## Project Structure

```
timetable-generation-master/
├── django-backend/          # Django backend
│   ├── backend/            # Django project
│   │   ├── timetable/      # Main app
│   │   │   ├── algorithms/ # Scheduling algorithms
│   │   │   ├── models.py   # Database models
│   │   │   ├── views.py    # API views
│   │   │   └── serializers.py
│   │   └── users/          # User management
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── pages/             # Next.js pages
│   │   ├── components/    # React components
│   │   └── utils/         # Utility functions
│   └── package.json
└── README.md
```

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

## Deployment

### Backend Deployment
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Use Gunicorn or uWSGI for production

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or any static hosting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team. 