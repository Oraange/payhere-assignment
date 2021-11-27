import json

from django.http import JsonResponse
from django.views import View
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from users.dto import SignUpInputDTO, SignInInputDTO, TokenDTO
from users.exceptions import DuplicateUser, PasswordValidationError, UserNotFound
from users.validations import validate_password
from .service import SignUpService, SignInService, TokenGenerator


class SignUpView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SignUpService()

    def post(self, request):
        data = json.loads(request.body)

        try:
            sign_up_info = SignUpInputDTO(**data)
            validate_email(sign_up_info.email)
            validate_password(sign_up_info.password)
            self.service.add_user(sign_up_info)

        except DuplicateUser:
            return JsonResponse({"message": "USER_ALREADY_EXIST"}, status=409)

        except ValidationError:
            return JsonResponse({"message": "INVALID_EMAIL"}, status=400)

        except PasswordValidationError:
            return JsonResponse({"message": "INVALID_PASSWORD"}, status=400)

        except TypeError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
        
        else:
            return JsonResponse({"message": "CREATED"}, status=201)


class SignInView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sign_in_service = SignInService()
        self.gen_token = TokenGenerator()

    def post(self, request):
        data = json.loads(request.body)

        try:
            sign_in_info = SignInInputDTO(**data)
            user = self.sign_in_service.get_user(sign_in_info.email)
            self.sign_in_service.check_password(sign_in_info.password, user.password)

        except UserNotFound:
            return JsonResponse({"message": "INVALID_USER"}, status=404)

        except TypeError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)

        else:
            token = TokenDTO(**self.gen_token.generate_token(user.id))
            return JsonResponse(
                {
                    "message": "SUCCESS",
                    "access_token": token.access_token
                }
            )
