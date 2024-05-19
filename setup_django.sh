#!/bin/bash

# Exit on error
set -e

# Variables
PROJECT_NAME="core"
APP_NAME="app"

# Ensure Python and necessary tools are installed
echo "Checking for necessary tools..."
command -v python3 >/dev/null 2>&1 || { echo "Python3 is not installed. Aborting."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo "pip is not installed. Aborting."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is not installed. Aborting."; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing django-tailwind..."
pip install django-tailwind

echo "Installing django-browser-reload..."
pip install django-browser-reload

echo "Installing whitenoise..."
pip install whitenoise

# Install Django
echo "Installing Django..."
pip install django

# Create Django project
echo "Creating Django project: $PROJECT_NAME..."
django-admin startproject $PROJECT_NAME

cd $PROJECT_NAME

# Create Django app
echo "Creating Django app: $APP_NAME..."
python manage.py startapp $APP_NAME

# Install Tailwind and Flowbite
echo "Installing Tailwind CSS and Flowbite..."
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
npm install flowbite

# Initialize Tailwind CSS
echo "Initializing Tailwind CSS..."
npx tailwindcss init

# Configure Tailwind CSS
echo "Configuring Tailwind CSS..."
cat > tailwind.config.js <<EOL
module.exports = {
  content: [
    './templates/**/*.html',
    './$APP_NAME/templates/**/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
}
EOL

# Create postcss.config.js
echo "Creating postcss.config.js..."
cat > postcss.config.js <<EOL
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOL

# Update Django settings
echo "Updating Django settings..."
sed -i '1iimport os' "$PROJECT_NAME/settings.py"
sed -i "/INSTALLED_APPS = \[/a \ \ \ \ 'django_browser_reload'," $PROJECT_NAME/settings.py
sed -i "/INSTALLED_APPS = \[/a \ \ \ \ 'tailwind'," $PROJECT_NAME/settings.py
sed -i '/STATIC_URL/aSTATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"\nSTATIC_ROOT = BASE_DIR / "staticfiles"\nSTATICFILES_DIRS = [\n\tos.path.join(BASE_DIR, "static"),\n]\nWHITENOISE_USE_FINDERS = True' "$PROJECT_NAME/settings.py"
sed -i "s|'DIRS': \[\],|'DIRS': \[BASE_DIR / 'templates'\],|" "$PROJECT_NAME/settings.py"

# Create Tailwind CSS input file
echo "Creating Tailwind CSS input file..."
mkdir -p static/src/
mkdir -p static/images/
cat > static/src/input.css <<EOL
@tailwind base;
@tailwind components;
@tailwind utilities;
EOL

echo $PROJECT_NAME

# Add STATIC_ROOT to settings.py
echo "Adding STATIC_ROOT to Django settings..."
sed -i "/^STATIC_URL = /a STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')" $PROJECT_NAME/settings.py

# Update base template
echo "Updating base template..."
mkdir -p templates
cat > templates/_base.html <<EOL
{% load static %}

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Django + Tailwind CSS + Flowbite</title>

    <link rel="stylesheet" href="{% static 'src/output.css' %}" />
  </head>
  <body class="bg-green-50">
    <!-- Add this -->
    <nav class="bg-green-50 border-gray-200 px-2 sm:px-4 py-2.5 rounded dark:bg-gray-800">
      <div class="container flex flex-wrap items-center justify-between mx-auto">
        <a href="#" class="flex items-center">
          <img src="{% static 'images/logo.svg' %}" class="h-6 mr-3 sm:h-9" alt="Flowbite Logo" />
          <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">Flowbite Django</span>
        </a>
        <button data-collapse-toggle="mobile-menu" type="button" class="inline-flex items-center p-2 ml-3 text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="mobile-menu" aria-expanded="false">
          <span class="sr-only">Open main menu</span>
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
          </svg>
          <svg class="hidden w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
        <div class="hidden w-full md:block md:w-auto" id="mobile-menu">
          <ul class="flex flex-col mt-4 md:flex-row md:space-x-8 md:mt-0 md:text-sm md:font-medium">
            <li>
              <a href="#" class="block py-2 pl-3 pr-4 text-white bg-green-700 rounded md:bg-transparent md:text-green-700 md:p-0 dark:text-white" aria-current="page">Home</a>
            </li>
            <li>
              <a href="#" class="block py-2 pl-3 pr-4 text-gray-700 border-b border-gray-100 hover:bg-gray-50 md:hover:bg-transparent md:border-0 md:hover:text-green-700 md:p-0 dark:text-gray-400 md:dark:hover:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700">About</a>
            </li>
            <li>
              <a href="#" class="block py-2 pl-3 pr-4 text-gray-700 hover:bg-gray-50 md:hover:bg-transparent md:border-0 md:hover:text-green-700 md:p-0 dark:text-gray-400 md:dark:hover:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Contact</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <!-- End of new HTML -->

    <div class="container mx-auto mt-4">
      {% block content %}

      {% endblock %}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://unpkg.com/htmx.org@1.9.12" integrity="sha384-ujb1lZYygJmzgSwoxRggbCHcjc0rB2XoQrxeTUQyRjrOnlCoYta87iKBWq3EsdM2" crossorigin="anonymous"></script>
  </body>
</html>
EOL

# Update index template
echo "Updating index template..."
cat > templates/index.html <<EOL
{% extends '_base.html' %}
{% load static %}
{% block content %}
  <h1 class="mb-6 text-3xl text-green-800">Django + Tailwind CSS + Flowbite</h1>

  <div class="flex space-x-4">
    <div class="max-w-sm bg-white border border-gray-200 rounded-lg shadow-md dark:bg-gray-800 dark:border-gray-700">
      <a href="#"><img class="rounded-t-lg" src="{% static 'images/cat.jpg' %}" alt="" /></a>
      <div class="p-5">
        <a href="#"><h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Django + Tailwind CSS</h5></a>
        <p class="font-normal text-gray-700 dark:text-gray-400">An example page on a Django setup with:</p>
        <ul>
          <li>Tailwind</li>
          <li>Flowbite</li>
          <li>Whitenoise</li>
          <li>Alpinejs</li>
          <li>htmx</li>
        </ul>
      </div>
    </div>
    <div class="max-w-sm bg-white border border-gray-200 rounded-lg shadow-md dark:bg-gray-800 dark:border-gray-700">
          <img class="rounded-t-lg" src="{% static 'images/dog.jpg' %}" alt="" />
        <div class="p-5">
          <a href="#"><h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Alpinejs and htmx</h5></a>
          <p class="font-normal text-gray-700 dark:text-gray-400">This is some text beneath the second card image.</p>
          <h1 x-data="{ message: 'I ❤️ Alpine' }" x-text="message"></h1>
          <div x-data="{ count: 0 }">
            <button x-on:click="count++" type="button" class="mt-3 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Increment</button>
            <span x-text="count"></span>
          </div>
          <h1 >I ❤️ Htmx</h1>
            <button hx-on:click="alert('Clicked!')" type="button" class="mt-3 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Click me!</button>
            Click me!
        </button>
        </div>
      </div>
{% endblock %}
EOL

echo "Adding app/urls.py"
cat > $APP_NAME/urls.py <<EOL
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
EOL

echo "Adding app/views.py"
cat > $APP_NAME/views.py <<EOL
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
EOL

echo "Add include to app.urls un core.urls"
sed -i 's/from django.urls import path/from django.urls import include, path/' "$PROJECT_NAME/urls.py"
sed -i "/path('admin\/', admin.site.urls)/a\ \tpath('', include('app.urls'))," "$PROJECT_NAME/urls.py"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css

echo "Migrating database..."
python manage.py migrate

echo "Copying images..."
cp ../images/* static/images/
# Done
echo "Setup complete. Run the following commands to start your project:"
echo "source venv/bin/activate"
echo "cd $PROJECT_NAME"
echo "python manage.py runserver"
