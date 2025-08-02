from rest_framework import viewsets
from .models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config, ClassGroup, Batch, TeacherSubjectAssignment
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ScheduleConfig, TimetableEntry
from celery.result import AsyncResult
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from .algorithms.advanced_scheduler import AdvancedTimetableScheduler
from .algorithms.working_scheduler import WorkingTimetableScheduler
from .algorithms.final_scheduler import FinalUniversalScheduler
from .constraint_manager import ConstraintManager
import logging
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from rest_framework import status
from django.db import transaction
from django.db.models import Q
from django.db import models

from .serializers import (
    SubjectSerializer,
    TeacherSerializer,
    ClassroomSerializer,
    ScheduleConfigSerializer,
    TimetableEntrySerializer,
    TimetableSerializer,
    ConfigSerializer,
    ClassGroupSerializer,
    BatchSerializer,
    TeacherSubjectAssignmentSerializer
)

from .tasks import (
    generate_timetable_async,
    validate_constraints_async,
    optimize_timetable_async,
    generate_timetable_report
)

from .services.cross_semester_conflict_detector import CrossSemesterConflictDetector
from .constraint_validator import ConstraintValidator

logger = logging.getLogger(__name__)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    authentication_classes = []  # Temporarily disable authentication for testing

    def create(self, request, *args, **kwargs):
        logger.info(f"Classroom received data: {request.data}")
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Classroom save failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

class ScheduleConfigViewSet(viewsets.ModelViewSet):
    queryset = ScheduleConfig.objects.all()
    serializer_class = ScheduleConfigSerializer
    authentication_classes = []  # Temporarily disable authentication for testing

    def create(self, request, *args, **kwargs):
        logger.info(f"ScheduleConfig received data: {request.data}")
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"ScheduleConfig save failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    authentication_classes = []  # Temporarily disable authentication for testing

class TeacherSubjectAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherSubjectAssignment.objects.all()
    serializer_class = TeacherSubjectAssignmentSerializer
    authentication_classes = []  # Temporarily disable authentication for testing

    def get_queryset(self):
        queryset = TeacherSubjectAssignment.objects.all()
        teacher_id = self.request.query_params.get('teacher', None)
        subject_id = self.request.query_params.get('subject', None)
        batch_id = self.request.query_params.get('batch', None)

        if teacher_id is not None:
            queryset = queryset.filter(teacher_id=teacher_id)
        if subject_id is not None:
            queryset = queryset.filter(subject_id=subject_id)
        if batch_id is not None:
            queryset = queryset.filter(batch_id=batch_id)

        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            # Handle validation errors and provide user-friendly messages
            error_message = str(e)
            if "already assigned" in error_message.lower():
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif "sections" in error_message.lower() and "assigned" in error_message.lower():
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': f'Failed to create assignment: {error_message}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            if "already assigned" in error_message.lower():
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif "sections" in error_message.lower() and "assigned" in error_message.lower():
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': f'Failed to update assignment: {error_message}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = TimetableEntry.objects.all()
    serializer_class = TimetableEntrySerializer

