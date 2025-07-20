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
    ConfigViewSet,
    ClassRoomViewSet,  # Potential naming issue
    LatestTimetableView,
    AdvancedTimetableView,
    SimpleTimetableView,
    FastTimetableView,
    ConstraintManagementView,
    OptimizationView,
    TimetableReportView,
    CrossSemesterConflictView,
)

# router = DefaultRouter()

# router.register(r'subjects', SubjectViewSet)
# router.register(r'teachers', TeacherViewSet)
# # router.register(r'classrooms', ClassroomViewSet)
# router.register(r'class-groups', ClassRoomViewSet)  # Name mismatch
# router.register(r'schedule-configs', ScheduleConfigViewSet)
# router.register(r'timetableviewset', TimetableViewSet)  # Naming convention
# router.register(r'configs', ConfigViewSet, basename='config')

# urlpatterns = [
#     path('timetable/', TimetableView.as_view(), name='timetable'),
#     path('tasks/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
# ] + router.urls

router = DefaultRouter()

router.register(r'subjects', SubjectViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'classrooms', ClassroomViewSet)  # Fixed: Added classroom endpoint
router.register(r'class-groups', ClassRoomViewSet)
router.register(r'schedule-configs', ScheduleConfigViewSet, basename='schedule-config')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'configs', ConfigViewSet, basename='config')

urlpatterns = [
    # Basic timetable operations
    path('generate-timetable/', TimetableView.as_view(), name='generate-timetable'),
    path('latest/', LatestTimetableView.as_view(), name='latest-timetable'),
    
    # Advanced timetable operations
    path('advanced-generate/', AdvancedTimetableView.as_view(), name='advanced-generate'),
    path('simple-generate/', SimpleTimetableView.as_view(), name='simple-generate'),
    path('fast-generate/', FastTimetableView.as_view(), name='fast-generate'),
    path('constraints/', ConstraintManagementView.as_view(), name='constraints'),
    path('optimize/', OptimizationView.as_view(), name='optimize'),
    path('report/', TimetableReportView.as_view(), name='report'),

    # Cross-semester conflict detection
    path('cross-semester-conflicts/', CrossSemesterConflictView.as_view(), name='cross-semester-conflicts'),

    # Task management
    path('task-status/<uuid:task_id>/', TaskStatusView.as_view(), name='task-status'),
] + router.urls