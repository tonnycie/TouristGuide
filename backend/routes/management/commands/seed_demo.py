from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from routes.models import Review, Route, Waypoint

DEMO_PASSWORD = "Demo!Pass2026"
DEMO_USERS = ["demo_ivan", "demo_maria", "demo_petar", "demo_elena"]

# координатите са приблизителни, достатъчни за демонстрация
ROUTES = [
    {
        "author": "demo_ivan",
        "title": "Седемте рилски езера",
        "destination": "Рила",
        "description": "Един от най-красивите планински маршрути в България. Пътеката се изкачва плавно и езерата се разкриват едно след друго.",
        "tips": "Тръгнете рано сутринта, вземете яке дори през лятото и повече вода.",
        "waypoints": [
            ("Паничище", "42.2686", "23.3170"),
            ("Хижа Рилски езера", "42.2056", "23.3260"),
            ("Окото", "42.2013", "23.3184"),
        ],
    },
    {
        "author": "demo_maria",
        "title": "Старият град на Пловдив",
        "destination": "Пловдив",
        "description": "Разходка сред римски останки, възрожденски къщи и тесни калдъръмени улици.",
        "tips": "Обувки с равна подметка, защото калдъръмът е хлъзгав. Най-добре е привечер.",
        "waypoints": [
            ("Античен театър", "42.1472", "24.7516"),
            ("Небет тепе", "42.1495", "24.7457"),
            ("Капана", "42.1502", "24.7490"),
        ],
    },
    {
        "author": "demo_petar",
        "title": "Северно Черноморие",
        "destination": "Варна - Калиакра",
        "description": "Крайбрежно пътуване с плажове, скали и един от най-красивите нос на нашето Черноморие.",
        "tips": "Избягвайте юли и август заради тълпите, а за Калиакра оставете поне два часа.",
        "waypoints": [
            ("Морска градина, Варна", "43.2072", "27.9231"),
            ("Златни пясъци", "43.2830", "28.0434"),
            ("Балчик", "43.4064", "28.1634"),
            ("Нос Калиакра", "43.3610", "28.4650"),
        ],
    },
    {
        "author": "demo_elena",
        "title": "Витоша: до Черни връх",
        "destination": "Витоша",
        "description": "Класически излет над София. Гледките от върха си струват усилието.",
        "tips": "Времето се сменя бързо, затова носете дъждобран. Лифтът спестява час.",
        "waypoints": [
            ("Златни мостове", "42.5920", "23.2570"),
            ("Алеко", "42.5692", "23.3009"),
            ("Черни връх", "42.5636", "23.2778"),
        ],
    },
    {
        "author": "demo_ivan",
        "title": "Велико Търново и Арбанаси",
        "destination": "Велико Търново",
        "description": "Столицата на средновековна България: крепостта Царевец, старите улици и селото Арбанаси наблизо.",
        "tips": "Вечерното светлинно шоу на Царевец започва след залез. Резервирайте нощувка предварително.",
        "waypoints": [
            ("Царевец", "43.0850", "25.6537"),
            ("Самоводската чаршия", "43.0818", "25.6500"),
            ("Арбанаси", "43.1000", "25.6670"),
        ],
    },
]

# (номер на маршрут, потребител, оценка, текст); никой не оценява собствен маршрут
REVIEWS = [
    (0, "demo_maria", 5, "Невероятна гледка! Препоръчвам на всеки, който обича планината."),
    (0, "demo_petar", 4, "Много хубаво, но изкачването е доста дълго."),
    (0, "demo_elena", 5, "Най-красивата пътека, която съм минавала."),
    (1, "demo_ivan", 4, "Приятна разходка, пловдивчани са късметлии."),
    (1, "demo_petar", 5, "Старият град е истинско съкровище."),
    (2, "demo_maria", 3, "Красиво е, но през лятото е много претъпкано."),
    (2, "demo_ivan", 4, "Калиакра си заслужава пътуването."),
    (3, "demo_ivan", 5, "Перфектен излет за един ден."),
    (3, "demo_maria", 4, "Хубав маршрут, но времето беше капризно."),
    (4, "demo_petar", 4, "Арбанаси е много спокойно и красиво."),
    (4, "demo_elena", 3, "Хубаво, но тръгнах късно и пропуснах шоуто."),
]


class Command(BaseCommand):
    help = "Създава demo потребители, маршрути и отзиви за демонстрация."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Изтрива старите demo данни и ги създава наново.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = User.objects.filter(username__in=DEMO_USERS).delete()
            self.stdout.write(f"Изтрити записи: {deleted}")
        elif User.objects.filter(username__in=DEMO_USERS).exists():
            self.stdout.write("Demo данните вече съществуват. Използвайте --reset, за да ги създадете наново.")
            return

        users = {
            name: User.objects.create_user(
                name, email=f"{name}@example.com", password=DEMO_PASSWORD
            )
            for name in DEMO_USERS
        }

        routes = []
        for data in ROUTES:
            route = Route.objects.create(
                author=users[data["author"]],
                title=data["title"],
                destination=data["destination"],
                description=data["description"],
                tips=data["tips"],
            )
            for index, (name, lat, lng) in enumerate(data["waypoints"]):
                Waypoint.objects.create(
                    route=route, name=name, latitude=lat, longitude=lng, order_index=index
                )
            routes.append(route)

        for route_index, username, rating, text in REVIEWS:
            Review.objects.create(
                route=routes[route_index], author=users[username], text=text, rating=rating
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: {len(users)} потребители, {len(routes)} маршрута, {len(REVIEWS)} отзива. "
                f"Парола на всички demo потребители: {DEMO_PASSWORD}"
            )
        )