from shop.models import User
from django.contrib.auth.hashers import (
    make_password,
    check_password
)


class UserRepository:

    # =========================================
    # CREATE USER
    # =========================================

    @staticmethod
    def create_user(**data):

        data["password"] = make_password(
            data["password"]
        )

        return User.objects.create(
            **data
        )


    # =========================================
    # GET USER BY ID
    # =========================================

    @staticmethod
    def get_user_by_id(user_id):

        try:

            return User.objects.get(
                user_id=user_id
            )

        except User.DoesNotExist:

            return None


    # =========================================
    # GET USER BY EMAIL
    # =========================================

    @staticmethod
    def get_user_by_email(email):

        try:

            return User.objects.get(
                email=email
            )

        except User.DoesNotExist:

            return None


    # =========================================
    # GET USER BY PHONE
    # =========================================

    @staticmethod
    def get_user_by_phone(phone):

        try:

            return User.objects.get(
                phone=phone
            )

        except User.DoesNotExist:

            return None


    # =========================================
    # LOGIN USER
    # =========================================

    @staticmethod
    def login_user(email, password):

        try:

            user = User.objects.get(
                email=email
            )

            if check_password(
                password,
                user.password
            ):

                return user

            return None

        except User.DoesNotExist:

            return None


    # =========================================
    # GET ALL USERS
    # =========================================

    @staticmethod
    def get_all_users():

        return User.objects.all()


    # =========================================
    # UPDATE USER
    # =========================================

    @staticmethod
    def update_user(user_id, **data):

        if "password" in data:

            data["password"] = make_password(
                data["password"]
            )

        User.objects.filter(
            user_id=user_id
        ).update(
            **data
        )

        return User.objects.get(
            user_id=user_id
        )


    # =========================================
    # DELETE USER
    # =========================================

    @staticmethod
    def delete_user(user_id):

        return User.objects.filter(
            user_id=user_id
        ).delete()