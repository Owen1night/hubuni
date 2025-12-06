from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """
    Направления: IT, медицина, бизнес, гранты и т.п.
    Используем для фильтра «Направления» и для чипов на главной.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Слаг (для URL)")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class University(models.Model):
    CITY_CHOICES = [
        ("almaty", "Алматы"),
        ("astana", "Астана"),
        ("shymkent", "Шымкент"),
        ("other", "Другой город"),
    ]

    TYPE_CHOICES = [
        ("public", "Государственный"),
        ("private", "Частный"),
    ]

    # Базовая инфа
    name = models.CharField(max_length=255, verbose_name="Полное название")
    short_name = models.CharField(max_length=100, blank=True, verbose_name="Краткое название")
    city = models.CharField(max_length=50, choices=CITY_CHOICES, verbose_name="Город")
    uni_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Тип вуза",
        default="public",
    )
    address = models.CharField(max_length=255, blank=True, verbose_name="Адрес")
    website = models.URLField(blank=True, verbose_name="Сайт")

    description = models.TextField(blank=True, verbose_name="Описание (для модалки)")

    main_image = models.ImageField(
        upload_to="universities/",
        blank=True,
        null=True,
        verbose_name="Главное фото",
    )

    # Категории (IT, медицина и т.д.)
    categories = models.ManyToManyField(
        Category,
        related_name="universities",
        blank=True,
        verbose_name="Категории",
    )

    # Стоимость обучения (за год)
    tuition_min = models.PositiveIntegerField(
        verbose_name="Минимальная стоимость в год, ₸",
        help_text="Например, 1200000",
    )
    tuition_max = models.PositiveIntegerField(
        verbose_name="Максимальная стоимость в год, ₸",
        help_text="Например, 1800000",
    )

    has_grants = models.BooleanField(default=False, verbose_name="Есть гранты")

    # Рейтинг и популярность
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        verbose_name="Рейтинг (например, 4.6)",
    )
    popularity_score = models.PositiveIntegerField(
        default=0,
        verbose_name="Популярность (чем больше, тем больше точка на карте)",
    )

    # Языки обучения
    language_kz = models.BooleanField(default=False, verbose_name="Казахский язык")
    language_ru = models.BooleanField(default=False, verbose_name="Русский язык")
    language_en = models.BooleanField(default=False, verbose_name="Английский язык")

    # Инклюзивность и условия
    mobility_access = models.BooleanField(
        default=False,
        verbose_name="Доступно для людей с ограниченной мобильностью",
    )
    sign_language = models.BooleanField(
        default=False,
        verbose_name="Есть сурдоперевод",
    )
    low_vision_support = models.BooleanField(
        default=False,
        verbose_name="Поддержка слабовидящих",
    )
    dormitory_available = models.BooleanField(
        default=False,
        verbose_name="Есть общежитие",
    )

    # Требования для поступления
    gpa_required = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Минимальный GPA",
    )
    ielts_required = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Минимальный IELTS",
    )
    ent_required = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Минимальный балл ЕНТ",
    )

    # 3D виртуальный тур (НОВЫЙ)
    virtual_tour_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на 3D-тур (виртуальная экскурсия)",
    )

    # Координаты для карты
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Широта (для карты)",
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Долгота (для карты)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Университет"
        verbose_name_plural = "Университеты"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def tuition_level(self):
        """
        Делим цены для тепловой карты:
        - low  : зелёный
        - mid  : жёлтый
        - high : красный
        """
        avg = (self.tuition_min + self.tuition_max) / 2
        if avg < 1_200_000:
            return "low"
        elif avg < 1_800_000:
            return "mid"
        return "high"


class Program(models.Model):
    """
    Отдельные программы внутри вуза (IT, Data Science и т.п.).
    """
    DEGREE_CHOICES = [
        ("bachelor", "Бакалавриат"),
        ("master", "Магистратура"),
        ("phd", "Докторантура"),
    ]

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="programs",
        verbose_name="Университет",
    )
    name = models.CharField(max_length=200, verbose_name="Название программы")
    degree_type = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES,
        default="bachelor",
        verbose_name="Уровень",
    )
    duration_years = models.PositiveIntegerField(
        default=4,
        verbose_name="Длительность обучения (лет)",
    )

    # Языки конкретной программы
    language_kz = models.BooleanField(default=False, verbose_name="Казахский язык")
    language_ru = models.BooleanField(default=False, verbose_name="Русский язык")
    language_en = models.BooleanField(default=False, verbose_name="Английский язык")

    tuition_per_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Стоимость в год (если отличается от вуза)",
    )

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def __str__(self):
        return f"{self.name} ({self.university.short_name or self.university.name})"


class UserProfile(models.Model):
    """
    Профиль пользователя (для “Для меня”, сохранённых вузов и рекомендаций)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    full_name = models.CharField(max_length=255, blank=True, verbose_name="Полное имя")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Телефон")

    planned_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Планируемый год поступления",
    )

    interested_categories = models.ManyToManyField(
        Category,
        related_name="interested_users",
        blank=True,
        verbose_name="Интересующие направления",
    )

    # Личные баллы для анализа "подхожу ли я"
    my_gpa = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Мой GPA",
    )
    my_ielts = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Мой IELTS",
    )
    my_ent = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Мой балл ЕНТ",
    )

    def __str__(self):
        return self.full_name or self.user.username


class SavedUniversity(models.Model):
    """
    Сохранённые пользователем университеты (профиль + calculator mode)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_universities",
    )
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="saved_by_users",
    )
    in_calculator = models.BooleanField(
        default=False,
        verbose_name="Добавлен в Calculator Mode",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сохранённый университет"
        verbose_name_plural = "Сохранённые университеты"
        unique_together = ("user", "university")

    def __str__(self):
        return f"{self.user.username} → {self.university.short_name or self.university.name}"
