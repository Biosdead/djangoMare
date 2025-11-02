from datetime import date as date_cls, timedelta
import calendar

from django.http import HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.utils import timezone
from urllib.parse import quote_plus

from mare_backend.models import TideDay


def _tide_typed(day_obj):
    tides = list(day_obj.tides.all().order_by("order"))
    typed = []
    for i, t in enumerate(tides):
        if len(tides) == 1:
            tide_type = None
        else:
            compare_idx = i + 1 if i + 1 < len(tides) else i - 1
            tide_type = "Maré Alta" if t.height > tides[compare_idx].height else "Maré Baixa"
        typed.append({
            "order": t.order,
            "time": t.time,
            "height": t.height,
            "type": tide_type,
        })
    return typed


def index(request):
    today = timezone.localdate()

    # Selected date via query param (?date=YYYY-MM-DD), defaults to today
    selected = today
    qd = request.GET.get("date")
    if qd:
        try:
            selected = date_cls.fromisoformat(qd)
        except ValueError:
            selected = today

    meses_pt = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    month_name = meses_pt[selected.month - 1].capitalize()

    # Canonical + OG image absolute URLs
    canonical_url = request.build_absolute_uri()
    if "?" in canonical_url:
        canonical_url = canonical_url.split("?", 1)[0]
    og_image_url = request.build_absolute_uri(static("pages/imagens/og-image.png"))

    # Load selected day tides
    day_obj = TideDay.objects.filter(date=selected).prefetch_related("tides").first()

    # Build single-month calendar widget for the selected month/year
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    days_qs = (
        TideDay.objects.filter(date__year=selected.year)
        .prefetch_related("tides")
        .order_by("date")
    )
    by_date = {td.date: td for td in days_qs}
    month_weeks = []
    for week in cal.monthdatescalendar(selected.year, selected.month):
        week_cells = []
        for d in week:
            td = by_date.get(d)
            week_cells.append({
                "date": d,
                "in_month": (d.month == selected.month),
                "has_data": td is not None,
                "tides": _tide_typed(td) if td else [],
            })
        month_weeks.append(week_cells)

    # Month selector options for the year (default 2025 request)
    year_for_picker = selected.year
    month_options = []
    for m in range(1, 13):
        value_date = date_cls(year_for_picker, m, 1)
        month_options.append({
            "value": value_date.isoformat(),
            "label": f"{meses_pt[m-1].capitalize()} {year_for_picker}",
            "selected": (m == selected.month),
        })

    # Day navigation links
    prev_day = selected - timedelta(days=1)
    next_day = selected + timedelta(days=1)
    base_path = request.path
    prev_link = f"{base_path}?date={prev_day.isoformat()}"
    next_link = f"{base_path}?date={next_day.isoformat()}"
    today_link = f"{base_path}?date={today.isoformat()}"

    # Month navigation links
    first_of_month = date_cls(selected.year, selected.month, 1)
    prev_month_year = (first_of_month.replace(day=1) - timedelta(days=1)).year
    prev_month = (first_of_month.replace(day=1) - timedelta(days=1)).month
    next_month_year = (first_of_month.replace(day=28) + timedelta(days=4)).year
    next_month = (first_of_month.replace(day=28) + timedelta(days=4)).month
    prev_month_link = f"{base_path}?date={date_cls(prev_month_year, prev_month, 1).isoformat()}"
    next_month_link = f"{base_path}?date={date_cls(next_month_year, next_month, 1).isoformat()}"

    default_share_text = "Marés de Salinópolis — confira em https://www.maresdesalinas.com.br"

    context = {
        "date": selected,
        "weekday": None,
        "tides": [],
        "has_data": False,
        "month_name": month_name,
        "canonical_url": canonical_url,
        "og_image_url": og_image_url,
        "whatsapp_share_url": f"https://wa.me/?text={quote_plus(default_share_text)}",
        "share_text": default_share_text,
        # month widget
        "year": selected.year,
        "month_weeks": month_weeks,
        "month_options": month_options,
        "prev_month_link": prev_month_link,
        "next_month_link": next_month_link,
        "today": today,
        # nav links
        "prev_link": prev_link,
        "next_link": next_link,
        "today_link": today_link,
    }

    if day_obj:
        typed = _tide_typed(day_obj)
        # Build WhatsApp share text with selected day's tides
        share_lines = [
            f"Marés de Salinópolis em {selected.strftime('%d/%m/%Y')}:",
        ]
        for it in typed:
            hhmm = it["time"].strftime("%H:%M")
            share_lines.append(f"{it['type']}: {hhmm} — {it['height']} m")
        share_lines.append("Veja mais em https://www.maresdesalinas.com.br")
        share_text = "\n".join(share_lines)

        context.update({
            "weekday": day_obj.weekday,
            "tides": typed,
            "has_data": True,
            "whatsapp_share_url": f"https://wa.me/?text={quote_plus(share_text)}",
            "share_text": share_text,
        })

    return render(request, "pages/index.html", context)


def sobre(request):
    return render(request, "pages/sobre.html")


def privacidade(request):
    return render(request, "pages/privacidade.html")


def ads_txt(request):
    content = "google.com, pub-8048981882025505, DIRECT, f08c47fec0942fa0\n"
    return HttpResponse(content, content_type="text/plain")


def calendar_year(request, year: int):
    meses_pt = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    cal = calendar.Calendar(firstweekday=6)  # Sunday first

    days_qs = (
        TideDay.objects.filter(date__year=year)
        .prefetch_related("tides")
        .order_by("date")
    )
    by_date = {td.date: td for td in days_qs}

    months = []
    for m in range(1, 13):
        month_weeks = []
        for week in cal.monthdatescalendar(year, m):
            week_cells = []
            for d in week:
                td = by_date.get(d)
                week_cells.append({
                    "date": d,
                    "in_month": (d.month == m),
                    "has_data": td is not None,
                    "tides": _tide_typed(td) if td else [],
                })
            month_weeks.append(week_cells)
        months.append({
            "name": meses_pt[m - 1].capitalize(),
            "number": m,
            "weeks": month_weeks,
        })

    context = {
        "year": year,
        "months": months,
    }
    return render(request, "pages/calendar.html", context)


def day_detail(request, year: int, month: int, day: int):
    try:
        target = date_cls(year, month, day)
    except ValueError:
        target = timezone.localdate()

    meses_pt = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    month_name = meses_pt[target.month - 1].capitalize()

    day_obj = TideDay.objects.filter(date=target).prefetch_related("tides").first()
    context = {
        "date": target,
        "weekday": day_obj.weekday if day_obj else None,
        "tides": _tide_typed(day_obj) if day_obj else [],
        "has_data": bool(day_obj),
        "month_name": month_name,
        "canonical_url": request.build_absolute_uri(),
        "og_image_url": request.build_absolute_uri(static("pages/imagens/og-image.png")),
        "whatsapp_share_url": "",
        "share_text": "",
    }
    if day_obj:
        lines = [f"Marés de Salinópolis em {target.strftime('%d/%m/%Y')}:"]
        for it in context["tides"]:
            lines.append(f"{it['type']}: {it['time'].strftime('%H:%M')} — {it['height']} m")
        lines.append("Veja mais em https://www.maresdesalinas.com.br")
        share_text = "\n".join(lines)
        context["share_text"] = share_text
        context["whatsapp_share_url"] = f"https://wa.me/?text={quote_plus(share_text)}"
    return render(request, "pages/day.html", context)
