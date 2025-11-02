from rest_framework import serializers
from .models import TideDay, Tide


class TideSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source="day.date", write_only=True, required=True)
    weekday = serializers.CharField(source="day.weekday", write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Tide
        fields = ("id", "order", "time", "height", "date", "weekday")
        read_only_fields = ("id",)

    def create(self, validated_data):
        day_data = validated_data.pop("day")
        date = day_data["date"]
        weekday = day_data.get("weekday")

        # Create or update the TideDay
        day_obj, _ = TideDay.objects.get_or_create(date=date, defaults={"weekday": weekday or ""})
        if weekday and day_obj.weekday != weekday:
            day_obj.weekday = weekday
            day_obj.save(update_fields=["weekday"])

        tide, _ = Tide.objects.update_or_create(
            day=day_obj,
            order=validated_data["order"],
            defaults={
                "time": validated_data["time"],
                "height": validated_data["height"],
            },
        )
        return tide


class TideDaySerializer(serializers.ModelSerializer):
    tides = TideSerializer(many=True, read_only=True)

    class Meta:
        model = TideDay
        fields = ("id", "date", "weekday", "tides")
        read_only_fields = ("id",)

