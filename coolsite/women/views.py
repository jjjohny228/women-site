from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView
from .models import *
from .forms import *
from .utils import DataMixin
menu = [{"title": "О сайте", "url_name": 'about'},
         {"title": "Добавить статью", "url_name": 'add_page'},
         {"title": "Обратная связь", "url_name": 'contact'},
         {"title": "Войти", "url_name": 'login'}]
# def index(request):
#     posts = Women.objects.all()
#     context = {
#         'posts': posts,
#         'menu': menu,
#         'title': "Главная страница",
#         'cat_selected': 0
#     }
#     return render(request, 'women/index.html', context=context)


class WomenHome(DataMixin, ListView):
    model = Women
    template_name = 'women/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        context.update(c_def)
        return context

    def get_queryset(self):
        return Women.objects.filter(is_published=True).select_related('cat')


def post(request, post_id):
    return HttpResponse(f"Отображение статьи под индексом: {post_id}")

def about(request):
    contact_list = Women.objects.all()
    paginator = Paginator(contact_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'women/about.html', {'page_obj': page_obj, "menu": menu, 'title': "О сайте"})


# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#                 form.save()
#                 return redirect('home')
#     else:
#         form = AddPostForm()
#     return render(request, "women/addpage.html", {'form': form, 'menu': menu, 'title': "Добавление статьи"})


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'women/addpage.html'
    login_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление статьи')
        return context | c_def


# def login(request):
#     return HttpResponse("<h1>Тут можно войти</h1>")


# def show_category(request, cat_slug):
#     cat = Category.objects.get(slug=cat_slug)
#     posts = Women.objects.filter(cat_id=cat.id)
#     if len(posts) == 0:
#         raise Http404()
#     context = {
#         'posts': posts,
#         'menu': menu,
#         'title': "Главная страница",
#         'cat_selected': cat_slug
#     }
#     return render(request, 'women/index.html', context=context)


class WomanCategory(DataMixin, ListView):
    model = Women
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(
            title="Категория -" + str(c.name),
            cat_selected=c.slug)
        return context | c_def

    def get_queryset(self):
        return Women.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')


# def show_post(request, post_slug):
#     post = get_object_or_404(Women, slug=post_slug)
#     context = {
#         'post': post,
#         'menu': menu,
#         'title': post.title,
#         'cat_selected': post.cat.slug
#     }
#     return render(request, 'women/post.html', context=context)


class ShowPost(DataMixin, DetailView):
    model = Women
    template_name = 'women/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'], cat_selected=context['post'].cat.slug)
        return context | c_def


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'women/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        return context | c_def

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'women/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return context | c_def

    def get_success_url(self):
        return reverse_lazy('home')


class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Обратная связь')
        return context | c_def

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')



def logout_user(request):
    logout(request)
    return redirect('login')
def NotFound(request, exception):
    return HttpResponseNotFound('Страница не найдена')