from django.contrib.auth.models import User
from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

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


class UserProfileView(APIView):
    """GET /api/users/<username>/ - публична статистика (без имейл)."""

    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        return Response(
            {
                "username": user.username,
                "date_joined": user.date_joined,
                "routes_count": user.routes.count(),
                "reviews_count": user.reviews.count(),
            }
        )


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("author").prefetch_related("waypoints", "photos")
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action != "list":  # филтрите важат само за списъка
            return queryset

        params = self.request.query_params
        queryset = queryset.annotate(avg_rating=Avg("reviews__rating"))

        search = params.get("search", "").strip()
        if search:
            # SQLite не различава главни и малки букви само за латиница,
            # затова за кирилица търсим в Python с casefold()
            needle = search.casefold()
            rows = Route.objects.values_list("id", "title", "destination", "description")
            ids = [pk for pk, *texts in rows if needle in " ".join(texts).casefold()]
            queryset = queryset.filter(id__in=ids)

        author = params.get("author", "").strip()
        if author:
            queryset = queryset.filter(author__username__iexact=author)

        min_rating = params.get("min_rating", "").strip()
        if min_rating:
            try:
                value = float(min_rating)
            except ValueError:
                raise ValidationError({"min_rating": "Трябва да е число."})
            queryset = queryset.filter(avg_rating__gte=value)

        if params.get("ordering") == "rating":
            queryset = queryset.order_by(F("avg_rating").desc(nulls_last=True), "-created_at")

        return queryset

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
        route = self.get_object()

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
        photo.image.delete(save=False)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)