from django.contrib.auth.models import User
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from .models import Route
from .permissions import IsAuthorOrReadOnly
from .serializers import RegisterSerializer, RouteSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("author").prefetch_related("waypoints")
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        # авторът винаги е влезлият потребител, не се взема от заявката
        serializer.save(author=self.request.user)