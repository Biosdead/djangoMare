import json
import re
import unicodedata
from datetime import date, time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from mare_backend.models import TideDay, Tide


def _strip_js_comments(text: str) -> str:
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def _normalize_key_names(s: str) -> str:
    # Normalize weird encodings of "Horário" to "Horario"
    s = re.sub(r'"Hor[^"\n\r]*?rio"', '"Horario"', s)
    # Keep "Altura" and "DIA" as-is
    return s


def _remove_trailing_commas(s: str) -> str:
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s


def _ascii_slug(name: str) -> str:
    return (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
        .lower()
    )


MONTH_MAP = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,  # Março (ç removido)
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}


class Command(BaseCommand):
    help = "Importa marés a partir de oldProj/banco.js para modelos TideDay/Tide."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            default=str(Path("mare") / "mare" / "oldProj" / "banco.js"),
            help="Caminho para banco.js",
        )
        parser.add_argument(
            "--year",
            dest="year",
            type=int,
            required=True,
            help="Ano para aplicar (ex.: 2025)",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Apaga dados existentes do ano antes de importar",
        )

    def handle(self, *args, **options):
        path = Path(options["path"]).resolve()
        year = options["year"]
        if not path.exists():
            raise CommandError(f"Arquivo não encontrado: {path}")

        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="latin-1")

        raw = _strip_js_comments(raw)

        # Collect month blocks like: Janeiro = { ... };
        months = {}
        current_name = None
        brace_level = 0
        buf = []
        for line in raw.splitlines():
            if current_name is None:
                m = re.match(r"\s*([A-Za-zÀ-ÿ]+)\s*=\s*\{\s*$", line)
                if m:
                    current_name = m.group(1)
                    brace_level = 1
                    buf = ["{"]
                continue
            else:
                # inside block
                brace_level += line.count("{")
                brace_level -= line.count("}")
                buf.append(line)
                if brace_level == 0:
                    # end of month object; remove trailing '};' if present
                    content = "\n".join(buf)
                    content = content.rstrip().rstrip(";")
                    content = _normalize_key_names(content)
                    content = _remove_trailing_commas(content)
                    months[current_name] = content
                    current_name = None
                    buf = []

        if not months:
            raise CommandError("Nenhum bloco de mês encontrado em banco.js")

        # Optionally truncate existing data for year
        if options["truncate"]:
            Tide.objects.filter(day__date__year=year).delete()
            TideDay.objects.filter(date__year=year).delete()

        created_days = 0
        created_tides = 0

        with transaction.atomic():
            for month_name, json_like in months.items():
                slug = _ascii_slug(month_name)
                month_num = MONTH_MAP.get(slug)
                if not month_num:
                    self.stderr.write(self.style.WARNING(f"Mês ignorado: {month_name}"))
                    continue
                # Parse JSON
                try:
                    data = json.loads(json_like)
                except json.JSONDecodeError as e:
                    raise CommandError(f"Falha ao decodificar mês {month_name}: {e}")

                for day_str, payload in data.items():
                    try:
                        day_int = int(day_str)
                    except ValueError:
                        self.stderr.write(self.style.WARNING(f"Dia inválido: {day_str} em {month_name}"))
                        continue
                    d = date(year, month_num, day_int)
                    weekday = str(payload.get("DIA", "")).strip()
                    day_obj, day_created = TideDay.objects.get_or_create(
                        date=d, defaults={"weekday": weekday}
                    )
                    if not day_created and weekday and day_obj.weekday != weekday:
                        day_obj.weekday = weekday
                        day_obj.save(update_fields=["weekday"])
                    if day_created:
                        created_days += 1

                    for n in (1, 2, 3, 4):
                        key = f"MARE{n}"
                        if key not in payload:
                            continue
                        block = payload[key]
                        horario = str(block.get("Horario", "")).strip()
                        altura = block.get("Altura")
                        if not horario or len(horario) != 4 or altura is None:
                            continue
                        try:
                            hh = int(horario[0:2])
                            mm = int(horario[2:4])
                            t = time(hh, mm)
                        except Exception:
                            continue
                        tide_obj, tide_created = Tide.objects.update_or_create(
                            day=day_obj,
                            order=n,
                            defaults={
                                "time": t,
                                "height": altura,
                            },
                        )
                        if tide_created:
                            created_tides += 1

        self.stdout.write(self.style.SUCCESS(
            f"Importação concluída. Dias criados: {created_days}, Marés criadas: {created_tides}"
        ))
