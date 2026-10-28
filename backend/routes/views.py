from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Route
from .permissions import IsAuthorOrReadOnly
from .serializers import RegisterSerializer, ReviewSerializer, RouteSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("author").prefetch_related("waypoints")
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # GET  /api/routes/<id>/reviews/  - списък с отзивите (публично)
    # POST /api/routes/<id>/reviews/  - нов отзив (само за влезли потребители)
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