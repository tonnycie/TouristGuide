from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Route, Waypoint


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
        read_only_fields = ["order_index"]  # редът се определя от позицията в списъка


class RouteSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    waypoints = WaypointSerializer(many=True, allow_empty=False)

    class Meta:
        model = Route
        fields = [
            "id", "title", "destination", "description",
            "tips", "author", "created_at", "waypoints",
        ]
        read_only_fields = ["id", "created_at"]

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
        if waypoints_data is not None:  # ако са изпратени точки, заместват старите
            instance.waypoints.all().delete()
            self._save_waypoints(instance, waypoints_data)
        return instance