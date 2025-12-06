from django.urls import path
from . import views

urlpatterns = [

    # ------------------ HOME & STATIC ------------------
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),

    # ------------------ AUTH ------------------
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    # ------------------ UNIVERSITIES ------------------
    path("universities/", views.university_list, name="university_list"),
    path("universities/<int:pk>/", views.university_detail_page, name="university_detail"),

    # ------------------ MODAL DETAIL API ------------------
    path("api/university/<int:pk>/detail/", views.university_detail_api, name="university_detail_api"),

    # ------------------ HEATMAP & FILTER API ------------------
    path("api/universities/map/", views.universities_map_data, name="universities_map_data"),
    path("api/university/filter/", views.university_filter_api, name="university_filter_api"),

    # ------------------ COMPARE ------------------
    path("compare/", views.compare_view, name="compare"),
    path("api/compare/", views.compare_api, name="compare_api"),

    # ------------------ CALCULATOR ------------------
    path("calculator/", views.calculator, name="calculator"),
    path("calculator/result/", views.calculator_result, name="calculator_result"),

    # ------------------ SAVE UNIVERSITY ------------------
    path("api/save_university/<int:uni_id>/", views.save_university_api, name="save_university"),
]
