from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    todos = request.session.get('todos', [])
    return render(request, 'index.html', {'todos': todos})

def add_todo(request):
    todos = request.session.get('todos', [])
    new_todo = request.POST.get('todo')
    if todos:
        new_id = max(todo['id'] for todo in todos) + 1
    else:
        new_id = 1
    new_todo = {'id': new_id, 'text': new_todo, 'completed': False}
    todos.append(new_todo)
    request.session['todos'] = todos
    request.session.modified = True
    return render(request, 'todo_list.html', {'todos': todos})

def remove_todo(request, todo_id):
    todos = request.session.get('todos', [])
    todos = [todo for todo in todos if todo['id'] != todo_id]
    request.session['todos'] = todos
    request.session.modified = True
    return render(request, 'todo_list.html', {'todos': todos})

def toggle_todo(request, todo_id):
    todos = request.session.get('todos', [])
    todo = next((todo for todo in todos if todo['id'] == todo_id), None)
    if todo:
        todo['completed'] = not todo['completed']
        request.session['todos'] = todos
        request.session.modified = True
        return render(request, 'todo_list.html', {'todos': todos})
    return HttpResponse("Todo not found", status=404)