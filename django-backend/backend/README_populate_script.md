# Timetable Test Data Population Script

## Overview
The `populate_test_data.py` script automatically populates your timetable database with complete test data based on the 4 batch timetables from MUET Department of Software Engineering.

## Features
- ✅ **Complete Data Set**: All teachers, subjects, and assignments from 4 batches (21SW, 22SW, 23SW, 24SW)
- ✅ **Theory & Practical**: Both theory subjects and practical subjects with "Pr" suffix
- ✅ **Proper Assignments**: Teachers assigned exactly as per original timetables
- ✅ **Safe Operations**: Uses database transactions for data integrity
- ✅ **Comprehensive Validation**: Verifies all data after population
- ✅ **Flexible Usage**: Can add to existing data or clear and repopulate

## Usage

### Basic Usage (Add to existing data)
```bash
python populate_test_data.py
```

### Clear and Repopulate (WARNING: Deletes all existing data)
```bash
python populate_test_data.py --clear
```

### Help
```bash
python populate_test_data.py --help
```

## Data Included

### Batches Covered
1. **21SW (8th Semester - Final Year)**
   - SM, CC, SQE + CC Pr, SQE Pr

2. **22SW (6th Semester - 3rd Year)**
   - SPM, DS&A, MAD, DS, TSW + DS&A Pr, MAD Pr

3. **23SW (4th Semester - 2nd Year)**
   - IS, HCI, ABIS, SCD, SP + SCD Pr

4. **24SW (2nd Semester - 1st Year)**
   - DSA, OR, SRE, SEM, DBS + DSA Pr, DBS Pr

### Teachers (25 total)
- Dr. Areej Fatemah, Dr. Rabeea Jaffari, Dr. S. M. Shehram Shah, Dr. Sania Bhatti
- Dr. Mohsin Memon, Prof. Dr. Qasim Ali
- Mr. Aqib Ali, Mr. Arsalan, Mr. Mansoor Bhaagat, Mr. Naveen Kumar
- Mr. Salahuddin Saddar, Mr. Sarwar Ali, Mr. Umar Farooq, Mr. Mansoor, Mr. Junaid Ahmed
- Ms. Aisha Esani, Ms. Dua Agha, Ms. Mariam Memon, Ms. Sana Faiz
- Ms. Shafya Qadeer, Ms. Shazma Memon, Ms. Soonti Taj, Ms. Amirta Dewani
- Ms. Aleena, Ms. Hina Ali

### Subjects (25 total)
- **Theory Subjects (18)**: All core subjects for each semester
- **Practical Subjects (7)**: Corresponding practical sessions

## Output Example
```
🎓 TIMETABLE GENERATION SYSTEM - TEST DATA POPULATOR
================================================================================
📋 Populating database with complete MUET Software Engineering data
📅 Batches: 21SW, 22SW, 23SW, 24SW
================================================================================

👨‍🏫 CREATING TEACHERS...
--------------------------------------------------
✅ Created: Dr. Areej Fatemah
✅ Created: Dr. Rabeea Jaffari
...

📚 CREATING SUBJECTS AND ASSIGNMENTS...
--------------------------------------------------
📖 THEORY SUBJECTS:
✅ Created Theory: SM - Simulation and Modeling
   👨‍🏫 Assigned 2 teachers: Dr. Sania Bhatti, Mr. Umar Farooq
...

🧪 PRACTICAL SUBJECTS:
✅ Created Practical: CC Pr - Cloud Computing Practical
   👨‍🏫 Assigned 1 teachers: Ms. Sana Faiz
...

🎉 DATA POPULATION COMPLETE!
================================================================================
✅ Created 25 new teachers
✅ Created 25 new subjects
✅ Made 35 teacher-subject assignments
✅ All validation checks passed!
🚀 Database is ready for timetable generation!
```

## Next Steps After Running Script
1. **Create Batches**: Use frontend or Django admin to create batch records (21SW, 22SW, 23SW, 24SW)
2. **Test Generation**: Test timetable generation with semester-specific constraints
3. **Verify Frontend**: Test frontend-backend data flow with real data

## Use Cases
- **Fresh Installation**: Quickly populate a new database with realistic test data
- **Testing**: Reset database to known state for comprehensive testing
- **Development**: Provide consistent data set for development and debugging
- **Demo**: Showcase system with realistic university data

## Safety Features
- **Transaction Safety**: All operations wrapped in database transactions
- **Validation**: Comprehensive checks ensure data integrity
- **Confirmation**: Clear confirmation required for destructive operations
- **Rollback**: Automatic rollback on any errors

## File Location
```
django-backend/backend/populate_test_data.py
```

## Requirements
- Django environment properly configured
- Database migrations applied
- Timetable models (Teacher, Subject) available

---
**Note**: This script is designed for testing and development. For production use, populate data through the frontend interface or Django admin panel.
