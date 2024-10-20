from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-todo/', views.add_todo, name='add_todo'),
    path('remove-todo/<int:todo_id>/', views.remove_todo, name='remove_todo'),
    path('toggle-todo/<int:todo_id>/', views.toggle_todo, name='toggle_todo'),
]