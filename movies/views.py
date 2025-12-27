from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from .forms import UserRegisterForm, MovieForm, UserProfileForm, CommentForm
from .models import Movie, Category, Favorite
from django.conf import settings

def home(request):
    movies = Movie.objects.order_by('-created_at')
    categories = Category.objects.all()
    featured_movies = movies.filter(poster__isnull=False).exclude(poster='')[:30]

    return render(request, 'movies/home.html', {
        'movies': movies,
        'categories': categories,
        'featured_movies': featured_movies,
    })
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            subject = "Welcome to Movie Platform"
            message = f"Hi {user.first_name},\n\nWelcome to our Movie Website!"
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, [user.email], fail_silently=True)

            return redirect('movies:login')
    else:
        form = UserRegisterForm()

    return render(request, 'movies/register.html', {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('movies:home')
        else:
            error = "Invalid username or password"
            return render(request, 'movies/login.html', {"error": error})
    return render(request, 'movies/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('movies:login')

@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('movies:profile')
    else:
        form = UserProfileForm(instance=request.user)

    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'movies/profile.html', {
        'form': form,
        'favorites': favorites,
    })

from .forms import MovieForm

@login_required
def add_movie(request):
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES)  
        if form.is_valid():
            movie = form.save(commit=False)
            movie.added_by = request.user
            movie.save()
            return redirect('movies:home')
    else:
        form = MovieForm()

    return render(request, 'movies/movie_form.html', {
        'form': form,
        'title': 'Add Movie',
    })

@login_required
def edit_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.added_by != request.user:
        return redirect('movies:home')

    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES, instance=movie)  
        if form.is_valid():
            form.save()
            return redirect('movies:movie_detail', pk=movie.pk)
    else:
        form = MovieForm(instance=movie)

    return render(request, 'movies/movie_form.html', {
        'form': form,
        'title': 'Edit Movie',
    })

@login_required
def delete_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if movie.added_by != request.user:
        return redirect('movies:home')

    if request.method == "POST":
        movie.delete()
        return redirect('movies:home')

    return render(request, 'movies/confirm_delete.html', {'movie': movie})

@login_required(login_url='movies:login')
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    comments = movie.comments.all().order_by('-created_at')

    if request.method == "POST":
        c_form = CommentForm(request.POST)
        if c_form.is_valid():
            comment = c_form.save(commit=False)
            comment.user = request.user
            comment.movie = movie
            comment.save()
            return redirect('movies:movie_detail', pk=pk)
    else:
        c_form = CommentForm()

    is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'comments': comments,
        'comment_form': c_form,
        'is_favorite': is_favorite,
    })

@login_required
def toggle_favorite(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        fav.delete()
    return redirect('movies:movie_detail', pk=pk)

def movies_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    movies = category.movies.all()
    return render(request, 'movies/category_list.html', {
        'category': category,
        'movies': movies,
    })

def search_movies(request):
    query = request.GET.get('q', '')
    movies = []
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(actors__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    return render(request, 'movies/search_results.html', {
        'query': query,
        'movies': movies,
    })