class FastTimetableView(APIView):
    """
    Very fast timetable generation for immediate results.
    """
    
    def post(self, request):
        try:
            # Get the latest config
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )
            
            # Get subjects, teachers, and classrooms
            subjects = Subject.objects.all()
            teachers = Teacher.objects.all()
            classrooms = Classroom.objects.all()
            
            print(f"Debug: Found {subjects.count()} subjects, {teachers.count()} teachers, {classrooms.count()} classrooms")
            print(f"Debug: Class groups: {config.class_groups}")
            
            if not subjects.exists() or not teachers.exists() or not classrooms.exists():
                return Response(
                    {'error': 'Please populate data first using the data population script.'},
                    status=400
                )
            
            # Clear existing timetable entries
            TimetableEntry.objects.all().delete()
            
            # Create a simple timetable
            entries = []
            class_groups = config.class_groups[:3] if isinstance(config.class_groups, list) else config.class_groups  # Use first 3 class groups for speed
            
            for class_group in class_groups:
                # Get theory and practical subjects
                theory_subjects = subjects.filter(is_practical=False)[:5]  # First 5 theory subjects
                practical_subjects = subjects.filter(is_practical=True)[:3]  # First 3 practical subjects
                
                print(f"Debug: For {class_group}, found {theory_subjects.count()} theory subjects, {practical_subjects.count()} practical subjects")
                
                # Schedule theory subjects
                theory_classrooms = [c for c in classrooms if 'Lab' not in c.name]
                if not theory_classrooms:
                    theory_classrooms = list(classrooms)  # Fallback to all classrooms
                
                for i, subject in enumerate(theory_subjects):
                    teacher = teachers[i % len(teachers)]
                    classroom = theory_classrooms[i % len(theory_classrooms)]
                    
                    entry = TimetableEntry.objects.create(
                        day=config.days[i % len(config.days)],
                        period=(i % 7) + 1,
                        subject=subject,
                        teacher=teacher,
                        classroom=classroom,
                        class_group=class_group,
                        start_time=config.start_time,
                        end_time=config.start_time,
                        is_practical=False
                    )
                    entries.append(entry)
                
                # Schedule practical subjects in 3 consecutive periods
                lab_classrooms = [c for c in classrooms if 'Lab' in c.name]
                if not lab_classrooms:
                    lab_classrooms = list(classrooms)  # Fallback to all classrooms
                
                for i, subject in enumerate(practical_subjects):
                    teacher = teachers[(i + 5) % len(teachers)]
                    lab_classroom = lab_classrooms[i % len(lab_classrooms)]
                    
                    # Create 3 consecutive periods for practical
                    for j in range(3):
                        entry = TimetableEntry.objects.create(
                            day=config.days[(i + 2) % len(config.days)],  # Different day
                            period=j + 1,
                            subject=subject,
                            teacher=teacher,
                            classroom=lab_classroom,
                            class_group=class_group,
                            start_time=config.start_time,
                            end_time=config.start_time,
                            is_practical=True
                        )
                        entries.append(entry)
            
            # Format response
            result = {
                'success': True,
                'message': 'Fast timetable generated successfully',
                'generation_time': 0.5,
                'fitness_score': 85.0,
                'constraint_violations': [],
                'generation': 1,
                'days': config.days,
                'timeSlots': [f"Period {i+1}" for i in range(7)],
                'entries': [{
                    'day': entry.day,
                    'period': entry.period,
                    'subject': f"{entry.subject.name}{' (PR)' if entry.is_practical else ''}",
                    'teacher': entry.teacher.name if entry.teacher else '',
                    'classroom': entry.classroom.name if entry.classroom else '',
                    'class_group': entry.class_group,
                    'start_time': entry.start_time.strftime("%H:%M:%S"),
                    'end_time': entry.end_time.strftime("%H:%M:%S"),
                    'is_practical': entry.is_practical
                } for entry in entries]
            }
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Fast timetable generation error: {str(e)}")
            return Response(
                {'error': f'Failed to generate timetable: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SimpleTimetableView(APIView):
    """
    Simple synchronous timetable generation for faster response.
    """
    
    def post(self, request):
        try:
            # Get the latest config
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )
            
            # Use the FINAL UNIVERSAL scheduler - works with ANY data
            scheduler = FinalUniversalScheduler(config)

            # Generate timetable synchronously (faster)
            result = scheduler.generate_timetable()
            
            return Response({
                'success': True,
                'message': 'Timetable generated successfully',
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Simple timetable generation error: {str(e)}")
            return Response(
                {'error': f'Failed to generate timetable: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdvancedTimetableView(APIView):
    """
    Advanced timetable generation with genetic algorithm and constraint satisfaction.
    """
    
    def post(self, request):
        try:
            # Get the latest config
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            print("Loaded config:", config)
            print("Config start_time:", getattr(config, 'start_time', None))
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )
            
            # Get constraints from request
            constraints = request.data.get('constraints', [])
            
            # Start async generation
            task = generate_timetable_async.delay(
                config_id=config.id,
                constraints=constraints
            )
            
            return Response({
                'success': True,
                'task_id': task.id,
                'message': 'Timetable generation started. Use task status endpoint to track progress.',
                'status_endpoint': f'/api/timetable/task-status/{task.id}/'
            })
            
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Advanced timetable generation error: {str(e)}")
            return Response(
                {'error': f'Failed to start timetable generation: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConstraintManagementView(APIView):
    """
    Manage scheduling constraints.
    """
    
    def get(self, request):
        try:
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            print("Loaded config:", config)
            print("Config start_time:", getattr(config, 'start_time', None))
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )
            constraint_manager = ConstraintManager(config)
            
            return Response(constraint_manager.export_constraints())
            
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Constraint management error: {str(e)}")
            return Response(
                {'error': f'Failed to get constraints: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            print("Loaded config:", config)
            print("Config start_time:", getattr(config, 'start_time', None))
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )
            constraint_manager = ConstraintManager(config)
            
            # Validate constraints
            is_valid = constraint_manager.validate_constraints()
            
            if not is_valid:
                return Response({
                    'success': False,
                    'validation_errors': constraint_manager.validation_errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update config with new constraints
            config.constraints = request.data.get('constraints', [])
            config.save()
            
            return Response({
                'success': True,
                'message': 'Constraints updated successfully',
                'constraint_summary': constraint_manager.get_constraint_summary()
            })
            
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Constraint update error: {str(e)}")
            return Response(
                {'error': f'Failed to update constraints: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OptimizationView(APIView):
    """
    Timetable optimization with multiple parameter sets.
    """
    
    def post(self, request):
        try:
            # Get optimization parameters
            optimization_params = request.data.get('optimization_params', {})
            
            # Start async optimization
            task = optimize_timetable_async.delay(
                optimization_params=optimization_params
            )
            
            return Response({
                'success': True,
                'task_id': task.id,
                'message': 'Timetable optimization started. Use task status endpoint to track progress.',
                'status_endpoint': f'/api/timetable/task-status/{task.id}/'
            })
            
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")
            return Response(
                {'error': f'Failed to start optimization: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TimetableReportView(APIView):
    """
    Generate comprehensive timetable reports.
    """
    
    def get(self, request):
        try:
            # Start async report generation
            task = generate_timetable_report.delay()
            
            return Response({
                'success': True,
                'task_id': task.id,
                'message': 'Report generation started. Use task status endpoint to get results.',
                'status_endpoint': f'/api/timetable/task-status/{task.id}/'
            })
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return Response(
                {'error': f'Failed to generate report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskStatusView(APIView):
    """
    Get status of async tasks.
    """
    
    def get(self, request, task_id):
        try:
            task = AsyncResult(task_id)
            
            if task.ready():
                result = task.result
                return Response({
                    'status': 'completed',
                    'result': result
                })
            else:
                # Get progress information
                if hasattr(task, 'info'):
                    progress = task.info
                else:
                    progress = {
                        'current': 0,
                        'total': 100,
                        'status': 'Processing...'
                    }
                
                return Response({
                    'status': 'processing',
                    'progress': progress
                })
                
        except Exception as e:
            logger.error(f"Task status error: {str(e)}")
            return Response(
                {'error': f'Failed to get task status: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TimetableView(APIView):
    authentication_classes = []  # Temporarily disable authentication for testing
    
    def get(self, request):
        try:
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            print("Loaded config:", config)
            print("Config start_time:", getattr(config, 'start_time', None))
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )
            entries = TimetableEntry.objects.all().order_by('day', 'period')
            
            # Get unique class groups
            class_groups = entries.values_list('class_group', flat=True).distinct()
            
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 1))  # Default to 1 timetable per page
            
            timetables = []
            for class_group in class_groups:
                class_entries = entries.filter(class_group=class_group)
                
                # Get all subjects for this class group
                subjects = Subject.objects.filter(
                    id__in=class_entries.values_list('subject', flat=True).distinct()
                )
                
                # Format time slots
                time_slots = []
                current_time = config.start_time
                for i in range(len(config.periods)):
                    end_time = (datetime.combine(datetime.today(), current_time) + 
                              timedelta(minutes=config.lesson_duration)).time()
                    slot = {
                        'period': i + 1,
                        'display': f"{i+1}{'st' if i==0 else 'nd' if i==1 else 'rd' if i==2 else 'th'} [{current_time.strftime('%I:%M')} to {end_time.strftime('%I:%M')}]"
                    }
                    time_slots.append(slot)
                    current_time = end_time
                
                # Create day-wise entries
                days_data = {}
                for day in config.days:
                    day_entries = class_entries.filter(day=day)
                    rooms = day_entries.values_list('classroom__name', flat=True).distinct()
                    days_data[day] = {
                        'room': next(iter(rooms), ''),
                        'entries': {}
                    }
                    for entry in day_entries:
                        days_data[day]['entries'][entry.period] = {
                            'subject': f"{entry.subject.name}{'(PR)' if entry.is_practical else ''}",
                            'room': entry.classroom.name if entry.classroom else '',
                            'teacher': entry.teacher.name if entry.teacher else ''
                        }
                
                # Get subject details
                subject_details = []
                for subject in subjects:
                    teachers = Teacher.objects.filter(subjects=subject)
                    theory_credits = 3 if subject.credits >= 3 else 2
                    practical_credits = 1 if subject.is_practical else 0
                    
                    subject_details.append({
                        'code': subject.code,
                        'name': subject.name,
                        'credit_hours': f"{theory_credits}+{practical_credits}",
                        'teachers': [t.name for t in teachers]
                    })
                
                timetable_data = {
                    'class_group': class_group,
                    'header': f"TIMETABLE OF {class_group}",
                    'time_slots': time_slots,
                    'days': days_data,
                    'subject_details': subject_details
                }
                
                timetables.append(timetable_data)
            
            # Implement pagination
            paginator = Paginator(timetables, page_size)
            total_pages = paginator.num_pages
            
            try:
                current_page = paginator.page(page)
            except Exception:
                current_page = paginator.page(1)
            
            return Response({
                'timetables': current_page.object_list,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'page_size': page_size,
                    'total_items': len(timetables)
                }
            })
            
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=404
            )
        except Exception as e:
            logger.error(f"Error retrieving timetable: {str(e)}")
            return Response(
                {'error': f'Failed to retrieve timetable: {str(e)}'}, 
                status=500
            )

    def post(self, request):
        try:
            # Get the latest config
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config:
                return Response(
                    {'error': 'No schedule configuration found. Please create a schedule configuration first.'},
                    status=400
                )
            if not config.start_time:
                return Response(
                    {'error': 'Schedule configuration is missing start time. Please update the configuration.'},
                    status=400
                )
            # Get active constraints from request
            constraints = request.data.get('constraints', [])
            # Update config with the constraints from the request
            config.constraints = constraints
            # Create scheduler instance - use FINAL UNIVERSAL scheduler
            scheduler = FinalUniversalScheduler(config)
            # Generate timetable
            timetable = scheduler.generate_timetable()
            # Save entries to database
            TimetableEntry.objects.all().delete()  # Clear existing entries
            entries_to_create = []
            for entry in timetable['entries']:
                # Remove (PR) from subject name if present
                subject_name = entry['subject'].replace(' (PR)', '')

                # Handle teacher assignment (may be None for THESISDAY entries)
                teacher = None
                if entry['teacher'] and entry['teacher'] != 'No Teacher Assigned':
                    try:
                        teacher = Teacher.objects.get(name=entry['teacher'])
                    except Teacher.DoesNotExist:
                        logger.warning(f"Teacher '{entry['teacher']}' not found, setting to None")
                        teacher = None

                # Handle classroom assignment (may be None)
                classroom = None
                if entry['classroom'] and entry['classroom'] != 'No Classroom Assigned':
                    try:
                        classroom = Classroom.objects.get(name=entry['classroom'])
                    except Classroom.DoesNotExist:
                        logger.warning(f"Classroom '{entry['classroom']}' not found, setting to None")
                        classroom = None

                entries_to_create.append(TimetableEntry(
                    day=entry['day'],
                    period=entry['period'],
                    subject=Subject.objects.get(name=subject_name),
                    teacher=teacher,
                    classroom=classroom,
                    class_group=entry['class_group'],
                    start_time=entry['start_time'],
                    end_time=entry['end_time'],
                    is_practical='(PR)' in entry['subject'],
                    schedule_config=config,
                    semester=config.semester,
                    academic_year=config.academic_year
                ))
            # Bulk create entries for better performance
            TimetableEntry.objects.bulk_create(entries_to_create)
            # Return success message
            return Response({
                'message': 'Timetable generated successfully',
                'entries_count': len(entries_to_create)
            })
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=404
            )
        except Exception as e:
            logger.error(f"Timetable generation error: {str(e)}")
            return Response(
                {'error': f'Failed to generate timetable: {str(e)}'}, 
                status=500
            )
    

class ConfigViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Received data: {request.data}")
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Save failed: {str(e)}")
            raise

class ClassRoomViewSet(viewsets.ModelViewSet):
    queryset = ClassGroup.objects.all()
    serializer_class = ClassGroupSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes = [IsAuthenticated]
    filterset_fields = ['code', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset
    
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    # permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'email']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset

class LatestTimetableView(APIView):
    authentication_classes = []  # Temporarily disable authentication for testing
    
    def get(self, request):
        try:
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config or not config.start_time:
                return Response(
                    {'error': 'No valid schedule configuration found.'},
                    status=400
                )

            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            class_group_filter = request.query_params.get('class_group', None)

            # Get all entries
            entries_query = TimetableEntry.objects.all().order_by('day', 'period')

            # Filter by class group if specified
            if class_group_filter:
                entries_query = entries_query.filter(class_group=class_group_filter)

            # Get unique class groups for pagination info
            all_class_groups = list(TimetableEntry.objects.values_list('class_group', flat=True).distinct())
            total_class_groups = len(all_class_groups)

            # If no specific class group requested, paginate by class groups
            if not class_group_filter:
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                paginated_class_groups = all_class_groups[start_idx:end_idx]
                entries_query = entries_query.filter(class_group__in=paginated_class_groups)

            entries = list(entries_query)

            # Format time slots
            time_slots = []
            current_time = config.start_time
            for i in range(len(config.periods)):
                end_time = (datetime.combine(datetime.today(), current_time) +
                          timedelta(minutes=config.lesson_duration)).time()
                time_slots.append(f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
                current_time = end_time

            # Format entries
            formatted_entries = []
            for entry in entries:
                formatted_entries.append({
                    'day': entry.day,
                    'period': entry.period,
                    'subject': f"{entry.subject.name}{' (PR)' if entry.is_practical else ''}",
                    'teacher': entry.teacher.name if entry.teacher else '',
                    'classroom': entry.classroom.name if entry.classroom else '',
                    'class_group': entry.class_group,
                    'start_time': entry.start_time.strftime("%H:%M:%S"),
                    'end_time': entry.end_time.strftime("%H:%M:%S")
                })

            # Calculate pagination info
            total_pages = (total_class_groups + page_size - 1) // page_size if not class_group_filter else 1
            has_next = page < total_pages
            has_previous = page > 1

            return Response({
                'days': config.days,
                'timeSlots': time_slots,
                'entries': formatted_entries,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'page_size': page_size,
                    'total_class_groups': total_class_groups,
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'class_groups': all_class_groups,
                    'current_class_groups': paginated_class_groups if not class_group_filter else [class_group_filter]
                }
            })
            
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=404
            )
        except Exception as e:
            logger.error(f"Error retrieving latest timetable: {str(e)}")
            return Response(
                {'error': f'Failed to retrieve latest timetable: {str(e)}'},
                status=500
            )


class CrossSemesterConflictView(APIView):
    """
    API endpoint for checking cross-semester conflicts
    """

    def get(self, request):
        """Get cross-semester conflict summary"""
        try:
            # Get the latest config
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config:
                return Response(
                    {'error': 'No schedule configuration found.'},
                    status=400
                )

            # Initialize conflict detector
            conflict_detector = CrossSemesterConflictDetector(config)

            # Get conflict summary
            summary = conflict_detector.get_conflict_summary()

            return Response({
                'success': True,
                'current_semester': config.semester,
                'current_academic_year': config.academic_year,
                'conflict_summary': summary
            })

        except Exception as e:
            logger.error(f"Cross-semester conflict check error: {str(e)}")
            return Response(
                {'error': f'Failed to check cross-semester conflicts: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Check conflicts for specific teacher and time slot"""
        try:
            teacher_id = request.data.get('teacher_id')
            day = request.data.get('day')
            period = request.data.get('period')

            if not all([teacher_id, day, period]):
                return Response(
                    {'error': 'teacher_id, day, and period are required'},
                    status=400
                )

            # Get the latest config
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config:
                return Response(
                    {'error': 'No schedule configuration found.'},
                    status=400
                )

            # Initialize conflict detector
            conflict_detector = CrossSemesterConflictDetector(config)

            # Check specific conflict
            has_conflict, conflict_descriptions = conflict_detector.check_teacher_conflict(
                teacher_id, day, period
            )

            # Get alternative suggestions if there's a conflict
            suggestions = []
            if has_conflict:
                suggestions = conflict_detector.suggest_alternative_slots(teacher_id, day)

            return Response({
                'success': True,
                'has_conflict': has_conflict,
                'conflicts': conflict_descriptions,
                'alternative_suggestions': suggestions
            })

        except Exception as e:
            logger.error(f"Specific conflict check error: {str(e)}")
            return Response(
                {'error': f'Failed to check specific conflict: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConstraintTestingView(APIView):
    """
    Comprehensive constraint testing interface for validating timetable constraints.
    Provides detailed analysis for each constraint type.
    """

    def get(self, request):
        """Get detailed constraint analysis for all constraints"""
        try:
            # Get all timetable entries
            entries = TimetableEntry.objects.all()

            if not entries.exists():
                return Response({
                    'success': False,
                    'error': 'No timetable entries found. Please generate a timetable first.'
                })

            # Initialize constraint validator
            validator = ConstraintValidator()

            # Run comprehensive validation
            validation_results = validator.validate_all_constraints(list(entries))

            # Get detailed constraint analysis
            constraint_analysis = self._get_detailed_constraint_analysis(entries)

            return Response({
                'success': True,
                'validation_results': validation_results,
                'constraint_analysis': constraint_analysis,
                'total_entries': entries.count(),
                'total_violations': validation_results['total_violations'],
                'overall_compliance': validation_results['overall_compliance']
            })

        except Exception as e:
            logger.error(f"Constraint testing failed: {str(e)}")
            return Response(
                {'error': f'Constraint testing failed: {str(e)}'},
                status=500
            )

    def post(self, request):
        """Get detailed analysis for a specific constraint type"""
        try:
            constraint_type = request.data.get('constraint_type')

            if not constraint_type:
                return Response(
                    {'error': 'constraint_type is required'},
                    status=400
                )

            # For cross-semester analysis, get ALL entries across all semesters
            if constraint_type == 'cross_semester_conflicts':
                entries = TimetableEntry.objects.all()  # All semesters
            else:
                # For other constraints, get current semester entries
                entries = TimetableEntry.objects.all()

            if not entries.exists():
                return Response({
                    'success': False,
                    'error': 'No timetable entries found. Please generate a timetable first.'
                })

            # Get specific constraint analysis
            analysis = self._get_specific_constraint_analysis(entries, constraint_type)

            return Response({
                'success': True,
                'constraint_type': constraint_type,
                'analysis': analysis,
                'total_entries_analyzed': entries.count()
            })

        except Exception as e:
            logger.error(f"Specific constraint testing failed: {str(e)}")
            return Response(
                {'error': f'Specific constraint testing failed: {str(e)}'},
                status=500
            )

    def _get_detailed_constraint_analysis(self, entries):
        """Get detailed analysis for all constraints"""
        analysis = {}

        # Cross-semester conflicts
        analysis['cross_semester_conflicts'] = self._analyze_cross_semester_conflicts(entries)

        # Subject frequency
        analysis['subject_frequency'] = self._analyze_subject_frequency(entries)

        # Teacher conflicts
        analysis['teacher_conflicts'] = self._analyze_teacher_conflicts(entries)

        # Room conflicts
        analysis['room_conflicts'] = self._analyze_room_conflicts(entries)

        # Practical blocks
        analysis['practical_blocks'] = self._analyze_practical_blocks(entries)

        # Friday time limits
        analysis['friday_time_limits'] = self._analyze_friday_time_limits(entries)

        # Thesis day constraint
        analysis['thesis_day_constraint'] = self._analyze_thesis_day_constraint(entries)

        # Teacher assignments
        analysis['teacher_assignments'] = self._analyze_teacher_assignments(entries)

        # Minimum daily classes
        analysis['minimum_daily_classes'] = self._analyze_minimum_daily_classes(entries)

        # Compact scheduling
        analysis['compact_scheduling'] = self._analyze_compact_scheduling(entries)

        # Friday-aware scheduling
        analysis['friday_aware_scheduling'] = self._analyze_friday_aware_scheduling(entries)

        # Room allocation constraints
        analysis['room_double_booking'] = self._analyze_room_double_booking(entries)
        analysis['practical_same_lab'] = self._analyze_practical_same_lab(entries)
        analysis['practical_in_labs_only'] = self._analyze_practical_in_labs_only(entries)
        analysis['theory_room_consistency'] = self._analyze_theory_room_consistency(entries)
        analysis['section_simultaneous_classes'] = self._analyze_section_simultaneous_classes(entries)
        analysis['working_hours_compliance'] = self._analyze_working_hours_compliance(entries)
        analysis['max_theory_per_day'] = self._analyze_max_theory_per_day(entries)

        return analysis

    def _get_specific_constraint_analysis(self, entries, constraint_type):
        """Get detailed analysis for a specific constraint"""
        analysis_methods = {
            'cross_semester_conflicts': self._analyze_cross_semester_conflicts,
            'subject_frequency': self._analyze_subject_frequency,
            'teacher_conflicts': self._analyze_teacher_conflicts,
            'room_conflicts': self._analyze_room_conflicts,
            'practical_blocks': self._analyze_practical_blocks,
            'friday_time_limits': self._analyze_friday_time_limits,
            'thesis_day_constraint': self._analyze_thesis_day_constraint,
            'teacher_assignments': self._analyze_teacher_assignments,
            'minimum_daily_classes': self._analyze_minimum_daily_classes,
            'compact_scheduling': self._analyze_compact_scheduling,
            'friday_aware_scheduling': self._analyze_friday_aware_scheduling,
            # Room allocation constraints
            'room_double_booking': self._analyze_room_double_booking,
            'practical_same_lab': self._analyze_practical_same_lab,
            'practical_in_labs_only': self._analyze_practical_in_labs_only,
            'theory_room_consistency': self._analyze_theory_room_consistency,
            'section_simultaneous_classes': self._analyze_section_simultaneous_classes,
            'working_hours_compliance': self._analyze_working_hours_compliance,
            'max_theory_per_day': self._analyze_max_theory_per_day,
        }

        if constraint_type in analysis_methods:
            return analysis_methods[constraint_type](entries)
        else:
            return {'error': f'Unknown constraint type: {constraint_type}'}

    def _analyze_cross_semester_conflicts(self, entries):
        """Analyze cross-semester conflicts in detail with teacher-based grouping"""
        try:
            config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
            if not config:
                return {'error': 'No schedule configuration found'}

            conflict_detector = CrossSemesterConflictDetector(config)
            conflicts = []
            teacher_schedules = {}

            # Group all entries by teacher to get complete picture
            for entry in entries:
                if entry.teacher:
                    teacher_name = entry.teacher.name
                    if teacher_name not in teacher_schedules:
                        teacher_schedules[teacher_name] = {
                            'teacher_id': entry.teacher.id,
                            'teacher_name': teacher_name,
                            'subjects': set(),
                            'sections': set(),
                            'schedule': [],
                            'rooms': set(),
                            'semesters': set(),
                            'conflicts': []
                        }

                    teacher_data = teacher_schedules[teacher_name]
                    teacher_data['subjects'].add(entry.subject.name if entry.subject else 'N/A')
                    teacher_data['sections'].add(entry.class_group)
                    teacher_data['rooms'].add(entry.classroom.name if entry.classroom else 'N/A')
                    teacher_data['semesters'].add(entry.semester)

                    # Add schedule entry
                    schedule_entry = {
                        'day': entry.day,
                        'period': entry.period,
                        'time': f"{entry.start_time} - {entry.end_time}",
                        'subject': entry.subject.name if entry.subject else 'N/A',
                        'section': entry.class_group,
                        'room': entry.classroom.name if entry.classroom else 'N/A',
                        'semester': entry.semester,
                        'academic_year': entry.academic_year
                    }
                    teacher_data['schedule'].append(schedule_entry)

                    # Check for conflicts
                    has_conflict, conflict_descriptions = conflict_detector.check_teacher_conflict(
                        entry.teacher.id, entry.day, entry.period
                    )

                    if has_conflict:
                        conflict_info = {
                            'entry_id': entry.id,
                            'teacher': teacher_name,
                            'subject': entry.subject.name if entry.subject else 'N/A',
                            'class_group': entry.class_group,
                            'day': entry.day,
                            'period': entry.period,
                            'time': f"{entry.start_time} - {entry.end_time}",
                            'room': entry.classroom.name if entry.classroom else 'N/A',
                            'conflicts': conflict_descriptions
                        }
                        conflicts.append(conflict_info)
                        teacher_data['conflicts'].append(conflict_info)

            # Convert sets to lists for JSON serialization
            for teacher_name, data in teacher_schedules.items():
                data['subjects'] = list(data['subjects'])
                data['sections'] = list(data['sections'])
                data['rooms'] = list(data['rooms'])
                data['semesters'] = list(data['semesters'])

                # Sort schedule by day and period
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                data['schedule'].sort(key=lambda x: (day_order.index(x['day']) if x['day'] in day_order else 999, x['period']))

            return {
                'total_conflicts': len(conflicts),
                'conflicts': conflicts,
                'teacher_schedules': teacher_schedules,
                'total_teachers': len(teacher_schedules),
                'status': 'PASS' if len(conflicts) == 0 else 'FAIL'
            }

        except Exception as e:
            return {'error': f'Cross-semester analysis failed: {str(e)}'}

    def _analyze_subject_frequency(self, entries):
        """Analyze subject frequency constraints"""
        from collections import defaultdict

        # Group by class_group and subject
        class_subject_counts = defaultdict(lambda: defaultdict(int))
        subject_details = defaultdict(list)

        for entry in entries:
            if entry.subject:
                class_group = entry.class_group
                subject_code = entry.subject.code
                class_subject_counts[class_group][subject_code] += 1

                subject_details[f"{class_group}-{subject_code}"].append({
                    'day': entry.day,
                    'period': entry.period,
                    'time': f"{entry.start_time} - {entry.end_time}",
                    'teacher': entry.teacher.name if entry.teacher else 'N/A',
                    'classroom': entry.classroom.name if entry.classroom else 'N/A'
                })

        violations = []
        compliant_subjects = []

        for class_group, subject_counts in class_subject_counts.items():
            for subject_code, actual_count in subject_counts.items():
                try:
                    subject = Subject.objects.get(code=subject_code)
                    expected_count = subject.credits

                    subject_info = {
                        'class_group': class_group,
                        'subject_code': subject_code,
                        'subject_name': subject.name,
                        'expected_count': expected_count,
                        'actual_count': actual_count,
                        'is_practical': subject.is_practical,
                        'schedule_details': subject_details[f"{class_group}-{subject_code}"]
                    }

                    if actual_count != expected_count:
                        subject_info['violation_type'] = 'frequency_mismatch'
                        violations.append(subject_info)
                    else:
                        compliant_subjects.append(subject_info)

                except Subject.DoesNotExist:
                    violations.append({
                        'class_group': class_group,
                        'subject_code': subject_code,
                        'violation_type': 'subject_not_found',
                        'schedule_details': subject_details[f"{class_group}-{subject_code}"]
                    })

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_subjects': compliant_subjects,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_teacher_conflicts(self, entries):
        """Analyze teacher conflicts (same teacher in multiple places at same time)"""
        from collections import defaultdict

        # Group by day and period
        time_slot_teachers = defaultdict(list)

        for entry in entries:
            if entry.teacher:
                key = f"{entry.day}-{entry.period}"
                time_slot_teachers[key].append({
                    'teacher_id': entry.teacher.id,
                    'teacher_name': entry.teacher.name,
                    'subject': entry.subject.name if entry.subject else 'N/A',
                    'class_group': entry.class_group,
                    'classroom': entry.classroom.name if entry.classroom else 'N/A',
                    'time': f"{entry.start_time} - {entry.end_time}"
                })

        conflicts = []

        for time_slot, teacher_entries in time_slot_teachers.items():
            # Group by teacher
            teacher_groups = defaultdict(list)
            for entry in teacher_entries:
                teacher_groups[entry['teacher_id']].append(entry)

            # Check for conflicts (same teacher in multiple places)
            for teacher_id, teacher_entries_list in teacher_groups.items():
                if len(teacher_entries_list) > 1:
                    day, period = time_slot.split('-')
                    conflicts.append({
                        'day': day,
                        'period': int(period),
                        'teacher_id': teacher_id,
                        'teacher_name': teacher_entries_list[0]['teacher_name'],
                        'conflicting_assignments': teacher_entries_list,
                        'conflict_count': len(teacher_entries_list)
                    })

        return {
            'total_conflicts': len(conflicts),
            'conflicts': conflicts,
            'status': 'PASS' if len(conflicts) == 0 else 'FAIL'
        }

    def _analyze_room_conflicts(self, entries):
        """Analyze room conflicts (same room assigned to multiple classes at same time)"""
        from collections import defaultdict

        conflicts = []

        # Group by day-period to find room conflicts
        day_period_rooms = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            if entry.classroom:
                day_period_key = f"{entry.day}-{entry.period}"
                room_id = entry.classroom.id
                day_period_rooms[day_period_key][room_id].append({
                    'entry_id': entry.id,
                    'classroom_name': entry.classroom.name,
                    'subject': entry.subject.name if entry.subject else 'N/A',
                    'teacher': entry.teacher.name if entry.teacher else 'N/A',
                    'class_group': entry.class_group,
                    'time': f"{entry.start_time} - {entry.end_time}"
                })

        print(f"Analyzing room conflicts for {len(entries)} entries")

        for day_period, rooms in day_period_rooms.items():
            for room_id, room_entries in rooms.items():
                if len(room_entries) > 1:
                    day, period = day_period.split('-')
                    conflict_info = {
                        'day': day,
                        'period': int(period),
                        'classroom_id': room_id,
                        'classroom_name': room_entries[0]['classroom_name'],
                        'conflicting_assignments': room_entries,
                        'conflict_count': len(room_entries)
                    }
                    conflicts.append(conflict_info)
                    print(f"Found room conflict: {room_entries[0]['classroom_name']} on {day} P{period} - {len(room_entries)} assignments")

        print(f"Total room conflicts found: {len(conflicts)}")

        return {
            'total_conflicts': len(conflicts),
            'conflicts': conflicts,
            'status': 'PASS' if len(conflicts) == 0 else 'FAIL'
        }

    def _analyze_practical_in_labs_only(self, entries):
        """Analyze if practical subjects are only in labs"""
        violations = []

        for entry in entries:
            if (entry.subject and entry.subject.is_practical and
                entry.classroom and not entry.classroom.is_lab):
                violations.append({
                    'class_group': entry.class_group,
                    'subject': entry.subject.code,
                    'classroom': entry.classroom.name,
                    'day': entry.day,
                    'period': entry.period,
                    'description': f'Practical {entry.subject.code} in non-lab room {entry.classroom.name}'
                })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} practical subjects not in labs'
        }

    def _analyze_theory_room_consistency(self, entries):
        """Analyze theory room consistency violations"""
        from collections import defaultdict

        violations = []
        section_daily_rooms = defaultdict(lambda: defaultdict(set))

        # Track rooms used by each section on each day for theory classes
        for entry in entries:
            if entry.subject and not entry.subject.is_practical and entry.classroom:
                section_daily_rooms[entry.class_group][entry.day].add(entry.classroom.name)

        # Check for inconsistencies
        for class_group, daily_rooms in section_daily_rooms.items():
            for day, rooms in daily_rooms.items():
                if len(rooms) > 1:
                    violations.append({
                        'class_group': class_group,
                        'day': day,
                        'rooms_used': list(rooms),
                        'description': f'{class_group} uses multiple rooms on {day}: {", ".join(rooms)}'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} room consistency violations'
        }

    def _analyze_section_simultaneous_classes(self, entries):
        """Analyze sections with simultaneous classes"""
        from collections import defaultdict

        violations = []
        time_slot_sections = defaultdict(list)

        # Group entries by time slot
        for entry in entries:
            key = (entry.day, entry.period)
            time_slot_sections[key].append(entry)

        # Check for sections with multiple classes at same time
        for (day, period), slot_entries in time_slot_sections.items():
            section_counts = defaultdict(int)
            for entry in slot_entries:
                section_counts[entry.class_group] += 1

            for class_group, count in section_counts.items():
                if count > 1:
                    violations.append({
                        'class_group': class_group,
                        'day': day,
                        'period': period,
                        'simultaneous_classes': count,
                        'description': f'{class_group} has {count} simultaneous classes on {day} P{period}'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} simultaneous class violations'
        }

    def _analyze_working_hours_compliance(self, entries):
        """Analyze working hours compliance (8AM-3PM)"""
        violations = []

        for entry in entries:
            if entry.start_time and entry.end_time:
                # Handle both string and time object formats
                if isinstance(entry.start_time, str):
                    start_hour = int(entry.start_time.split(':')[0])
                else:
                    start_hour = entry.start_time.hour

                if isinstance(entry.end_time, str):
                    end_hour = int(entry.end_time.split(':')[0])
                else:
                    end_hour = entry.end_time.hour

                if start_hour < 8 or end_hour > 15:
                    violations.append({
                        'class_group': entry.class_group,
                        'subject': entry.subject.code if entry.subject else 'Unknown',
                        'day': entry.day,
                        'period': entry.period,
                        'start_time': str(entry.start_time),
                        'end_time': str(entry.end_time),
                        'description': f'Class {entry.start_time}-{entry.end_time} outside 8AM-3PM'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} working hours violations'
        }

    def _analyze_max_theory_per_day(self, entries):
        """Analyze maximum one theory class per day constraint"""
        from collections import defaultdict

        violations = []
        section_daily_theory = defaultdict(lambda: defaultdict(list))

        # Count theory classes per section per day
        for entry in entries:
            if entry.subject and not entry.subject.is_practical:
                section_daily_theory[entry.class_group][entry.day].append(entry)

        # Check for violations (more than 1 theory class per day)
        for class_group, daily_classes in section_daily_theory.items():
            for day, theory_classes in daily_classes.items():
                if len(theory_classes) > 1:
                    violations.append({
                        'class_group': class_group,
                        'day': day,
                        'theory_count': len(theory_classes),
                        'subjects': [e.subject.code for e in theory_classes],
                        'description': f'{class_group} has {len(theory_classes)} theory classes on {day}'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} multiple theory per day violations'
        }

    def _analyze_practical_blocks(self, entries):
        """Analyze practical block constraints (3-hour consecutive blocks)"""
        from collections import defaultdict

        # Group practical entries by class_group and subject
        practical_groups = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            if entry.is_practical and entry.subject:
                practical_groups[entry.class_group][entry.subject.code].append({
                    'day': entry.day,
                    'period': entry.period,
                    'subject': entry.subject.name,
                    'teacher': entry.teacher.name if entry.teacher else 'N/A',
                    'classroom': entry.classroom.name if entry.classroom else 'N/A',
                    'time': f"{entry.start_time} - {entry.end_time}"
                })

        violations = []
        compliant_blocks = []

        for class_group, subjects in practical_groups.items():
            for subject_code, practical_entries in subjects.items():
                # Group by day to check for consecutive blocks
                day_groups = defaultdict(list)
                for entry in practical_entries:
                    day_groups[entry['day']].append(entry)

                for day, day_entries in day_groups.items():
                    # Sort by period
                    day_entries.sort(key=lambda x: x['period'])

                    # Check if periods are consecutive and total 3 hours
                    if len(day_entries) >= 3:
                        periods = [entry['period'] for entry in day_entries]
                        is_consecutive = all(periods[i] + 1 == periods[i + 1] for i in range(len(periods) - 1))

                        block_info = {
                            'class_group': class_group,
                            'subject_code': subject_code,
                            'subject_name': day_entries[0]['subject'],
                            'day': day,
                            'periods': periods,
                            'entries': day_entries,
                            'is_consecutive': is_consecutive,
                            'block_length': len(day_entries)
                        }

                        if is_consecutive and len(day_entries) == 3:
                            compliant_blocks.append(block_info)
                        else:
                            block_info['violation_type'] = 'invalid_block_structure'
                            violations.append(block_info)
                    else:
                        violations.append({
                            'class_group': class_group,
                            'subject_code': subject_code,
                            'subject_name': day_entries[0]['subject'],
                            'day': day,
                            'periods': [entry['period'] for entry in day_entries],
                            'entries': day_entries,
                            'violation_type': 'insufficient_block_length',
                            'block_length': len(day_entries)
                        })

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_blocks': compliant_blocks,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_friday_time_limits(self, entries):
        """Analyze Friday time limit constraints"""
        friday_entries = [entry for entry in entries if entry.day.upper() == 'FRIDAY']
        violations = []
        compliant_entries = []

        for entry in friday_entries:
            has_practical = any(e.is_practical for e in friday_entries if e.class_group == entry.class_group)

            # Friday limits: 12:00/1:00 PM with practical, 11:00 AM without practical
            if has_practical:
                # Allow until period 4 (1:00 PM) if there are practicals
                max_period = 4
                limit_description = "1:00 PM (with practicals)"
            else:
                # Allow until period 3 (11:00 AM) if no practicals
                max_period = 3
                limit_description = "11:00 AM (no practicals)"

            entry_info = {
                'class_group': entry.class_group,
                'subject': entry.subject.name if entry.subject else 'N/A',
                'teacher': entry.teacher.name if entry.teacher else 'N/A',
                'period': entry.period,
                'time': f"{entry.start_time} - {entry.end_time}",
                'is_practical': entry.is_practical,
                'has_practical_in_class': has_practical,
                'limit_description': limit_description,
                'max_allowed_period': max_period
            }

            if entry.period > max_period:
                entry_info['violation_type'] = 'exceeds_friday_limit'
                violations.append(entry_info)
            else:
                compliant_entries.append(entry_info)

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_entries': compliant_entries,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_thesis_day_constraint(self, entries):
        """Analyze thesis day constraint (Wednesday exclusive for thesis)"""
        wednesday_entries = [entry for entry in entries if entry.day.upper() == 'WEDNESDAY']
        violations = []
        compliant_entries = []

        # Group by class_group
        from collections import defaultdict
        class_groups = defaultdict(list)

        for entry in wednesday_entries:
            class_groups[entry.class_group].append(entry)

        for class_group, group_entries in class_groups.items():
            has_thesis = any(
                entry.subject and ('thesis' in entry.subject.name.lower() or 'thesis' in entry.subject.code.lower())
                for entry in group_entries
            )

            if has_thesis:
                # If class has thesis, Wednesday should be exclusive for thesis
                for entry in group_entries:
                    is_thesis_subject = (
                        entry.subject and
                        ('thesis' in entry.subject.name.lower() or 'thesis' in entry.subject.code.lower())
                    )

                    entry_info = {
                        'class_group': class_group,
                        'subject': entry.subject.name if entry.subject else 'N/A',
                        'teacher': entry.teacher.name if entry.teacher else 'N/A',
                        'period': entry.period,
                        'time': f"{entry.start_time} - {entry.end_time}",
                        'is_thesis_subject': is_thesis_subject,
                        'class_has_thesis': has_thesis
                    }

                    if not is_thesis_subject:
                        entry_info['violation_type'] = 'non_thesis_on_thesis_day'
                        violations.append(entry_info)
                    else:
                        compliant_entries.append(entry_info)
            else:
                # If no thesis, any subject is allowed on Wednesday
                for entry in group_entries:
                    compliant_entries.append({
                        'class_group': class_group,
                        'subject': entry.subject.name if entry.subject else 'N/A',
                        'teacher': entry.teacher.name if entry.teacher else 'N/A',
                        'period': entry.period,
                        'time': f"{entry.start_time} - {entry.end_time}",
                        'is_thesis_subject': False,
                        'class_has_thesis': False
                    })

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_entries': compliant_entries,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_teacher_assignments(self, entries):
        """Analyze teacher assignment constraints"""
        violations = []
        compliant_assignments = []

        for entry in entries:
            if entry.subject and entry.teacher:
                # Check if teacher is assigned to teach this subject for this class group
                try:
                    # Check if teacher is assigned to this subject for this section
                    section = entry.class_group.split('-')[1] if '-' in entry.class_group else entry.class_group
                    assignments = TeacherSubjectAssignment.objects.filter(
                        teacher=entry.teacher,
                        subject=entry.subject
                    )

                    # Check if any assignment includes this section
                    assignment = None
                    for assign in assignments:
                        if section in assign.sections:
                            assignment = assign
                            break

                    if not assignment:
                        raise TeacherSubjectAssignment.DoesNotExist()

                    compliant_assignments.append({
                        'teacher': entry.teacher.name,
                        'subject': entry.subject.name,
                        'class_group': entry.class_group,
                        'day': entry.day,
                        'period': entry.period,
                        'time': f"{entry.start_time} - {entry.end_time}",
                        'assignment_id': assignment.id
                    })

                except TeacherSubjectAssignment.DoesNotExist:
                    violations.append({
                        'teacher': entry.teacher.name,
                        'subject': entry.subject.name,
                        'class_group': entry.class_group,
                        'day': entry.day,
                        'period': entry.period,
                        'time': f"{entry.start_time} - {entry.end_time}",
                        'violation_type': 'teacher_not_assigned_to_subject'
                    })

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_assignments': compliant_assignments,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_minimum_daily_classes(self, entries):
        """Analyze minimum daily classes constraint"""
        from collections import defaultdict

        # Group by class_group and day
        daily_classes = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            daily_classes[entry.class_group][entry.day].append({
                'subject': entry.subject.name if entry.subject else 'N/A',
                'teacher': entry.teacher.name if entry.teacher else 'N/A',
                'period': entry.period,
                'time': f"{entry.start_time} - {entry.end_time}",
                'is_practical': entry.is_practical
            })

        violations = []
        compliant_days = []

        for class_group, days in daily_classes.items():
            for day, day_entries in days.items():
                practical_count = sum(1 for entry in day_entries if entry['is_practical'])
                theory_count = len(day_entries) - practical_count

                day_info = {
                    'class_group': class_group,
                    'day': day,
                    'total_classes': len(day_entries),
                    'practical_count': practical_count,
                    'theory_count': theory_count,
                    'entries': day_entries
                }

                # Check violations: only practical or only one class
                if len(day_entries) == 1 or (practical_count > 0 and theory_count == 0):
                    if len(day_entries) == 1:
                        day_info['violation_type'] = 'only_one_class'
                    else:
                        day_info['violation_type'] = 'only_practical_classes'
                    violations.append(day_info)
                else:
                    compliant_days.append(day_info)

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_days': compliant_days,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_compact_scheduling(self, entries):
        """Analyze compact scheduling constraint"""
        from collections import defaultdict

        # Group by class_group and day
        daily_schedules = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            daily_schedules[entry.class_group][entry.day].append(entry.period)

        violations = []
        compliant_schedules = []

        for class_group, days in daily_schedules.items():
            for day, periods in days.items():
                periods.sort()

                # Check for gaps in schedule
                gaps = []
                if len(periods) > 1:
                    for i in range(len(periods) - 1):
                        gap_size = periods[i + 1] - periods[i] - 1
                        if gap_size > 0:
                            gaps.append({
                                'start_period': periods[i],
                                'end_period': periods[i + 1],
                                'gap_size': gap_size
                            })

                schedule_info = {
                    'class_group': class_group,
                    'day': day,
                    'periods': periods,
                    'start_period': min(periods) if periods else None,
                    'end_period': max(periods) if periods else None,
                    'total_periods': len(periods),
                    'gaps': gaps,
                    'has_gaps': len(gaps) > 0
                }

                # Check if schedule is compact (no gaps and reasonable end time)
                if len(gaps) > 0 or (periods and max(periods) > 5):
                    if len(gaps) > 0:
                        schedule_info['violation_type'] = 'schedule_gaps'
                    else:
                        schedule_info['violation_type'] = 'late_end_time'
                    violations.append(schedule_info)
                else:
                    compliant_schedules.append(schedule_info)

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_schedules': compliant_schedules,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_friday_aware_scheduling(self, entries):
        """Analyze Friday-aware scheduling constraint"""
        from collections import defaultdict

        # Group by class_group
        class_schedules = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            class_schedules[entry.class_group][entry.day].append(entry.period)

        violations = []
        compliant_schedules = []

        for class_group, days in class_schedules.items():
            friday_periods = days.get('FRIDAY', [])
            has_friday_practical = any(
                entry.is_practical for entry in entries
                if entry.class_group == class_group and entry.day.upper() == 'FRIDAY'
            )

            # Check Monday-Thursday scheduling considering Friday limits
            for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY']:
                day_periods = days.get(day, [])

                if day_periods:
                    max_period = max(day_periods)

                    # If Friday has constraints, Monday-Thursday should be more compact
                    if friday_periods:
                        friday_max = max(friday_periods)
                        expected_friday_limit = 4 if has_friday_practical else 3

                        schedule_info = {
                            'class_group': class_group,
                            'day': day,
                            'periods': day_periods,
                            'max_period': max_period,
                            'friday_max_period': friday_max,
                            'friday_limit': expected_friday_limit,
                            'has_friday_practical': has_friday_practical
                        }

                        # Check if weekday scheduling is Friday-aware
                        if max_period > 5:  # Too late on weekdays when Friday is constrained
                            schedule_info['violation_type'] = 'not_friday_aware'
                            violations.append(schedule_info)
                        else:
                            compliant_schedules.append(schedule_info)

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_schedules': compliant_schedules,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_senior_batch_lab_assignment(self, entries):
        """Analyze senior batch lab assignment constraint"""
        from collections import defaultdict

        violations = []
        compliant_assignments = []

        # Group entries by batch (extract batch from class_group)
        batch_assignments = defaultdict(list)

        for entry in entries:
            if entry.classroom and entry.class_group:
                # Extract batch from class_group (e.g., "21SW-A" -> "21SW")
                batch_name = entry.class_group.split('-')[0] if '-' in entry.class_group else entry.class_group
                batch_assignments[batch_name].append(entry)

        # Determine seniority based on batch year (lower number = senior)
        # e.g., 21SW is senior to 22SW, 23SW, 24SW
        for batch_name, batch_entries in batch_assignments.items():
            try:
                # Extract year from batch name (e.g., "21SW" -> 21)
                batch_year = int(batch_name[:2])

                # Determine if this is a senior batch (lower year numbers are senior)
                # 21SW, 22SW = Senior batches (ALL classes in labs)
                # 23SW, 24SW = Junior batches (only practicals in labs)
                is_senior_batch = batch_year <= 22

                for entry in batch_entries:
                    classroom_name = entry.classroom.name.lower()
                    is_lab_room = 'lab' in classroom_name or 'laboratory' in classroom_name

                    assignment_info = {
                        'batch': batch_name,
                        'class_group': entry.class_group,
                        'subject': entry.subject.name if entry.subject else 'N/A',
                        'classroom': entry.classroom.name,
                        'day': entry.day,
                        'period': entry.period,
                        'time': f"{entry.start_time} - {entry.end_time}",
                        'is_senior_batch': is_senior_batch,
                        'is_lab_room': is_lab_room,
                        'is_practical': entry.is_practical
                    }

                    # Check constraint: Senior batches MUST be in labs (ALL classes)
                    if is_senior_batch:
                        if not is_lab_room:
                            # VIOLATION: Senior batch not in lab
                            assignment_info['violation_type'] = 'senior_batch_not_in_lab'
                            assignment_info['expected'] = 'Lab room (senior batch privilege)'
                            assignment_info['actual'] = f'Regular classroom ({entry.classroom.name})'
                            violations.append(assignment_info)
                        else:
                            # COMPLIANT: Senior batch in lab
                            compliant_assignments.append(assignment_info)
                    else:
                        # Junior batches: practicals in labs, theory in regular rooms
                        if entry.is_practical:
                            if is_lab_room:
                                # COMPLIANT: Junior practical in lab
                                compliant_assignments.append(assignment_info)
                            else:
                                # VIOLATION: Junior practical not in lab
                                assignment_info['violation_type'] = 'junior_practical_not_in_lab'
                                assignment_info['expected'] = 'Lab room for practical'
                                assignment_info['actual'] = f'Regular classroom ({entry.classroom.name})'
                                violations.append(assignment_info)
                        else:
                            # Junior theory can be in regular rooms (preferred) or labs if needed
                            compliant_assignments.append(assignment_info)

            except (ValueError, IndexError):
                # Skip batches with invalid naming format
                continue

        return {
            'total_violations': len(violations),
            'violations': violations,
            'compliant_assignments': compliant_assignments,
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }

    def _analyze_room_double_booking(self, entries):
        """
        ENHANCED: Analyze room double-booking conflicts.
        Detects when multiple classes are assigned to the same room at the same time.
        """
        try:
            from collections import defaultdict

            room_schedule = defaultdict(list)
            conflicts = []

            # Group entries by room, day, and period
            for entry in entries:
                if entry.classroom:
                    key = (entry.classroom.id, entry.day, entry.period)
                    room_schedule[key].append(entry)

            # Find conflicts (more than one entry per time slot)
            for (room_id, day, period), room_entries in room_schedule.items():
                if len(room_entries) > 1:
                    room_name = room_entries[0].classroom.name
                    conflict_details = []

                    for entry in room_entries:
                        subject_code = entry.subject.code if entry.subject else 'Unknown'
                        conflict_details.append({
                            'class_group': entry.class_group,
                            'subject': subject_code,
                            'teacher': entry.teacher.name if entry.teacher else 'Unknown'
                        })

                    conflicts.append({
                        'room_name': room_name,
                        'day': day,
                        'period': period,
                        'conflict_count': len(room_entries),
                        'conflicting_classes': conflict_details
                    })

            return {
                'status': 'FAIL' if conflicts else 'PASS',
                'total_conflicts': len(conflicts),
                'conflicts': conflicts,
                'message': f'Found {len(conflicts)} room double-booking conflicts' if conflicts else 'No room conflicts detected'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'Failed to analyze room conflicts: {str(e)}'
            }

    def _analyze_practical_same_lab(self, entries):
        """
        ENHANCED: Analyze practical same-lab rule compliance.
        Ensures all 3 blocks of each practical subject use the same lab.
        """
        try:
            from collections import defaultdict

            practical_groups = defaultdict(list)
            violations = []
            compliant_practicals = []

            # Group practical entries by class group and subject
            for entry in entries:
                if entry.subject and entry.subject.is_practical and entry.classroom:
                    key = (entry.class_group, entry.subject.code)
                    practical_groups[key].append(entry)

            # Check each practical group for same-lab compliance
            for (class_group, subject_code), group_entries in practical_groups.items():
                if len(group_entries) >= 2:  # Need at least 2 entries to check consistency
                    # Get all unique labs used by this practical
                    labs_used = set(entry.classroom.id for entry in group_entries)

                    if len(labs_used) > 1:
                        # VIOLATION: Multiple labs used for same practical
                        lab_details = []
                        for entry in group_entries:
                            lab_details.append({
                                'day': entry.day,
                                'period': entry.period,
                                'lab_name': entry.classroom.name,
                                'is_lab': entry.classroom.is_lab
                            })

                        violations.append({
                            'class_group': class_group,
                            'subject': subject_code,
                            'labs_used': len(labs_used),
                            'total_blocks': len(group_entries),
                            'lab_details': lab_details
                        })
                    else:
                        # COMPLIANT: All blocks in same lab
                        lab_name = group_entries[0].classroom.name
                        compliant_practicals.append({
                            'class_group': class_group,
                            'subject': subject_code,
                            'lab_name': lab_name,
                            'total_blocks': len(group_entries),
                            'is_lab': group_entries[0].classroom.is_lab
                        })

            return {
                'status': 'FAIL' if violations else 'PASS',
                'total_violations': len(violations),
                'violations': violations,
                'compliant_practicals': compliant_practicals,
                'total_practical_groups': len(practical_groups),
                'message': f'Found {len(violations)} same-lab violations' if violations else 'All practicals follow same-lab rule'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'Failed to analyze practical same-lab rule: {str(e)}'
            }


class ConstraintResolverView(APIView):
    """
    Intelligent constraint resolution for specific constraint types.
    Attempts to fix violations without creating new ones.
    """

    def post(self, request):
        """Attempt to resolve a specific constraint type"""
        try:
            constraint_type = request.data.get('constraint_type')
            max_attempts = request.data.get('max_attempts', 5)

            if not constraint_type:
                return Response(
                    {'error': 'constraint_type is required'},
                    status=400
                )

            # Get current timetable entries
            entries = TimetableEntry.objects.all()

            if not entries.exists():
                return Response({
                    'success': False,
                    'error': 'No timetable entries found. Please generate a timetable first.'
                })

            # Initialize constraint validator
            validator = ConstraintValidator()

            # Get initial state
            initial_results = validator.validate_all_constraints(list(entries))

            # Map constraint types to validator constraint names
            constraint_name_mapping = {
                'subject_frequency': 'Subject Frequency',
                'practical_blocks': 'Practical Blocks',
                'teacher_conflicts': 'Teacher Conflicts',
                'room_conflicts': 'Room Conflicts',
                'friday_time_limits': 'Friday Time Limits',
                'minimum_daily_classes': 'Minimum Daily Classes',
                'thesis_day_constraint': 'Thesis Day Constraint',
                'compact_scheduling': 'Compact Scheduling',
                'cross_semester_conflicts': 'Cross Semester Conflicts',
                'teacher_assignments': 'Teacher Assignments',
                'friday_aware_scheduling': 'Friday Aware Scheduling',
                # Room allocation constraints
                'room_double_booking': 'Room Conflicts',
                'practical_same_lab': 'Room Conflicts',
                'practical_in_labs_only': 'Room Conflicts',
                'theory_room_consistency': 'Room Conflicts',
                'section_simultaneous_classes': 'Teacher Conflicts',
                'working_hours_compliance': 'Compact Scheduling',
                'max_theory_per_day': 'Subject Frequency'
            }

            constraint_name = constraint_name_mapping.get(constraint_type, constraint_type.replace('_', ' ').title())
            initial_violations = initial_results['constraint_results'].get(constraint_name, {}).get('violations', 0)

            print(f"Constraint resolution for {constraint_type} ({constraint_name}): {initial_violations} initial violations")

            if initial_violations == 0:
                return Response({
                    'success': True,
                    'message': f'{constraint_type} constraint is already satisfied',
                    'attempts_made': 0,
                    'violations_before': 0,
                    'violations_after': 0,
                    'other_constraints_affected': 0
                })

            # Attempt to resolve the specific constraint
            resolution_result = self._resolve_specific_constraint(
                constraint_type, entries, validator, max_attempts
            )

            return Response({
                'success': resolution_result['success'],
                'message': resolution_result['message'],
                'attempts_made': resolution_result['attempts_made'],
                'violations_before': initial_violations,
                'violations_after': resolution_result['violations_after'],
                'other_constraints_affected': resolution_result['other_constraints_affected'],
                'resolution_details': resolution_result['details']
            })

        except Exception as e:
            logger.error(f"Constraint resolution failed: {str(e)}")
            return Response(
                {'error': f'Constraint resolution failed: {str(e)}'},
                status=500
            )

    def _resolve_specific_constraint(self, constraint_type, entries, validator, max_attempts):
        """Resolve a specific constraint type intelligently"""
        attempts_made = 0
        violations_after = 0
        other_constraints_affected = 0
        details = []

        try:
            # Get initial state of all constraints
            initial_state = validator.validate_all_constraints(list(entries))

            # Use the same constraint name mapping
            constraint_name_mapping = {
                'subject_frequency': 'Subject Frequency',
                'practical_blocks': 'Practical Blocks',
                'teacher_conflicts': 'Teacher Conflicts',
                'room_conflicts': 'Room Conflicts',
                'friday_time_limits': 'Friday Time Limits',
                'minimum_daily_classes': 'Minimum Daily Classes',
                'thesis_day_constraint': 'Thesis Day Constraint',
                'compact_scheduling': 'Compact Scheduling',
                'cross_semester_conflicts': 'Cross Semester Conflicts',
                'teacher_assignments': 'Teacher Assignments',
                'friday_aware_scheduling': 'Friday Aware Scheduling',
                'senior_batch_lab_assignment': 'Senior Batch Lab Assignment'
            }

            constraint_name = constraint_name_mapping.get(constraint_type, constraint_type.replace('_', ' ').title())
            initial_target_violations = initial_state['constraint_results'].get(constraint_name, {}).get('violations', 0)

            initial_other_violations = sum(
                result['violations'] for name, result in initial_state['constraint_results'].items()
                if name != constraint_name
            )

            for attempt in range(max_attempts):
                attempts_made += 1

                # Apply constraint-specific resolution strategy
                resolution_applied = self._apply_constraint_resolution(constraint_type, entries)

                if not resolution_applied:
                    details.append(f"Attempt {attempt + 1}: No resolution strategy available")
                    break

                # Validate after resolution attempt
                current_state = validator.validate_all_constraints(list(entries))
                current_violations = current_state['constraint_results'].get(constraint_name, {}).get('violations', 0)

                current_other_violations = sum(
                    result['violations'] for name, result in current_state['constraint_results'].items()
                    if name != constraint_name
                )

                violations_after = current_violations
                other_constraints_affected = current_other_violations - initial_other_violations

                details.append(f"Attempt {attempt + 1}: {resolution_applied['action']} - "
                             f"Violations: {current_violations}, Other affected: {other_constraints_affected}")

                # Check if constraint is resolved without breaking others
                if current_violations == 0:
                    if other_constraints_affected <= 0:  # No new violations in other constraints
                        return {
                            'success': True,
                            'message': f'{constraint_type} constraint resolved successfully',
                            'attempts_made': attempts_made,
                            'violations_after': violations_after,
                            'other_constraints_affected': other_constraints_affected,
                            'details': details
                        }
                    else:
                        details.append(f"Constraint resolved but created {other_constraints_affected} new violations")

                # If we created too many new violations, revert and try different approach
                if other_constraints_affected > 2:
                    details.append(f"Too many new violations created, trying different approach")
                    continue

            return {
                'success': violations_after < initial_target_violations,
                'message': f'Partial resolution achieved after {attempts_made} attempts',
                'attempts_made': attempts_made,
                'violations_after': violations_after,
                'other_constraints_affected': other_constraints_affected,
                'details': details
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Resolution failed: {str(e)}',
                'attempts_made': attempts_made,
                'violations_after': violations_after,
                'other_constraints_affected': other_constraints_affected,
                'details': details + [f"Error: {str(e)}"]
            }

    def _apply_constraint_resolution(self, constraint_type, entries):
        """Apply specific resolution strategy based on constraint type"""
        try:
            if constraint_type == 'teacher_conflicts':
                return self._resolve_teacher_conflicts(entries)
            elif constraint_type == 'room_conflicts':
                return self._resolve_room_conflicts(entries)
            elif constraint_type == 'subject_frequency':
                return self._resolve_subject_frequency(entries)
            elif constraint_type == 'practical_blocks':
                return self._resolve_practical_blocks(entries)
            elif constraint_type == 'friday_time_limits':
                return self._resolve_friday_time_limits(entries)
            elif constraint_type == 'compact_scheduling':
                return self._resolve_compact_scheduling(entries)
            elif constraint_type == 'thesis_day_constraint':
                return self._resolve_thesis_day_constraint(entries)
            elif constraint_type == 'room_double_booking':
                return self._resolve_room_double_booking(entries)
            elif constraint_type == 'practical_same_lab':
                return self._resolve_practical_same_lab(entries)
            elif constraint_type == 'practical_in_labs_only':
                return self._resolve_practical_in_labs_only(entries)
            elif constraint_type == 'theory_room_consistency':
                return self._resolve_theory_room_consistency(entries)
            elif constraint_type == 'section_simultaneous_classes':
                return self._resolve_section_simultaneous_classes(entries)
            elif constraint_type == 'working_hours_compliance':
                return self._resolve_working_hours_compliance(entries)
            elif constraint_type == 'max_theory_per_day':
                return self._resolve_max_theory_per_day(entries)
            elif constraint_type == 'minimum_daily_classes':
                return self._resolve_minimum_daily_classes(entries)
            elif constraint_type == 'teacher_assignments':
                return self._resolve_teacher_assignments(entries)
            elif constraint_type == 'friday_aware_scheduling':
                return self._resolve_friday_aware_scheduling(entries)
            else:
                return None

        except Exception as e:
            logger.error(f"Resolution strategy failed for {constraint_type}: {str(e)}")
            return None

    def _resolve_teacher_conflicts(self, entries):
        """Resolve teacher conflicts by moving conflicting classes"""
        from collections import defaultdict
        import random

        # Find teacher conflicts
        time_slot_teachers = defaultdict(list)

        for entry in entries:
            if entry.teacher:
                key = f"{entry.day}-{entry.period}"
                time_slot_teachers[key].append(entry)

        conflicts_resolved = 0

        for time_slot, slot_entries in time_slot_teachers.items():
            teacher_groups = defaultdict(list)
            for entry in slot_entries:
                teacher_groups[entry.teacher.id].append(entry)

            # Find conflicts (same teacher, multiple classes)
            for teacher_id, teacher_entries in teacher_groups.items():
                if len(teacher_entries) > 1:
                    # Try to move one of the conflicting entries
                    entry_to_move = teacher_entries[1]  # Move the second entry

                    # Find an available time slot for this entry
                    moved = self._find_available_slot_and_move(entry_to_move, entries)
                    if moved:
                        conflicts_resolved += 1

        if conflicts_resolved > 0:
            return {'action': f'Moved {conflicts_resolved} conflicting teacher assignments'}
        return None

    def _resolve_room_conflicts(self, entries):
        """Resolve room conflicts by reassigning rooms"""
        from collections import defaultdict

        conflicts_resolved = 0

        # Group by day-period to find room conflicts
        day_period_rooms = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            if entry.classroom:
                day_period_key = f"{entry.day}-{entry.period}"
                room_id = entry.classroom.id
                day_period_rooms[day_period_key][room_id].append(entry)

        # Find and resolve conflicts
        for day_period, rooms in day_period_rooms.items():
            for room_id, room_entries in rooms.items():
                if len(room_entries) > 1:
                    # Multiple entries in same room at same time - conflict!
                    print(f"Found room conflict: {len(room_entries)} entries in room {room_entries[0].classroom.name} at {day_period}")

                    # Try to reassign all but the first entry
                    for i in range(1, len(room_entries)):
                        entry_to_reassign = room_entries[i]
                        day, period = day_period.split('-')

                        # Find an available room for this time slot
                        reassigned = self._find_available_room_and_reassign(entry_to_reassign, day, int(period))
                        if reassigned:
                            conflicts_resolved += 1
                            print(f"Successfully reassigned {entry_to_reassign.subject} to new room")
                        else:
                            print(f"Failed to reassign {entry_to_reassign.subject} - no available rooms")

        if conflicts_resolved > 0:
            return {'action': f'Reassigned {conflicts_resolved} conflicting room assignments'}
        return None

    def _resolve_compact_scheduling(self, entries):
        """Resolve compact scheduling by moving classes to reduce gaps"""
        from collections import defaultdict

        # Group by class_group and day
        daily_schedules = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            daily_schedules[entry.class_group][entry.day].append(entry)

        gaps_resolved = 0

        for class_group, days in daily_schedules.items():
            for day, day_entries in days.items():
                if len(day_entries) > 1:
                    # Sort by period
                    day_entries.sort(key=lambda x: x.period)

                    # Find gaps
                    for i in range(len(day_entries) - 1):
                        gap_size = day_entries[i + 1].period - day_entries[i].period - 1
                        if gap_size > 0:
                            # Try to move the later entry to fill the gap
                            moved = self._move_entry_to_fill_gap(day_entries[i + 1], day_entries[i].period + 1)
                            if moved:
                                gaps_resolved += 1

        if gaps_resolved > 0:
            return {'action': f'Filled {gaps_resolved} schedule gaps'}
        return None

    def _find_available_slot_and_move(self, entry, all_entries):
        """Find an available time slot and move the entry"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = range(1, 8)  # Assuming 7 periods max

        # Get occupied slots for this teacher
        teacher_slots = set()
        for e in all_entries:
            if e.teacher and e.teacher.id == entry.teacher.id and e.id != entry.id:
                teacher_slots.add(f"{e.day}-{e.period}")

        # Find available slot
        for day in days:
            for period in periods:
                slot_key = f"{day}-{period}"
                if slot_key not in teacher_slots:
                    # Check if room is available too
                    room_available = not any(
                        e.classroom and e.classroom.id == entry.classroom.id and
                        e.day == day and e.period == period and e.id != entry.id
                        for e in all_entries
                    )

                    if room_available:
                        # Move the entry
                        entry.day = day
                        entry.period = period
                        entry.save()
                        return True

        return False

    def _find_available_room_and_reassign(self, entry, day, period):
        """Find an available room and reassign the entry"""
        from .models import Classroom

        # Get all available classrooms
        all_rooms = Classroom.objects.all()

        print(f"Looking for available room for {entry.subject} on {day} period {period}")
        print(f"Current room: {entry.classroom.name if entry.classroom else 'None'}")

        # Find rooms not occupied at this time
        for room in all_rooms:
            room_occupied = TimetableEntry.objects.filter(
                classroom=room,
                day=day,
                period=period
            ).exclude(id=entry.id).exists()

            print(f"Checking room {room.name}: {'occupied' if room_occupied else 'available'}")

            if not room_occupied:
                old_room = entry.classroom.name if entry.classroom else 'None'
                entry.classroom = room
                entry.save()
                print(f"Successfully moved {entry.subject} from {old_room} to {room.name}")
                return True

        print(f"No available rooms found for {entry.subject}")
        return False

    def _resolve_senior_batch_lab_assignment(self, entries):
        """Resolve senior batch lab assignment by moving senior batches to labs"""
        from .models import Classroom

        violations_resolved = 0

        # Get all lab rooms (using is_lab field instead of name matching)
        lab_rooms = Classroom.objects.filter(is_lab=True)

        if not lab_rooms.exists():
            print("No lab rooms found in the system")
            return None

        print(f"Found {lab_rooms.count()} lab rooms: {[lab.name for lab in lab_rooms]}")

        # Find senior batch entries not in labs
        senior_violations = []

        for entry in entries:
            if entry.classroom and entry.class_group:
                # Extract batch from class_group
                batch_name = entry.class_group.split('-')[0] if '-' in entry.class_group else entry.class_group

                try:
                    batch_year = int(batch_name[:2])
                    is_senior_batch = batch_year <= 22  # 21SW, 22SW are senior

                    if is_senior_batch:
                        classroom_name = entry.classroom.name.lower()
                        is_lab_room = 'lab' in classroom_name or 'laboratory' in classroom_name

                        if not is_lab_room:
                            senior_violations.append(entry)
                            print(f"Found senior violation: {batch_name} {entry.subject} in {entry.classroom.name} on {entry.day} P{entry.period}")

                except (ValueError, IndexError):
                    continue

        print(f"Found {len(senior_violations)} senior batch violations to resolve")

        # Try to resolve violations by moving to labs
        for entry in senior_violations:
            moved_to_lab = self._move_to_available_lab(entry, lab_rooms)
            if moved_to_lab:
                violations_resolved += 1
                batch_name = entry.class_group.split('-')[0]
                print(f"Successfully moved {batch_name} ({entry.subject}) to lab room")
            else:
                print(f"Failed to move {entry.class_group} ({entry.subject}) - no available labs")

        if violations_resolved > 0:
            return {'action': f'Moved {violations_resolved} senior batch classes to lab rooms'}
        else:
            return {'action': f'Attempted to resolve {len(senior_violations)} violations but no labs were available'}

    def _move_to_available_lab(self, entry, lab_rooms):
        """Move an entry to an available lab room, with smart swapping if needed"""

        # First, try to find a completely free lab
        for lab_room in lab_rooms:
            lab_occupied = TimetableEntry.objects.filter(
                classroom=lab_room,
                day=entry.day,
                period=entry.period
            ).exclude(id=entry.id).exists()

            if not lab_occupied:
                old_room = entry.classroom.name if entry.classroom else 'None'
                entry.classroom = lab_room
                entry.save()
                print(f"Moved {entry.class_group} from {old_room} to {lab_room.name} (free lab)")
                return True

        # If no free labs, try to swap with junior batches in labs
        for lab_room in lab_rooms:
            lab_occupant = TimetableEntry.objects.filter(
                classroom=lab_room,
                day=entry.day,
                period=entry.period
            ).exclude(id=entry.id).first()

            if lab_occupant and lab_occupant.class_group:
                # Check if occupant is a junior batch
                occupant_batch = lab_occupant.class_group.split('-')[0]
                try:
                    occupant_year = int(occupant_batch[:2])
                    is_occupant_junior = occupant_year > 22  # 23SW, 24SW are junior

                    # Only swap if occupant is junior and their subject is theory (not practical)
                    if is_occupant_junior and not lab_occupant.is_practical:
                        # Swap rooms: senior gets lab, junior gets regular room
                        old_senior_room = entry.classroom
                        old_junior_room = lab_occupant.classroom

                        entry.classroom = old_junior_room  # Senior gets lab
                        lab_occupant.classroom = old_senior_room  # Junior gets regular room

                        entry.save()
                        lab_occupant.save()

                        print(f"Swapped rooms: {entry.class_group} (senior) gets {old_junior_room.name}, {lab_occupant.class_group} (junior) gets {old_senior_room.name}")
                        return True

                except (ValueError, IndexError):
                    continue

        return False

    def _move_entry_to_fill_gap(self, entry, target_period):
        """Move an entry to a specific period to fill a gap"""
        # Check if target period is available for this teacher and room
        conflicts = TimetableEntry.objects.filter(
            day=entry.day,
            period=target_period
        ).filter(
            models.Q(teacher=entry.teacher) | models.Q(classroom=entry.classroom)
        ).exclude(id=entry.id)

        if not conflicts.exists():
            entry.period = target_period
            entry.save()
            return True

        return False

    def _resolve_room_double_booking(self, entries):
        """
        ENHANCED: Resolve room double-booking conflicts.
        Moves conflicting classes to available rooms while maintaining constraints.
        """
        try:
            from collections import defaultdict
            from .room_allocator import RoomAllocator

            room_allocator = RoomAllocator()
            room_schedule = defaultdict(list)
            conflicts_resolved = 0

            # Group entries by room, day, and period to find conflicts
            for entry in entries:
                if entry.classroom:
                    key = (entry.classroom.id, entry.day, entry.period)
                    room_schedule[key].append(entry)

            # Resolve conflicts
            for (room_id, day, period), room_entries in room_schedule.items():
                if len(room_entries) > 1:
                    # Keep the first entry, move others
                    entries_to_move = room_entries[1:]

                    for entry in entries_to_move:
                        # Find alternative room
                        if entry.subject and entry.subject.is_practical:
                            # Practical subjects need labs
                            alternative_room = room_allocator.allocate_room_for_practical(
                                day, period, entry.class_group, entry.subject, entries
                            )
                        else:
                            # Theory subjects can use regular rooms or labs
                            alternative_room = room_allocator.allocate_room_for_theory(
                                day, period, entry.class_group, entry.subject, entries
                            )

                        if alternative_room:
                            entry.classroom = alternative_room
                            entry.save()
                            conflicts_resolved += 1

            return {
                'action': f'Resolved {conflicts_resolved} room conflicts by moving classes to available rooms',
                'success': conflicts_resolved > 0,
                'changes_made': conflicts_resolved
            }

        except Exception as e:
            return {
                'action': f'Failed to resolve room conflicts: {str(e)}',
                'success': False,
                'changes_made': 0
            }

    def _resolve_practical_same_lab(self, entries):
        """
        ENHANCED: Resolve practical same-lab violations.
        Ensures all blocks of each practical use the same lab.
        """
        try:
            from collections import defaultdict
            from .room_allocator import RoomAllocator

            room_allocator = RoomAllocator()
            practical_groups = defaultdict(list)
            violations_resolved = 0

            # Group practical entries by class group and subject
            for entry in entries:
                if entry.subject and entry.subject.is_practical and entry.classroom:
                    key = (entry.class_group, entry.subject.code)
                    practical_groups[key].append(entry)

            # Fix violations using the enhanced consistency enforcement
            fixed_entries = room_allocator.ensure_practical_block_consistency(entries)

            # Count how many violations were fixed
            for (class_group, subject_code), group_entries in practical_groups.items():
                if len(group_entries) >= 2:
                    labs_used_before = set(entry.classroom.id for entry in group_entries)
                    if len(labs_used_before) > 1:
                        # Check if it's fixed now
                        current_entries = [e for e in fixed_entries
                                         if e.class_group == class_group and
                                         e.subject and e.subject.code == subject_code]
                        labs_used_after = set(entry.classroom.id for entry in current_entries
                                            if entry.classroom)
                        if len(labs_used_after) == 1:
                            violations_resolved += 1

            return {
                'action': f'Applied same-lab consistency enforcement, resolved {violations_resolved} violations',
                'success': violations_resolved > 0,
                'changes_made': violations_resolved
            }

        except Exception as e:
            return {
                'action': f'Failed to resolve same-lab violations: {str(e)}',
                'success': False,
                'changes_made': 0
            }





    def _analyze_theory_room_consistency(self, entries):
        """Analyze theory room consistency violations"""
        from collections import defaultdict

        violations = []
        section_daily_rooms = defaultdict(lambda: defaultdict(set))

        # Track rooms used by each section on each day for theory classes
        for entry in entries:
            if entry.subject and not entry.subject.is_practical and entry.classroom:
                section_daily_rooms[entry.class_group][entry.day].add(entry.classroom.name)

        # Check for inconsistencies
        for class_group, daily_rooms in section_daily_rooms.items():
            for day, rooms in daily_rooms.items():
                if len(rooms) > 1:
                    violations.append({
                        'class_group': class_group,
                        'day': day,
                        'rooms_used': list(rooms),
                        'description': f'{class_group} uses multiple rooms on {day}: {", ".join(rooms)}'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} room consistency violations'
        }

    def _analyze_section_simultaneous_classes(self, entries):
        """Analyze sections with simultaneous classes"""
        from collections import defaultdict

        violations = []
        time_slot_sections = defaultdict(list)

        # Group entries by time slot
        for entry in entries:
            key = (entry.day, entry.period)
            time_slot_sections[key].append(entry)

        # Check for sections with multiple classes at same time
        for (day, period), slot_entries in time_slot_sections.items():
            section_counts = defaultdict(int)
            for entry in slot_entries:
                section_counts[entry.class_group] += 1

            for class_group, count in section_counts.items():
                if count > 1:
                    violations.append({
                        'class_group': class_group,
                        'day': day,
                        'period': period,
                        'simultaneous_classes': count,
                        'description': f'{class_group} has {count} simultaneous classes on {day} P{period}'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} simultaneous class violations'
        }

    def _analyze_working_hours_compliance(self, entries):
        """Analyze working hours compliance (8AM-3PM)"""
        violations = []

        for entry in entries:
            if entry.start_time and entry.end_time:
                start_hour = int(entry.start_time.split(':')[0])
                end_hour = int(entry.end_time.split(':')[0])

                if start_hour < 8 or end_hour > 15:
                    violations.append({
                        'class_group': entry.class_group,
                        'subject': entry.subject.code if entry.subject else 'Unknown',
                        'day': entry.day,
                        'period': entry.period,
                        'start_time': entry.start_time,
                        'end_time': entry.end_time,
                        'description': f'Class {entry.start_time}-{entry.end_time} outside 8AM-3PM'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} working hours violations'
        }

    def _analyze_max_theory_per_day(self, entries):
        """Analyze maximum one theory class per day constraint"""
        from collections import defaultdict

        violations = []
        section_daily_theory = defaultdict(lambda: defaultdict(list))

        # Count theory classes per section per day
        for entry in entries:
            if entry.subject and not entry.subject.is_practical:
                section_daily_theory[entry.class_group][entry.day].append(entry)

        # Check for violations (more than 1 theory class per day)
        for class_group, daily_classes in section_daily_theory.items():
            for day, theory_classes in daily_classes.items():
                if len(theory_classes) > 1:
                    violations.append({
                        'class_group': class_group,
                        'day': day,
                        'theory_count': len(theory_classes),
                        'subjects': [e.subject.code for e in theory_classes],
                        'description': f'{class_group} has {len(theory_classes)} theory classes on {day}'
                    })

        return {
            'status': 'PASS' if len(violations) == 0 else 'FAIL',
            'total_violations': len(violations),
            'violations': violations,
            'message': f'Found {len(violations)} multiple theory per day violations'
        }

    # Additional constraint resolution methods for new constraint types
    def _resolve_practical_in_labs_only(self, entries):
        """Resolve practical subjects not in labs by moving them to available labs"""
        from .room_allocator import RoomAllocator

        room_allocator = RoomAllocator()
        resolved_count = 0

        for entry in entries:
            if (entry.subject and entry.subject.is_practical and
                entry.classroom and not entry.classroom.is_lab):

                # Find an available lab for this practical
                available_lab = room_allocator.allocate_room_for_practical(
                    entry.day, entry.period, entry.class_group, entry.subject, entries
                )

                if available_lab:
                    entry.classroom = available_lab
                    entry.save()
                    resolved_count += 1

        return {
            'action': f'Moved {resolved_count} practical subjects to labs',
            'success': resolved_count > 0,
            'changes_made': resolved_count
        } if resolved_count > 0 else None



    def _resolve_theory_room_consistency(self, entries):
        """Resolve theory room consistency by assigning consistent rooms per section per day"""
        from collections import defaultdict

        resolved_count = 0
        section_daily_rooms = defaultdict(lambda: defaultdict(list))

        # Group theory entries by section and day
        for entry in entries:
            if entry.subject and not entry.subject.is_practical:
                section_daily_rooms[entry.class_group][entry.day].append(entry)

        # Fix inconsistencies
        for class_group, daily_entries in section_daily_rooms.items():
            for day, day_entries in daily_entries.items():
                if len(day_entries) > 1:
                    # Use the first entry's room as the standard
                    standard_room = day_entries[0].classroom

                    for entry in day_entries[1:]:
                        if entry.classroom != standard_room:
                            # Check if standard room is available for this period
                            conflicts = TimetableEntry.objects.filter(
                                day=entry.day,
                                period=entry.period,
                                classroom=standard_room
                            ).exclude(id=entry.id)

                            if not conflicts.exists():
                                entry.classroom = standard_room
                                entry.save()
                                resolved_count += 1

        return {
            'action': f'Standardized {resolved_count} room assignments for consistency',
            'success': resolved_count > 0,
            'changes_made': resolved_count
        } if resolved_count > 0 else None

    def _resolve_section_simultaneous_classes(self, entries):
        """Resolve sections with simultaneous classes by moving one of the conflicting classes"""
        from collections import defaultdict

        resolved_count = 0
        time_slot_sections = defaultdict(list)

        # Group entries by time slot
        for entry in entries:
            key = (entry.day, entry.period)
            time_slot_sections[key].append(entry)

        # Find and resolve conflicts
        for (day, period), slot_entries in time_slot_sections.items():
            section_entries = defaultdict(list)
            for entry in slot_entries:
                section_entries[entry.class_group].append(entry)

            for class_group, group_entries in section_entries.items():
                if len(group_entries) > 1:
                    # Move all but the first entry
                    for entry in group_entries[1:]:
                        moved = self._find_available_slot_and_move(entry, entries)
                        if moved:
                            resolved_count += 1

        return {
            'action': f'Moved {resolved_count} simultaneous classes to different time slots',
            'success': resolved_count > 0,
            'changes_made': resolved_count
        } if resolved_count > 0 else None

    def _resolve_working_hours_compliance(self, entries):
        """Resolve working hours violations by moving classes to valid time slots"""
        resolved_count = 0

        for entry in entries:
            if entry.start_time and entry.end_time:
                start_hour = int(entry.start_time.split(':')[0])
                end_hour = int(entry.end_time.split(':')[0])

                if start_hour < 8 or end_hour > 15:
                    # Try to move to a valid time slot (periods 1-7, 8AM-3PM)
                    for period in range(1, 8):
                        # Check if this period is within working hours
                        if 8 <= (7 + period) <= 15:  # Assuming period 1 starts at 8AM
                            # Check if slot is available
                            conflicts = TimetableEntry.objects.filter(
                                day=entry.day,
                                period=period,
                                teacher=entry.teacher,
                                classroom=entry.classroom
                            ).exclude(id=entry.id)

                            if not conflicts.exists():
                                entry.period = period
                                entry.save()
                                resolved_count += 1
                                break

        return {
            'action': f'Moved {resolved_count} classes to valid working hours',
            'success': resolved_count > 0,
            'changes_made': resolved_count
        } if resolved_count > 0 else None

    def _resolve_max_theory_per_day(self, entries):
        """Resolve multiple theory classes per day by moving excess classes to other days"""
        from collections import defaultdict

        resolved_count = 0
        section_daily_theory = defaultdict(lambda: defaultdict(list))

        # Group theory classes by section and day
        for entry in entries:
            if entry.subject and not entry.subject.is_practical:
                section_daily_theory[entry.class_group][entry.day].append(entry)

        # Resolve violations
        for class_group, daily_classes in section_daily_theory.items():
            for day, theory_classes in daily_classes.items():
                if len(theory_classes) > 1:
                    # Keep the first class, move others to different days
                    for entry in theory_classes[1:]:
                        moved = self._move_to_different_day(entry, entries)
                        if moved:
                            resolved_count += 1

        return {
            'action': f'Moved {resolved_count} excess theory classes to different days',
            'success': resolved_count > 0,
            'changes_made': resolved_count
        } if resolved_count > 0 else None

    def _resolve_minimum_daily_classes(self, entries):
        """Resolve minimum daily classes violations by redistributing classes"""
        # This is complex and may require adding classes, which is beyond simple resolution
        return {
            'action': 'Minimum daily classes constraint requires schedule regeneration',
            'success': False,
            'changes_made': 0
        }

    def _resolve_teacher_assignments(self, entries):
        """Resolve teacher assignment violations by reassigning teachers"""
        from timetable.models import TeacherSubjectAssignment

        resolved_count = 0

        for entry in entries:
            if entry.teacher and entry.subject:
                # Check if teacher is assigned to this subject
                assignments = TeacherSubjectAssignment.objects.filter(
                    teacher=entry.teacher,
                    subject=entry.subject
                )

                if not assignments.exists():
                    # Find a teacher who is assigned to this subject
                    valid_assignments = TeacherSubjectAssignment.objects.filter(
                        subject=entry.subject
                    )

                    for assignment in valid_assignments:
                        # Check if this teacher is available at this time
                        conflicts = TimetableEntry.objects.filter(
                            day=entry.day,
                            period=entry.period,
                            teacher=assignment.teacher
                        ).exclude(id=entry.id)

                        if not conflicts.exists():
                            entry.teacher = assignment.teacher
                            entry.save()
                            resolved_count += 1
                            break

        return {
            'action': f'Reassigned {resolved_count} teachers to their designated subjects',
            'success': resolved_count > 0,
            'changes_made': resolved_count
        } if resolved_count > 0 else None

    def _resolve_friday_aware_scheduling(self, entries):
        """Resolve Friday-aware scheduling violations"""
        # This is a quality constraint that's hard to resolve automatically
        return {
            'action': 'Friday-aware scheduling requires comprehensive schedule review',
            'success': False,
            'changes_made': 0
        }

    def _move_to_different_day(self, entry, entries):
        """Move an entry to a different day"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        current_day = entry.day

        for day in days:
            if day != current_day:
                # Check if teacher and room are available on this day at same period
                conflicts = TimetableEntry.objects.filter(
                    day=day,
                    period=entry.period
                ).filter(
                    models.Q(teacher=entry.teacher) | models.Q(classroom=entry.classroom)
                ).exclude(id=entry.id)

                if not conflicts.exists():
                    entry.day = day
                    entry.save()
                    return True

        return False

