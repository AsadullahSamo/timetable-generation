from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet,
    TeacherViewSet,
    ClassroomViewSet,
    ScheduleConfigViewSet,
    TimetableViewSet,
    TimetableView,
    TaskStatusView,
    ConfigViewSet
)

router = DefaultRouter()

router.register(r'subjects', SubjectViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'schedule-configs', ScheduleConfigViewSet)  # Changed prefix
router.register(r'timetableviewset', TimetableViewSet)
router.register(r'configs', ConfigViewSet, basename='config')  # Unique prefix

urlpatterns = [
    path('timetable/', TimetableView.as_view(), name='timetable'),  
    path('tasks/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
] + router.urls