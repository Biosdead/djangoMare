from django.shortcuts import render
from django.utils import timezone
from django.templatetags.static import static
from urllib.parse import quote_plus

from mare_backend.models import TideDay


def index(request):
    today = timezone.localdate()
    meses_pt = [
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    ]
    month_name = meses_pt[today.month - 1].capitalize()
    day_obj = TideDay.objects.filter(date=today).prefetch_related("tides").first()
    # Canonical + OG image absolute URLs
    canonical_url = request.build_absolute_uri()
    if "?" in canonical_url:
        canonical_url = canonical_url.split("?", 1)[0]
    og_image_url = request.build_absolute_uri(static("pages/imagens/og-image.png"))

    default_share_text = "Marés de Salinópolis — confira em https://www.maresdesalinas.com.br"

    context = {
        "date": today,
        "weekday": None,
        "tides": [],
        "has_data": False,
        "month_name": month_name,
        "canonical_url": canonical_url,
        "og_image_url": og_image_url,
        "whatsapp_share_url": f"https://wa.me/?text={quote_plus(default_share_text)}",
        "share_text": default_share_text,
    }
    if day_obj:
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
        # Build WhatsApp share text with today's tides
        share_lines = [
            f"Marés de Salinópolis em {today.strftime('%d/%m/%Y')}:",
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

from django.http import HttpResponse


def ads_txt(request):
    content = "google.com, pub-8048981882025505, DIRECT, f08c47fec0942fa0\n"
    return HttpResponse(content, content_type="text/plain")
