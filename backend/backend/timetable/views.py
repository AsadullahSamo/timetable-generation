from rest_framework import viewsets
from .models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config, ClassGroup
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ScheduleConfig, TimetableEntry
from celery.result import AsyncResult
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from .algorithms.scheduler import TimetableScheduler
import logging
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator

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


class TimetableView(APIView):
    def _convert_config_to_schedule_config(self, config):
        """Convert Config model to ScheduleConfig format for algorithm compatibility"""
        from collections import namedtuple

        # Get class groups from ClassGroup model
        class_groups_data = ClassGroup.objects.all()
        all_class_groups = []
        for cg in class_groups_data:
            all_class_groups.extend(cg.class_groups)

        # If no class groups found, use default
        if not all_class_groups:
            all_class_groups = ['CS-1A', 'CS-1B', 'CS-2A', 'CS-2B']

        # Convert generated_periods to period names
        period_names = []
        if config.generated_periods:
            first_day_periods = list(config.generated_periods.values())[0]
            period_names = [f"Period {i+1}" for i in range(len(first_day_periods))]
        else:
            period_names = [f"Period {i+1}" for i in range(config.periods)]

        # Create a ScheduleConfig-like object
        ScheduleConfigLike = namedtuple('ScheduleConfigLike', [
            'id', 'name', 'days', 'periods', 'start_time', 'lesson_duration',
            'constraints', 'class_groups'
        ])

        return ScheduleConfigLike(
            id=config.id,
            name=config.name,
            days=config.days,
            periods=period_names,
            start_time=config.start_time,
            lesson_duration=config.lesson_duration,
            constraints={},  # Default empty constraints
            class_groups=all_class_groups
        )

    def get(self, request):
        try:
            config = ScheduleConfig.objects.latest('id')
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
            # Try to get the latest Config from frontend first
            frontend_config = Config.objects.filter(
                generated_periods__isnull=False
            ).exclude(generated_periods={}).order_by('-id').first()

            if frontend_config:
                # Convert Config to ScheduleConfig format
                config = self._convert_config_to_schedule_config(frontend_config)
            else:
                # Fallback to existing ScheduleConfig
                config = ScheduleConfig.objects.latest('id')
            
            # Get active constraints from request
            import json
            try:
                if hasattr(request, 'data'):
                    constraints = request.data.get('constraints', [])
                else:
                    # Parse JSON body for regular Django requests
                    body = json.loads(request.body.decode('utf-8')) if request.body else {}
                    constraints = body.get('constraints', [])
            except (json.JSONDecodeError, AttributeError):
                constraints = []
            
            # Update config with the constraints from the request
            # Note: If config is a namedtuple, we can't modify it, but constraints are passed to scheduler separately
            
            # Create scheduler instance
            scheduler = TimetableScheduler(config)
            
            # Generate timetable
            timetable = scheduler.generate()
            
            # Save entries to database
            TimetableEntry.objects.all().delete()  # Clear existing entries
            
            entries_to_create = []
            for entry in timetable['entries']:
                # Smart subject name resolution
                subject_name = entry['subject']
                try:
                    # Try exact match first
                    subject = Subject.objects.get(name=subject_name)
                except Subject.DoesNotExist:
                    # Try without (PR) suffix
                    clean_name = subject_name.replace(' (PR)', '')
                    try:
                        subject = Subject.objects.get(name=clean_name)
                    except Subject.DoesNotExist:
                        # Log the error and skip this entry
                        logger.error(f"Subject not found: '{subject_name}' or '{clean_name}'")
                        continue

                entries_to_create.append(TimetableEntry(
                    day=entry['day'],
                    period=entry['period'],
                    subject=subject,
                    teacher=Teacher.objects.get(name=entry['teacher']),
                    classroom=Classroom.objects.get(name=entry['classroom']),
                    class_group=entry['class_group'],
                    start_time=entry['start_time'],
                    end_time=entry['end_time'],
                    is_practical=subject.is_practical  # Use the subject's database property
                ))
            
            # Bulk create entries for better performance
            TimetableEntry.objects.bulk_create(entries_to_create)
            
            # Return formatted timetable data
            return self.get(request)
            
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
    

