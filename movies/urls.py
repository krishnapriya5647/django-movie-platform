from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),

    path('movie/add/', views.add_movie, name='add_movie'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:pk>/edit/', views.edit_movie, name='edit_movie'),
    path('movie/<int:pk>/delete/', views.delete_movie, name='delete_movie'),
    path('movie/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),

    path('category/<slug:slug>/', views.movies_by_category, name='movies_by_category'),
    path('search/', views.search_movies, name='search'),
]
