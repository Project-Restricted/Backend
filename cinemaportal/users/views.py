from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import PublicUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .serializers import ModeratorRequestSerializer
from django.utils import timezone
from django.shortcuts import get_object_or_404

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        password = data.get('password')
        password_confirm = data.get('passwordConfirm') or data.get('password_confirm')
        if not password or password != password_confirm:
            return Response({'success': False, 'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        username = data.get('username')
        email = data.get('email')
        if not username or not email:
            return Response({'success': False, 'error': 'username and email are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            name = data.get('name')
            lastName = data.get('lastName')
            if name:
                user.first_name = name
            if lastName:
                user.last_name = lastName
            user.save()

            serializer = PublicUserSerializer(user)
            return Response({'success': True, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')
        if not username_or_email or not password:
            return Response({'success': False, 'error': 'username/email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to authenticate by username first, then by email
        user = authenticate(username=username_or_email, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            return Response({'success': False, 'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        tokens = {'access': str(refresh.access_token), 'refresh': str(refresh)}
        serializer = PublicUserSerializer(user)
        data = {'success': True, 'user': serializer.data, 'tokens': tokens}

        # Optional: set refresh token in httpOnly cookie if client requested cookie flow
        use_cookie = request.data.get('useCookie') or request.data.get('use_cookie')
        if use_cookie:
            cookie_name = getattr(settings, 'SIMPLE_JWT_REFRESH_COOKIE', 'refresh')
            secure = getattr(settings, 'SIMPLE_JWT_REFRESH_COOKIE_SECURE', False)
            samesite = getattr(settings, 'SIMPLE_JWT_REFRESH_COOKIE_SAMESITE', 'Lax')
            httponly = getattr(settings, 'SIMPLE_JWT_REFRESH_COOKIE_HTTPONLY', True)
            resp = Response(data)
            resp.set_cookie(cookie_name, str(refresh), httponly=httponly, secure=secure, samesite=samesite)
            return resp

        return Response(data)


class LogoutView(APIView):
    """Logout endpoint supporting both cookie-based and token-based logout.

    Behavior:
    - Try to read refresh token from cookie named by `SIMPLE_JWT_REFRESH_COOKIE`.
    - If not found, try to read `refresh` from request.data.
    - If a refresh token is provided, attempt to blacklist it.
    - Return { success: True } always (idempotent).
    - Works even if access token is expired (only requires refresh token).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        cookie_name = getattr(settings, 'SIMPLE_JWT_REFRESH_COOKIE', 'refresh')
        refresh_token = request.COOKIES.get(cookie_name) or request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # token invalid or already blacklisted — ignore
                pass

        # Clear cookie if present
        resp = Response({'success': True})
        if cookie_name in request.COOKIES:
            resp.delete_cookie(cookie_name)
        return resp


class ModeratorRequestView(APIView):
    # AllowAny so CORS preflight (OPTIONS) succeeds. We enforce auth manually in POST.
    permission_classes = [AllowAny]

    def post(self, request):
        # Require authenticated user for the actual POST
        if not request.user or not request.user.is_authenticated:
            return Response({'success': False, 'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if user already has a pending moderator request
        from .models import ModeratorRequest
        pending_request = ModeratorRequest.objects.filter(user=request.user, status='pending').first()
        if pending_request:
            return Response({'success': False, 'error': 'You already have a pending moderator request'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ModeratorRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        # Create ModeratorRequest object
        mr = ModeratorRequest.objects.create(user=request.user, message=serializer.validated_data.get('message', ''), created_at=timezone.now())
        return Response({'success': True, 'request': {'id': mr.id, 'status': mr.status, 'created_at': mr.created_at}})


class AccountView(APIView):
    """Return the authenticated user's public account data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PublicUserSerializer(request.user, context={'request': request})
        return Response({'success': True, 'user': serializer.data})
