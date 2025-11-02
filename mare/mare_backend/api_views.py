from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import TideDay, Tide
from .serializers import TideDaySerializer, TideSerializer


class TideDayViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TideDay.objects.all().prefetch_related("tides").order_by("date")
    serializer_class = TideDaySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        date_param = self.request.query_params.get("date")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if date_param:
            try:
                d = datetime.strptime(date_param, "%Y-%m-%d").date()
                qs = qs.filter(date=d)
            except ValueError:
                pass
        if start and end:
            try:
                ds = datetime.strptime(start, "%Y-%m-%d").date()
                de = datetime.strptime(end, "%Y-%m-%d").date()
                qs = qs.filter(date__range=(ds, de))
            except ValueError:
                pass
        return qs


class TideViewSet(viewsets.ModelViewSet):
    queryset = Tide.objects.select_related("day").all().order_by("day__date", "order")
    serializer_class = TideSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        date_param = self.request.query_params.get("date")
        if date_param:
            try:
                d = datetime.strptime(date_param, "%Y-%m-%d").date()
                qs = qs.filter(day__date=d)
            except ValueError:
                pass
        return qs

