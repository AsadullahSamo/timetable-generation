from rest_framework import viewsets
from .models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config, ClassGroup
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ScheduleConfig, TimetableEntry
from celery.result import AsyncResult
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
import logging

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
    def get(self, request):
        config = ScheduleConfig.objects.latest('created_at')
        entries = TimetableEntry.objects.all().order_by('day', 'period')
        
        # Generate time slots from config
        time_slots = []
        current_time = config.start_time
        for _ in range(len(config.periods)):
            time_slots.append(current_time.strftime("%I:%M %p"))
            current_time = (datetime.combine(datetime.today(), current_time) + 
                           timedelta(minutes=config.lesson_duration)).time()
        
        data = {
            "days": config.days,
            "timeSlots": time_slots,
            "entries": TimetableSerializer(entries, many=True).data
        }
        
        return Response(data)
    

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
    
    
    