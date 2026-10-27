from django.contrib import admin
from .models import Photo, Review, Route, Waypoint


class WaypointInline(admin.TabularInline):
    model = Waypoint
    extra = 1


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("title", "destination", "author", "created_at")
    inlines = [WaypointInline]


admin.site.register(Photo)
admin.site.register(Review)