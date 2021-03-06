from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import render
from django_filters import rest_framework as filters

from djoser.views import UserViewSet
from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings

from tests.utils import get_random_password
from .models import (
    Lesson,
    House,
    Teacher,
    Substitution,
    Subject,
    Level,
    CancelReason,
    Student,
)
from .serializers import (
    LessonSerializer,
    HouseSerializer,
    StudentSerializer,
    SubstitutionSerializer,
    SubstitutionSerializerUpdate,
    ChangePasswordAfterRegisterSerializer,
    SubjectSerializer,
    LevelSerializer,
    CancelReasonSerializer,
)

from .substitutions import (
    create_substitution,
    assign_teacher,
    unassign_teacher,
    user_can_modify,
    cannot_modify_response,
    teacher_already_assigned_response,
    teacher_not_assigned_response,
)
from .filters import SubstitutionFilter

import os


class Register(UserViewSet):
    def perform_create(self, serializer):
        password = get_random_password()
        serializer["password"] = password
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)


class ChangePasswordAfterRegister(viewsets.ModelViewSet):
    http_method_names = ["patch"]

    serializer_class = ChangePasswordAfterRegisterSerializer
    model = Teacher
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        user_id = self.kwargs["id"]
        obj = self.model.objects.get(id=user_id)
        # print("obj", obj)
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # Check old password

            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.fb_name = serializer.data.get("fb_name")
            self.object.is_resetpwd = True
            self.object.save()

            response = {
                "message": "Password updated successfully",
            }

            return Response(response)


class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())

        # this line is the only change from the base implementation.
        kwargs["data"] = {"uid": self.kwargs["uid"], "token": self.kwargs["token"]}

        return serializer_class(*args, **kwargs)

    def activation(self, request, uid, token, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return render(request, "activation_confirmed.html")


class HouseViewSet(viewsets.ModelViewSet):

    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = HouseSerializer

    def get_queryset(self):
        return House.objects.all()


class LessonViewSet(viewsets.ModelViewSet):

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.all()


class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.all()


def index(request):
    """
    Renders built frontend application.
    """
    return render(request, os.path.join("build", "index.html"))


# SUBSTITUTION VIEWS


class SubstitutionsView(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
    )  # Should already be set by default
    serializer_class = SubstitutionSerializer
    http_method_names = ["get", "put", "delete"]
    queryset = Substitution.objects.all()
    filterset_fields = ["new_teacher"]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SubstitutionFilter
    pagination_class = LimitOffsetPagination


    def list(self, request, *args, **kwargs):

        """
        #### Body
            Nothing
        #### Returns
            List of all (or filtered) substitutions
        #### Filters - optional
            You can filter results by any substitution field.
            /api/substitutions/?field_name=value

            Examples:
            /api/substitutions/?new_teacher_found=false - return only pending substitutions
            /api/substitutions/?level=1
            /api/substitutions/?level=1&new_teacher_found=false

        **Filter fields formats:**<br>
        `new_teacher: int`<br>
        `old_teacher: int`<br>
        `datetime: str (e.g. "2021-11-23T16:00:55)"`<br>
        `datetime_range: [from_date, to_date] (e.g. ["2021-10-23T14:00:55", "2021-18-23T17:30:34"])`<br>
        `subject: int`<br>
        `new_teacher_found: bool`<br>
        """
        filtered_qs = self.filter_queryset(self.get_queryset())
        context = self.paginate_queryset(filtered_qs)
        serializer = self.serializer_class(context, many=True)
        return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):

        """
        #### Body
            All substitution object fields are optional (See POST fields)
        #### Returns
            Substitution object for given substitution_id
        #### Permissions
            Only substitution creator or admin can edit
        """
        self.serializer_class = SubstitutionSerializerUpdate
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Assert substitution belongs to the request user or request user is admin
        if not user_can_modify(request, instance):
            return cannot_modify_response

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        """
        #### Body
            Nothing
        #### Returns
            Nothing
        #### Permissions
            Only substitution creator or admin can delete
        """
        instance = self.get_object()
        # Assert substitution belongs to the request user or request user is admin
        if not user_can_modify(request, instance):
            return cannot_modify_response
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class CreateSubstitutionView(SubstitutionsView):

    """
    Creates new substitution instance. On success sends notification email to all active teachers except the requesting one.

    As for now email will be sent to requesting user as well for easier developement.

    #### Body
        level: (string) id of level. Get level id from here: /api/levels/
        datetime: (string) date in one of following formats YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]. Standard ISO format example: 2021-10-28T12:12:00
        subject: (int) id of subject. Get subject id from here: /api/subjects/
        last_topics: (string)(optional)
        planned_topics: (string)(optional)
        methodology_and_platform: (string)(optional)

    #### Returns
        body fields +
        id: (int or None) None or id of created substitution
        reason: Verbal description of this response
        old_teacher: currently logged-in user is set in old_teacher field
        new_teacher_found: false
        new_teacher: null
    """

    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return create_substitution(request)


class AssignTeacherView(SubstitutionsView):
    """
    Assigns currently logged-in user as new_teacher.
    Sets new_teacher_found field in substitution to True.
    Sends email to the creator of this substitution with facebook name.
    If there is already teacher assigned returns failure.

    #### Body
        Nothing

    #### Returns
        ON SUCCES:
            Substitution object (See POST)
        ON FAILURE:
            reason: (string) Verbal description of this response
            success: (bool)
            new_teacher_found: (bool)
    """

    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        substitution = self.get_object()
        if substitution.new_teacher_found:
            return teacher_already_assigned_response
        serializer = self.get_serializer(
            substitution, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        # Custom perform update
        assign_teacher(self.request, substitution)

        return Response(serializer.data)


class UnassignTeacherView(SubstitutionsView):
    """
    Unassigns currently logged-in user as new_teacher.
    Sets new_teacher_found field in substitution to False.
    Sends email with substitution notifications to users.
    If there is no teacher assigned returns failure.

    #### Body
        Nothing

    #### Returns
        ON SUCCES:
            Substitution object (See POST)
        ON FAILURE:
            reason: (string) Verbal description of this response
            success: (bool)
            new_teacher_found: (bool)
    """

    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        print(request)
        partial = kwargs.pop("partial", False)
        substitution = self.get_object()

        user = request.user
        assigned_teacher = substitution.new_teacher
        if not substitution.new_teacher_found:
            return teacher_not_assigned_response
        elif user != assigned_teacher:
            return cannot_modify_response

        serializer = self.get_serializer(
            substitution, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        # Custom perform update
        unassign_teacher(self.request, substitution)

        if getattr(substitution, "_prefetched_objects_cache", None):
            substitution._prefetched_objects_cache = {}

        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.all()


class LevelViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LevelSerializer

    def get_queryset(self):
        return Level.objects.all()


class CancelReasonViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CancelReasonSerializer

    def get_queryset(self):
        return CancelReason.objects.all()
