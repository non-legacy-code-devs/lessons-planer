from rest_framework import routers
from backend.views import *


router = routers.SimpleRouter()
router.register(r"lessons", LessonViewSet, basename="lessons")
router.register(r"houses", HouseViewSet, basename="houses")
router.register(r"students", StudentViewSet, basename="students")
router.register(r"subjects", SubjectViewSet, basename="subjects")
router.register(r"levels", LevelViewSet, basename="levels")
router.register(r"cancel_reasons", CancelReasonViewSet, basename="cancel_reasons")

# Substitutions
router.register(
    r"substitutions/create", CreateSubstitutionView, basename="create_substitution"
)
router.register(
    r"substitutions/assign_teacher", AssignTeacherView, basename="assign_teacher"
)
router.register(
    r"substitutions/unassign_teacher", UnassignTeacherView, basename="unassign_teacher"
)
router.register(r"substitutions", SubstitutionsView, basename="substitutions")
