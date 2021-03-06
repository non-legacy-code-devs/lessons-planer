from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.response import Response as RestFrameworkResponse

from .models import (
    Substitution,
    Teacher,
    get_subject_full_name,
    get_level_full_name,
    Subject,
    Level,
)
from .notifications import SubstitutionEmail, SubstitutionConfirmationEmail
from .serializers import SubstitutionSerializer

# Possible statuses used in substitutions responses
status_ok = status.HTTP_200_OK
status_not_found = status.HTTP_404_NOT_FOUND
status_conflict = status.HTTP_409_CONFLICT
status_permission = status.HTTP_401_UNAUTHORIZED


def map_number_to_weekday(number):
    """Returns name of the week for number from 1 to 7"""
    assert 0 <= number < 7
    days = [
        "Poniedziałek",
        "Wtorek",
        "Środa",
        "Czwartek",
        "Piątek",
        "Sobota",
        "Niedziela",
    ]
    return days[number]


def validate_user_before_email(teacher, current_user):
    """
    Returns true if teacher:
        - has valid email
        - is active
        - is not current user
    """
    # Validate Email
    try:
        validate_email(teacher.email)
    except ValidationError as e:
        return False

    # Is Active
    if not teacher.is_active:
        return False

    # TODO uncomment it after going live
    # Is not current user
    # if teacher == current_user:
    #     return False

    return True


def save_substitution(data):
    new_substitution = Substitution(**data)
    new_substitution.save()
    return new_substitution


def create_substitution(request):
    response_data = {
        "reason": "Substitution successfully created. Sending emails to teachers..."
    }
    current_status = status_ok

    # Dont let the user to pass new_teacher or new_teacher_found fields
    if "new_teacher" in request.data or "new_teacher_found" in request.data:
        current_status = status_conflict
        response_data[
            "reason"
        ] = "You cannot pass new_teacher or new_teacher_found field while creating substitution"

    # Assert that date of that lesson is in the future
    if current_status == status_ok:
        current_time = datetime.now()
        requested_time = datetime.strptime(request.data["datetime"], "%Y-%m-%dT%H:%M")
        if requested_time.timestamp() < current_time.timestamp():
            current_status = status_conflict
            response_data["reason"] = "Please provide time in the future"

    # Assert that this is not duplicate (Same user and exactly the same date)
    if current_status == status_ok:
        sub_with_same_date_and_user = Substitution.objects.filter(
            datetime=requested_time, old_teacher=request.user
        )
        if sub_with_same_date_and_user:
            current_status = status_conflict
            response_data[
                "reason"
            ] = "There is already substitution for this user with exactly the same datetime and user. Substitution not created assuming this is an error"

    # Create substitution
    if current_status == status_ok:
        substitution_data = {k: v for (k, v) in request.data.items()}
        substitution_data["old_teacher"] = request.user
        # Already checked if exist in serializer
        substitution_data["subject"] = Subject.objects.get(
            id=substitution_data["subject"]
        )
        substitution_data["level"] = Level.objects.get(id=substitution_data["level"])

        substitution = save_substitution(substitution_data)
        substitution_id = substitution.id

        send_mail_with_substitution_info(substitution_id, requested_time, request)

        response_data.update(SubstitutionSerializer(substitution).data)

    response = RestFrameworkResponse(data=response_data, status=current_status)
    return response


def send_mail_with_substitution_info(substitution_id, substitution_date, request):
    # TODO should teachers be filtered by subject?
    teachers = Teacher.objects.all()

    week_day = substitution_date.weekday()
    time = substitution_date.strftime("%H:%M")
    date = substitution_date.strftime("%d.%m")

    context = {
        "subject": get_subject_full_name(request.data["subject"]),
        "level": get_level_full_name(request.data["level"]),
        "week_day": map_number_to_weekday(week_day),
        "time": time,
        "date": date,
        "substitution_id": substitution_id,
    }

    sub_email = SubstitutionEmail(request, context)
    mail_list = [
        teacher.email
        for teacher in teachers
        if validate_user_before_email(teacher, request.user)
    ]

    if mail_list:
        sub_email.send(to=[], bcc=mail_list)
    return True


def assign_teacher(request, substitution):
    new_teacher = request.user

    substitution.new_teacher = (
        new_teacher  # new_teacher_found property updates in model.on_save
    )
    substitution.save()
    send_email_to_old_teacher(request, substitution)


def unassign_teacher(request, substitution):
    new_teacher = None

    substitution.new_teacher = (
        new_teacher  # new_teacher_found property updates in model.on_save
    )
    substitution.new_teacher_found = False
    substitution.save()

    teachers = Teacher.objects.all()
    substitution_date = substitution.datetime

    week_day = substitution_date.weekday()
    time = substitution_date.strftime("%H:%M")
    date = substitution_date.strftime("%d.%m")

    context = {
        "subject": substitution.subject.name,
        "level": substitution.level.name,
        "week_day": map_number_to_weekday(week_day),
        "time": time,
        "date": date,
        "substitution_id": substitution.id,
    }

    sub_email = SubstitutionEmail(request, context)
    mail_list = [
        teacher.email
        for teacher in teachers
        if validate_user_before_email(teacher, request.user)
    ]

    if mail_list:
        sub_email.send(to=[], bcc=mail_list)
    return True


def send_email_to_old_teacher(request, substitution):
    """ "
    Send email with new teacher contact info to the teacher that applied for substitution
    """
    contact = substitution.new_teacher.fb_name
    if contact is None:
        contact = "User did not provide fb name."

    time = substitution.datetime.strftime("%H:%M")
    date = substitution.datetime.strftime("%d.%m")

    context = {
        "new_teacher": contact,
        "time": time,
        "date": date,
        "substitution_id": substitution.id,
    }

    sub_email = SubstitutionConfirmationEmail(request, context)

    mail_list = [substitution.old_teacher.email]
    if mail_list:
        sub_email.send(to=[], bcc=mail_list)


def user_can_modify(request, instance):
    """
    Assert that the user is the creator of this substitution or is admin
    Returns True or False
    """
    # Assert substitution belongs to the request user or request user is admin
    if not request.user == instance.old_teacher and not request.user.is_staff:
        return False
    return True


cannot_modify_response = RestFrameworkResponse(
    status=status.HTTP_401_UNAUTHORIZED,
    data={"reason": "Only substitution creator or admin can edit this substitution"},
)

teacher_already_assigned_response = RestFrameworkResponse(
    status=status.HTTP_409_CONFLICT,
    data={
        "reason": "New teacher was already assigned to this substitution",
        "new_teacher_found": True,
        "success": False,
    },
)
teacher_not_assigned_response = RestFrameworkResponse(
    status=status.HTTP_409_CONFLICT,
    data={
        "reason": "No teacher assigned for this lesson",
        "new_teacher_found": False,
        "success": False,
    },
)
