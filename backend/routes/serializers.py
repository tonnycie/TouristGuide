from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Avg
from rest_framework import serializers

from .models import Review, Route, Waypoint
from .sanitize import clean_required, clean_text


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class WaypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waypoint
        fields = ["id", "name", "latitude", "longitude", "order_index"]
        read_only_fields = ["order_index"]

    def validate_name(self, value):
        return clean_required(value)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ["id", "author", "text", "rating", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_text(self, value):
        return clean_required(value)


class RouteSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    waypoints = WaypointSerializer(many=True, allow_empty=False)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = [
            "id", "title", "destination", "description", "tips",
            "author", "created_at", "waypoints",
            "average_rating", "reviews_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 1) if avg is not None else None

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def validate_title(self, value):
        return clean_required(value)

    def validate_destination(self, value):
        return clean_required(value)

    def validate_description(self, value):
        return clean_text(value)

    def validate_tips(self, value):
        return clean_text(value)

    def _save_waypoints(self, route, waypoints_data):
        for index, data in enumerate(waypoints_data):
            Waypoint.objects.create(route=route, order_index=index, **data)

    @transaction.atomic
    def create(self, validated_data):
        waypoints_data = validated_data.pop("waypoints")
        route = Route.objects.create(**validated_data)
        self._save_waypoints(route, waypoints_data)
        return route

    @transaction.atomic
    def update(self, instance, validated_data):
        waypoints_data = validated_data.pop("waypoints", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if waypoints_data is not None:
            instance.waypoints.all().delete()
            self._save_waypoints(instance, waypoints_data)
        return instance