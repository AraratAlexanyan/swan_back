from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.middleware import csrf
from itsdangerous import URLSafeTimedSerializer
from rest_framework import decorators, status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from account.models import Account
from account.serializers import LoginSerializer, RegisterSerializer, AccountSerializer


class LoginApiView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(email=email, password=password)

        if user is not None:
            tokens = self.get_user_tokens(user)
            res = Response()
            res.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=tokens["access_token"],
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            res.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=tokens["refresh_token"],
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            res.data = tokens
            res["X-CSRFToken"] = csrf.get_token(request)
            return res
        raise AuthenticationFailed(
            "Email or Password is incorrect!")


    def get_user_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }


class RegisterApiView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokenizer = URLSafeTimedSerializer(settings.SECRET_KEY)

        serialized_token = tokenizer.dumps(
            {
                "email": serializer.data['email'],
                "username": serializer.data['username']
            }
        )

        verify_url = f'{settings.BASE_URL}/api/acc/verify?token={serialized_token}'

        send_mail(
            "Email Verification!",
            "You are successfully registered. Follow bellow to finish verify",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[serializer.data['email']],
            html_message=f'<a href={verify_url}>Click Here!</a>'
        )

        if user is not None:
            return Response('Registered', status=status.HTTP_201_CREATED)

        return AuthenticationFailed('Invalid data')


@decorators.api_view(['POST'])
@decorators.permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        token = RefreshToken(refresh_token)
        token.blacklist()

        res = Response()
        res.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        res.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        res.delete_cookie('X-CSRFToken')
        res.delete_cookie('csrftoken')

        return res

    except:
        raise ParseError("Invalid token")


class CookieRefreshTokenSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            return InvalidToken("No valid tokens founded")


class CookieTokenRefresh(TokenRefreshView):

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=response.data['refresh'],
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            del response.data['refresh']
        response['X-CRDFToken'] = request.COOKIES.get('csrftoken')
        return super().finalize_response(request, response, *args, **kwargs)


class UserDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = Account.objects.get(id=request.user.id)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AccountSerializer(user)
        return Response(serializer.data)


class EmailVerification(APIView):

    permission_classes = (AllowAny,)

    def get(self, req):

        mail_token = req.GET.get('token')
        print(mail_token)

        if not mail_token:
            return Response('Verification failed', status=status.HTTP_400_BAD_REQUEST)

        tokenizer = URLSafeTimedSerializer(settings.SECRET_KEY)
        print(tokenizer)

        try:
            data = tokenizer.loads(mail_token, max_age=settings.VERIFICATION_TIME_IN_SECONDS)
            print(data)
        except Exception:
            return Response("Verification failed, data expired", status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = Account.objects.get(username=data["username"], email=data["email"])
        except Exception:
            return Response(
                dict(message="Verification Failed: something bad happened"),
                status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
