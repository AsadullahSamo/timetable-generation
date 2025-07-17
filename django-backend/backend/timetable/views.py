from rest_framework import viewsets
from .models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config, ClassGroup
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ScheduleConfig, TimetableEntry
from celery.result import AsyncResult
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from .algorithms.advanced_scheduler import AdvancedTimetableScheduler
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
    ClassGroupSerializer
)

from .tasks import (
    generate_timetable_async,
    validate_constraints_async,
    optimize_timetable_async,
    generate_timetable_report
)

logger = logging.getLogger(__name__)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer

class ScheduleConfigViewSet(viewsets.ModelViewSet):
    queryset = ScheduleConfig.objects.all()
    serializer_class = ScheduleConfigSerializer

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = TimetableEntry.objects.all()
    serializer_class = TimetableEntrySerializer

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
            # Create scheduler instance
            scheduler = AdvancedTimetableScheduler(config)
            # Generate timetable
            timetable = scheduler.generate_timetable()
            # Save entries to database
            TimetableEntry.objects.all().delete()  # Clear existing entries
            entries_to_create = []
            for entry in timetable['entries']:
                # Remove (PR) from subject name if present
                subject_name = entry['subject'].replace(' (PR)', '')
                entries_to_create.append(TimetableEntry(
                    day=entry['day'],
                    period=entry['period'],
                    subject=Subject.objects.get(name=subject_name),
                    teacher=Teacher.objects.get(name=entry['teacher']),
                    classroom=Classroom.objects.get(name=entry['classroom']),
                    class_group=entry['class_group'],
                    start_time=entry['start_time'],
                    end_time=entry['end_time'],
                    is_practical='(PR)' in entry['subject']
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
            entries = TimetableEntry.objects.all().order_by('day', 'period')
            
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
            
            return Response({
                'days': config.days,
                'timeSlots': time_slots,
                'entries': formatted_entries
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
    
    
    