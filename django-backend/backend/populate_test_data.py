#!/usr/bin/env python3
"""
Timetable Generation System - Test Data Population Script
=========================================================

This script populates the database with complete test data based on the 
4 batch timetables (21SW, 22SW, 23SW, 24SW) from MUET Department of Software Engineering.

Usage:
    python populate_test_data.py

Features:
- Creates all teachers with proper emails
- Creates all theory and practical subjects
- Assigns teachers to subjects exactly as per original timetables
- Supports both fresh setup and data refresh
- Comprehensive verification and reporting

Author: Timetable Generation System
Date: 2025-01-20
"""

import os
import sys
import django
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher


class TimetableDataPopulator:
    """Handles population of test data for timetable generation system."""
    
    def __init__(self):
        self.created_teachers = 0
        self.created_subjects = 0
        self.total_assignments = 0
        
    def clear_existing_data(self):
        """Clear existing data if requested."""
        print("🗑️  CLEARING EXISTING DATA...")
        print("-" * 50)
        
        # Clear assignments first (many-to-many relationships)
        for teacher in Teacher.objects.all():
            teacher.subjects.clear()
        
        # Delete all records
        subjects_deleted = Subject.objects.count()
        teachers_deleted = Teacher.objects.count()
        
        Subject.objects.all().delete()
        Teacher.objects.all().delete()
        
        print(f"✅ Deleted {teachers_deleted} teachers")
        print(f"✅ Deleted {subjects_deleted} subjects")
        print("✅ Cleared all assignments")
        
    def create_teachers(self):
        """Create all teachers from the 4 batch timetables."""
        print("\n👨‍🏫 CREATING TEACHERS...")
        print("-" * 50)
        
        # Complete list of teachers from all 4 images
        teachers_data = [
            # From 21SW, 22SW, 23SW batches
            "Dr. Areej Fatemah",
            "Dr. Rabeea Jaffari", 
            "Dr. S. M. Shehram Shah",
            "Dr. Sania Bhatti",
            "Mr. Aqib Ali",
            "Mr. Arsalan",
            "Mr. Mansoor Bhaagat",
            "Mr. Naveen Kumar",
            "Mr. Salahuddin Saddar",
            "Mr. Sarwar Ali",
            "Mr. Umar Farooq",
            "Ms. Aisha Esani",
            "Ms. Dua Agha",
            "Ms. Mariam Memon",
            "Ms. Sana Faiz",
            "Ms. Shafya Qadeer",
            "Ms. Shazma Memon",
            "Ms. Soonti Taj",
            "Prof. Dr. Qasim Ali",
            
            # From 24SW batch (new teachers)
            "Dr. Mohsin Memon",
            "Mr. Mansoor",
            "Ms. Amirta Dewani",
            "Mr. Junaid Ahmed",
            "Ms. Aleena",
            "Ms. Hina Ali"
        ]
        
        for teacher_name in teachers_data:
            if not Teacher.objects.filter(name=teacher_name).exists():
                # Generate email from name
                email_name = (teacher_name.lower()
                            .replace('dr. ', '')
                            .replace('mr. ', '')
                            .replace('ms. ', '')
                            .replace('prof. ', '')
                            .replace(' ', '.'))
                email = f"{email_name}@faculty.muet.edu.pk"
                
                teacher = Teacher.objects.create(name=teacher_name, email=email)
                print(f"✅ Created: {teacher_name}")
                self.created_teachers += 1
            else:
                print(f"📖 Exists: {teacher_name}")
                
        print(f"\n📊 Teachers Summary: {self.created_teachers} created, {len(teachers_data)} total")
        
    def create_subjects_and_assignments(self):
        """Create all subjects and assign teachers."""
        print("\n📚 CREATING SUBJECTS AND ASSIGNMENTS...")
        print("-" * 50)
        
        # Complete subject-teacher mapping from all 4 batches
        subjects_data = [
            # 21SW - 8th Semester (Final Year)
            ('SM', 'Simulation and Modeling', 3, ['Dr. Sania Bhatti', 'Mr. Umar Farooq']),
            ('CC', 'Cloud Computing', 3, ['Ms. Sana Faiz']),
            ('SQE', 'Software Quality Engineering', 3, ['Mr. Aqib Ali']),
            
            # 22SW - 6th Semester (3rd Year)
            ('SPM', 'Software Project Management', 3, ['Mr. Salahuddin Saddar']),
            ('DS&A', 'Data Science & Analytics', 3, ['Ms. Aisha Esani']),
            ('MAD', 'Mobile Application Development', 3, ['Ms. Mariam Memon', 'Mr. Umar Farooq']),
            ('DS', 'Discrete Structures', 3, ['Ms. Shafya Qadeer']),
            ('TSW', 'Technical & Scientific Writing', 3, ['Mr. Sarwar Ali', 'Ms. Shazma Memon']),
            
            # 23SW - 4th Semester (2nd Year)
            ('IS', 'Information Security', 3, ['Ms. Soonti Taj', 'Prof. Dr. Qasim Ali']),
            ('HCI', 'Human Computer Interaction', 3, ['Mr. Arsalan']),
            ('ABIS', 'Agent based Intelligent Systems', 3, ['Mr. Naveen Kumar']),
            ('SCD', 'Software Construction & Development', 3, ['Ms. Dua Agha']),
            ('SP', 'Statistics & Probability', 3, ['Mr. Mansoor Bhaagat']),
            
            # 24SW - 2nd Semester (1st Year)
            ('DSA', 'Data Structure & Algorithm', 3, ['Dr. Mohsin Memon', 'Mr. Mansoor']),
            ('OR', 'Operations Research', 3, ['Mr. Naveen Kumar']),
            ('SRE', 'Software Requirement Engineering', 3, ['Ms. Amirta Dewani']),
            ('SEM', 'Software Economics & Management', 3, ['Mr. Junaid Ahmed']),
            ('DBS', 'Database Systems', 3, ['Ms. Aleena', 'Ms. Hina Ali']),
        ]
        
        # Practical subjects with specific teachers
        practical_subjects_data = [
            # 21SW Practicals
            ('CC Pr', 'Cloud Computing Practical', 1, ['Ms. Sana Faiz']),
            ('SQE Pr', 'Software Quality Engineering Practical', 1, ['Mr. Aqib Ali']),
            
            # 22SW Practicals
            ('DS&A Pr', 'Data Science & Analytics Practical', 1, ['Ms. Aisha Esani']),
            ('MAD Pr', 'Mobile Application Development Practical', 1, ['Mr. Umar Farooq']),
            
            # 23SW Practicals
            ('SCD Pr', 'Software Construction & Development Practical', 1, ['Ms. Dua Agha']),
            
            # 24SW Practicals
            ('DSA Pr', 'Data Structure & Algorithm Practical', 1, ['Dr. Mohsin Memon', 'Mr. Mansoor']),
            ('DBS Pr', 'Database Systems Practical', 1, ['Ms. Hina Ali']),
        ]
        
        # Create theory subjects
        print("\n📖 THEORY SUBJECTS:")
        self._create_subjects_batch(subjects_data, "Theory")
        
        # Create practical subjects
        print("\n🧪 PRACTICAL SUBJECTS:")
        self._create_subjects_batch(practical_subjects_data, "Practical")
        
    def _create_subjects_batch(self, subjects_data, subject_type):
        """Helper method to create a batch of subjects."""
        for code, name, credits, teacher_names in subjects_data:
            # Create subject
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'credits': credits}
            )
            
            if created:
                print(f"✅ Created {subject_type}: {code} - {name}")
                self.created_subjects += 1
            else:
                print(f"📖 Exists {subject_type}: {code} - {name}")
            
            # Assign teachers
            assigned_count = 0
            for teacher_name in teacher_names:
                if teacher_name:
                    teacher = Teacher.objects.filter(name=teacher_name).first()
                    if teacher:
                        teacher.subjects.add(subject)
                        assigned_count += 1
                        self.total_assignments += 1
                    else:
                        print(f"   ❌ Teacher not found: {teacher_name}")
            
            if assigned_count > 0:
                teacher_list = ', '.join(teacher_names)
                print(f"   👨‍🏫 Assigned {assigned_count} teachers: {teacher_list}")

    def verify_data(self):
        """Verify the populated data and generate comprehensive report."""
        print("\n🔍 VERIFICATION AND REPORTING...")
        print("=" * 80)

        teachers = Teacher.objects.all().order_by('name')
        subjects = Subject.objects.all().order_by('code')

        # Separate theory and practical subjects
        theory_subjects = subjects.exclude(code__contains='Pr')
        practical_subjects = subjects.filter(code__contains='Pr')

        print(f"\n📊 DATABASE STATISTICS:")
        print("-" * 50)
        print(f"Total Teachers: {teachers.count()}")
        print(f"Total Subjects: {subjects.count()}")
        print(f"  - Theory: {theory_subjects.count()}")
        print(f"  - Practical: {practical_subjects.count()}")
        print(f"Total Assignments: {self.total_assignments}")

        print(f"\n🎯 SUBJECTS BY BATCH/SEMESTER:")
        print("-" * 50)

        batch_subjects = {
            '21SW (8th Sem - Final Year)': ['SM', 'CC', 'SQE', 'CC Pr', 'SQE Pr'],
            '22SW (6th Sem - 3rd Year)': ['SPM', 'DS&A', 'MAD', 'DS', 'TSW', 'DS&A Pr', 'MAD Pr'],
            '23SW (4th Sem - 2nd Year)': ['IS', 'HCI', 'ABIS', 'SCD', 'SP', 'SCD Pr'],
            '24SW (2nd Sem - 1st Year)': ['DSA', 'OR', 'SRE', 'SEM', 'DBS', 'DSA Pr', 'DBS Pr']
        }

        for batch, subject_codes in batch_subjects.items():
            print(f"\n{batch}:")
            for code in subject_codes:
                subject = Subject.objects.filter(code=code).first()
                if subject:
                    teachers_assigned = subject.teacher_set.all()
                    teacher_names = ', '.join([t.name for t in teachers_assigned])
                    print(f"  {code}: {teacher_names if teacher_names else 'No teachers'}")
                else:
                    print(f"  {code}: ❌ MISSING SUBJECT")

        print(f"\n👨‍🏫 TEACHER WORKLOAD:")
        print("-" * 50)
        for teacher in teachers:
            subjects_taught = teacher.subjects.all().order_by('code')
            if subjects_taught:
                theory_subjects = [s.code for s in subjects_taught if 'Pr' not in s.code]
                practical_subjects = [s.code for s in subjects_taught if 'Pr' in s.code]

                print(f"{teacher.name}:")
                if theory_subjects:
                    print(f"   📖 Theory: {', '.join(theory_subjects)}")
                if practical_subjects:
                    print(f"   🧪 Practical: {', '.join(practical_subjects)}")

        # Validation checks
        print(f"\n✅ VALIDATION CHECKS:")
        print("-" * 50)

        unassigned_subjects = []
        for subject in subjects:
            if not subject.teacher_set.exists():
                unassigned_subjects.append(subject.code)

        if unassigned_subjects:
            print(f"❌ Subjects without teachers: {', '.join(unassigned_subjects)}")
        else:
            print("✅ All subjects have assigned teachers")

        # Check for missing practical counterparts
        practical_base_codes = []
        for subject in practical_subjects:
            if subject.code.endswith(' Pr'):
                base_code = subject.code.replace(' Pr', '')
                practical_base_codes.append(base_code)
            elif subject.code.endswith('Pr'):
                base_code = subject.code.replace('Pr', '')
                practical_base_codes.append(base_code)

        expected_practicals = ['CC', 'SQE', 'DS&A', 'MAD', 'SCD', 'DSA', 'DBS']
        missing_practicals = [code for code in expected_practicals if code not in practical_base_codes]

        print(f"📊 Found practical subjects: {', '.join([f'{code} Pr' for code in practical_base_codes])}")

        if missing_practicals:
            print(f"⚠️  Missing practical subjects: {', '.join([f'{code} Pr' for code in missing_practicals])}")
        else:
            print("✅ All expected practical subjects created")

        return len(unassigned_subjects) == 0 and len(missing_practicals) == 0

    def run(self, clear_existing=False):
        """Main execution method."""
        print("🎓 TIMETABLE GENERATION SYSTEM - TEST DATA POPULATOR")
        print("=" * 80)
        print("📋 Populating database with complete MUET Software Engineering data")
        print("📅 Batches: 21SW, 22SW, 23SW, 24SW")
        print("=" * 80)

        try:
            with transaction.atomic():
                if clear_existing:
                    self.clear_existing_data()

                self.create_teachers()
                self.create_subjects_and_assignments()

                # Verify data
                is_valid = self.verify_data()

                print(f"\n🎉 DATA POPULATION COMPLETE!")
                print("=" * 80)
                print(f"✅ Created {self.created_teachers} new teachers")
                print(f"✅ Created {self.created_subjects} new subjects")
                print(f"✅ Made {self.total_assignments} teacher-subject assignments")

                if is_valid:
                    print("✅ All validation checks passed!")
                    print("🚀 Database is ready for timetable generation!")
                else:
                    print("⚠️  Some validation issues found - check output above")

                return True

        except Exception as e:
            print(f"\n❌ ERROR DURING POPULATION: {str(e)}")
            print("🔄 Transaction rolled back - database unchanged")
            return False


def main():
    """Main function with command line argument handling."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Populate timetable database with test data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python populate_test_data.py                    # Add data (keep existing)
  python populate_test_data.py --clear           # Clear and repopulate
  python populate_test_data.py --help            # Show this help
        """
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before populating (WARNING: This will delete all teachers and subjects!)'
    )

    args = parser.parse_args()

    if args.clear:
        confirm = input("\n⚠️  WARNING: This will delete ALL existing teachers and subjects!\n"
                       "Are you sure you want to continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return

    populator = TimetableDataPopulator()
    success = populator.run(clear_existing=args.clear)

    if success:
        print(f"\n🎯 NEXT STEPS:")
        print("1. Create batches (21SW, 22SW, 23SW, 24SW) via frontend or admin")
        print("2. Test timetable generation with semester-specific constraints")
        print("3. Verify frontend-backend data flow")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