class TaskStatusView(APIView):
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        return Response({
            'status': task.status,
            'result': task.result if task.ready() else None
        })
    
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

    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    
    
class TestIntegrationView(APIView):
    def get(self, request):
        """Test the Config to ScheduleConfig integration"""
        try:
            # Get latest frontend config
            frontend_config = Config.objects.filter(
                generated_periods__isnull=False
            ).exclude(generated_periods={}).order_by('-id').first()

            if not frontend_config:
                return Response({'error': 'No frontend config found'}, status=404)

            # Convert to ScheduleConfig format
            view = TimetableView()
            converted_config = view._convert_config_to_schedule_config(frontend_config)

            # Test scheduler initialization
            from timetable.algorithms.scheduler import TimetableScheduler
            scheduler = TimetableScheduler(converted_config)

            return Response({
                'success': True,
                'frontend_config': {
                    'id': frontend_config.id,
                    'name': frontend_config.name,
                    'periods': frontend_config.periods,
                    'days': frontend_config.days
                },
                'converted_config': {
                    'name': converted_config.name,
                    'periods': converted_config.periods,
                    'class_groups': converted_config.class_groups
                },
                'scheduler_initialized': True
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)

class LatestTimetableView(APIView):
    def get(self, request):
        try:
            # Get the latest config using id instead of created_at
            config = ScheduleConfig.objects.latest('id')
            entries = TimetableEntry.objects.all().order_by('day', 'period')
            
            # Log entries for debugging
            logger.info(f"Found {entries.count()} entries")
            for entry in entries:
                logger.info(f"Entry - Day: {entry.day}, Period: {entry.period}, Teacher: {entry.teacher.name}, Subject: {entry.subject.name}, Class: {entry.class_group}")
            
            # Generate time slots from config
            time_slots = []
            current_time = config.start_time
            for _ in range(len(config.periods)):
                time_slots.append(current_time.strftime("%I:%M %p"))
                current_time = (datetime.combine(datetime.today(), current_time) + 
                               timedelta(minutes=config.lesson_duration)).time()
            
            # Normalize day names to match between config and entries
            entries_data = TimetableSerializer(entries, many=True).data

            # Create day mapping from entry format to config format
            day_mapping = {
                'Monday': 'MON', 'Mon': 'MON',
                'Tuesday': 'TUE', 'Tue': 'TUE',
                'Wednesday': 'WED', 'Wed': 'WED',
                'Thursday': 'THU', 'Thu': 'THU',
                'Friday': 'FRI', 'Fri': 'FRI',
                'Saturday': 'SAT', 'Sat': 'SAT',
                'Sunday': 'SUN', 'Sun': 'SUN'
            }

            # Debug: Check what day formats we actually have
            unique_days = set(entry['day'] for entry in entries_data)
            logger.info(f"Unique day formats in entries: {unique_days}")
            logger.info(f"Config days: {config.days}")
            logger.info(f"Day mapping keys: {list(day_mapping.keys())}")

            # Normalize entry day names to match config format
            for entry in entries_data:
                original_day = entry['day']
                # Simple approach: convert to uppercase and take first 3 chars
                entry['day'] = entry['day'].upper()[:3]
                logger.info(f"Day mapping: '{original_day}' -> '{entry['day']}'")

            data = {
                "days": config.days,
                "timeSlots": time_slots,
                "entries": entries_data
            }
            
            # Log final data for debugging
            logger.info(f"Sending data with {len(data['entries'])} entries")
            logger.info(f"Days: {data['days']}")
            logger.info(f"Time slots: {data['timeSlots']}")
            
            return Response(data)
        except ScheduleConfig.DoesNotExist:
            return Response(
                {'error': 'No schedule configuration found'}, 
                status=404
            )
        except Exception as e:
            logger.error(f"Error retrieving latest timetable: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve timetable'}, 
                status=500
            )
    
    
    