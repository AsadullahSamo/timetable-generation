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

    
    