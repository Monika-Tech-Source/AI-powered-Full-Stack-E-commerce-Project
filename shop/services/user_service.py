from shop.repositories.user_repository import UserRepository


class UserService:

    # =========================================
    # REGISTER USER
    # =========================================

    @staticmethod
    def register_user(**data):

        existing_user = UserRepository.get_user_by_email(
            data["email"]
        )

        if existing_user:

            raise ValueError(
                "Email already registered"
            )

        existing_phone = UserRepository.get_user_by_phone(
            data["phone"]
        )

        if existing_phone:

            raise ValueError(
                "Phone number already registered"
            )

        return UserRepository.create_user(
            **data
        )


    # =========================================
    # LOGIN
    # =========================================

    @staticmethod
    def login_user(email, password):

        return UserRepository.login_user(
            email,
            password
        )


    # =========================================
    # GET USER
    # =========================================

    @staticmethod
    def get_user(user_id):

        return UserRepository.get_user_by_id(
            user_id
        )


    # =========================================
    # GET ALL USERS
    # =========================================

    @staticmethod
    def get_all_users():

        return UserRepository.get_all_users()


    # =========================================
    # UPDATE USER
    # =========================================

    @staticmethod
    def update_user(user_id, **data):

        if "email" in data:

            existing_user = UserRepository.get_user_by_email(
                data["email"]
            )

            if (
                existing_user
                and existing_user.user_id != user_id
            ):

                raise ValueError(
                    "Email already registered"
                )

        if "phone" in data:

            existing_phone = UserRepository.get_user_by_phone(
                data["phone"]
            )

            if (
                existing_phone
                and existing_phone.user_id != user_id
            ):

                raise ValueError(
                    "Phone number already registered"
                )

        return UserRepository.update_user(
            user_id,
            **data
        )


    # =========================================
    # DELETE USER
    # =========================================

    @staticmethod
    def delete_user(user_id):

        return UserRepository.delete_user(
            user_id
        )