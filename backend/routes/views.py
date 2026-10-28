from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .models import Route
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    PhotoSerializer,
    RegisterSerializer,
    ReviewSerializer,
    RouteSerializer,
)

MAX_PHOTOS_PER_ROUTE = 10


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("author").prefetch_related("waypoints", "photos")
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # GET  /api/routes/<id>/reviews/ - списък с отзивите (публично)
    # POST /api/routes/<id>/reviews/ - нов отзив (само за влезли потребители)
    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        route = self.get_object()

        if request.method == "GET":
            queryset = route.reviews.select_related("author")
            return Response(ReviewSerializer(queryset, many=True).data)

        if route.author == request.user:
            return Response(
                {"detail": "Не можете да оценявате собствен маршрут."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if route.reviews.filter(author=request.user).exists():
            return Response(
                {"detail": "Вече сте оставили отзив за този маршрут."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(route=route, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # POST /api/routes/<id>/photos/ - качване на снимка (само авторът)
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def photos(self, request, pk=None):
        route = self.get_object()  # връща 403, ако не сте авторът

        if route.photos.count() >= MAX_PHOTOS_PER_ROUTE:
            return Response(
                {"detail": f"Максимум {MAX_PHOTOS_PER_ROUTE} снимки на маршрут."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PhotoSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save(route=route)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # DELETE /api/routes/<id>/photos/<photo_id>/ - изтриване на снимка (само авторът)
    @action(
        detail=True,
        methods=["delete"],
        url_path=r"photos/(?P<photo_id>\d+)",
        permission_classes=[IsAuthenticated, IsAuthorOrReadOnly],
    )
    def delete_photo(self, request, pk=None, photo_id=None):
        route = self.get_object()
        photo = get_object_or_404(route.photos.all(), pk=photo_id)
        photo.image.delete(save=False)  # изтрива и файла от диска
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)