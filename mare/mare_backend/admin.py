from django.contrib import admin
from .models import TideDay, Tide


class TideInline(admin.TabularInline):
    model = Tide
    extra = 0


@admin.register(TideDay)
class TideDayAdmin(admin.ModelAdmin):
    list_display = ("date", "weekday")
    search_fields = ("weekday",)
    inlines = [TideInline]


@admin.register(Tide)
class TideAdmin(admin.ModelAdmin):
    list_display = ("day", "order", "time", "height")
    list_select_related = ("day",)
    list_filter = ("order",)

# Register your models here.
