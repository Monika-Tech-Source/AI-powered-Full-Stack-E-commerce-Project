from ..models import User


def admin_status(request):

    user_id = request.session.get("user_id")

    is_admin = False

    if user_id:

        try:
            user = User.objects.get(
                user_id=user_id
            )

            is_admin = user.is_admin

        except User.DoesNotExist:

            is_admin = False

    return {
        "is_admin": is_admin
    }