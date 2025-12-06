from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .forms import RegisterForm, EmailLoginForm
from .models import University, Category, UserProfile, SavedUniversity


# -------------------- STATIC PAGES --------------------

def about(request):
    return render(request, "core/about.html")


# -------------------- AUTH: REGISTER --------------------

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data["full_name"]
            email = form.cleaned_data["email"].lower()
            phone = form.cleaned_data["phone"]
            password = form.cleaned_data["password1"]

            # user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            user.first_name = full_name
            user.save()

            # profile
            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                phone=phone
            )

            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "core/register.html", {"form": form})


# -------------------- AUTH: LOGIN --------------------

def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]

            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                form.add_error(None, "Неверный email или пароль.")
    else:
        form = EmailLoginForm()

    return render(request, "core/login.html", {"form": form})


# -------------------- AUTH: LOGOUT --------------------

def logout_view(request):
    logout(request)
    return redirect("home")


# -------------------- AUTH: PROFILE --------------------

@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)

    saved_unis = (
        SavedUniversity.objects
        .filter(user=request.user)
        .select_related("university")
        .order_by("-created_at")
    )

    return render(request, "core/profile.html", {
        "profile": profile,
        "saved_unis": saved_unis,
    })


# -------------------- HOME PAGE --------------------

def home(request):
    category_slug = request.GET.get("category")
    limit = request.GET.get("limit")

    try:
        limit = int(limit) if limit else 6
    except ValueError:
        limit = 6

    categories = Category.objects.all().order_by("name")
    qs = University.objects.prefetch_related("categories").order_by("-popularity_score")

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        qs = qs.filter(categories=selected_category)

    total_count = qs.count()
    universities = qs[:limit]

    context = {
        "categories": categories,
        "selected_category": selected_category,
        "universities": universities,
        "show_more": total_count > limit,
        "next_limit": limit + 6,
        "total_count": total_count,
        "shown_count": len(universities),
    }

    return render(request, "core/index.html", context)


# -------------------- UNIVERSITY PAGES --------------------

def university_list(request):
    return render(request, "core/university_list.html")


def university_detail_page(request, pk):
    uni = get_object_or_404(University, pk=pk)
    return render(request, "core/university_detail.html", {"uni": uni})


# -------------------- API: MODAL DETAIL --------------------

def university_detail_api(request, pk):
    uni = get_object_or_404(University, pk=pk)

    # сохранял ли пользователь этот вуз
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedUniversity.objects.filter(
            user=request.user,
            university=uni
        ).exists()

    html = render_to_string(
        "core/university_modal_detail.html",
        {
            "uni": uni,
            "is_saved": is_saved,
            "user": request.user,
        },
        request=request,   # важно: чтобы csrf_token работал в модалке
    )

    return HttpResponse(html)


# -------------------- API: SAVE / UNSAVE UNIVERSITY --------------------

@require_POST
@login_required
def save_university_api(request, uni_id):
    """
    Toggle-сохранение университета:
    - если уже сохранён -> удалить
    - если нет -> сохранить
    """
    user = request.user
    uni = get_object_or_404(University, pk=uni_id)

    existing = SavedUniversity.objects.filter(user=user, university=uni).first()

    if existing:
        existing.delete()
        message = "Университет удалён из сохранённых"
        status = "removed"
    else:
        SavedUniversity.objects.create(user=user, university=uni)
        message = "Университет сохранён!"
        status = "added"

    return JsonResponse({"message": message, "status": status})


# -------------------- HEATMAP API --------------------

def universities_map_data(request):
    universities = University.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )

    data = []
    for u in universities:
        avg_price = int((u.tuition_min + u.tuition_max) / 2)

        data.append({
            "id": u.id,
            "name": u.name,
            "lat": u.latitude,
            "lng": u.longitude,
            "image": u.main_image.url if u.main_image else "",
            "avg_price": avg_price,
            "popularity_score": u.popularity_score,
            "tuition_level": u.tuition_level,
        })

    return JsonResponse({"universities": data})


# -------------------- CALCULATOR --------------------

def calculator(request):
    universities = University.objects.prefetch_related("categories").order_by("name")
    return render(request, "core/calculator.html", {
        "universities": universities,
    })


def calculator_result(request):
    return render(request, "core/calculator_result.html")


# -------------------- COMPARE --------------------

def compare_view(request):
    return render(request, "core/compare.html")


def compare_api(request):
    ids = request.GET.get("ids")

    if not ids:
        return JsonResponse({"universities": []})

    id_list = [int(i) for i in ids.split(",") if i.isnumeric()]
    unis = University.objects.filter(id__in=id_list)

    data = []
    for u in unis:
        data.append({
            "id": u.id,
            "name": u.name,
            "city": u.get_city_display(),
            "price_min": u.tuition_min,
            "price_max": u.tuition_max,
            "rating": u.rating,
            "categories": [c.name for c in u.categories.all()],
            "grants": u.has_grants,
            "image": u.main_image.url if u.main_image else "",
        })

    return JsonResponse({"universities": data})


# -------------------- FILTER API --------------------

def university_filter_api(request):
    qs = University.objects.all()

    city = request.GET.get("city")
    type = request.GET.get("type")
    grants = request.GET.get("grants")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    lang = request.GET.get("lang")
    dorm = request.GET.get("dorm")

    if city:
        qs = qs.filter(city=city)

    if type:
        qs = qs.filter(uni_type=type)

    if grants in ["0", "1"]:
        qs = qs.filter(has_grants=bool(int(grants)))

    if min_price:
        qs = qs.filter(tuition_min__gte=int(min_price))

    if max_price:
        qs = qs.filter(tuition_max__lte=int(max_price))

    if lang == "kz":
        qs = qs.filter(language_kz=True)
    elif lang == "ru":
        qs = qs.filter(language_ru=True)
    elif lang == "en":
        qs = qs.filter(language_en=True)

    if dorm in ["0", "1"]:
        qs = qs.filter(dormitory_available=bool(int(dorm)))

    data = []
    for u in qs:
        data.append({
            "id": u.id,
            "name": u.name,
            "city": u.get_city_display(),
            "tuition_min": u.tuition_min,
            "tuition_max": u.tuition_max,
            "rating": float(u.rating),
            "categories": [c.name for c in u.categories.all()],
            "grants": u.has_grants,
            "image": u.main_image.url if u.main_image else "",
        })

    return JsonResponse({"universities": data})
