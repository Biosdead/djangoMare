from django.db import models


class TideDay(models.Model):
    date = models.DateField(unique=True)
    weekday = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]

    def __str__(self) -> str:
        return f"{self.date} ({self.weekday})"


class Tide(models.Model):
    day = models.ForeignKey(TideDay, on_delete=models.CASCADE, related_name="tides")
    order = models.PositiveSmallIntegerField()  # 1..4
    time = models.TimeField()
    height = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ("day", "order")
        ordering = ["day__date", "order"]

    def __str__(self) -> str:
        return f"{self.day.date} #{self.order} - {self.time} ({self.height} m)"
