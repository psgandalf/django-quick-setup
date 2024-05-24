#!/usr/bin/env python3

import os
import subprocess
import sys
import fileinput

def run_command(command, error_message):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError:
        print(error_message)
        sys.exit(1)

def check_package_versions(requirements_file):
    with open(requirements_file, 'r') as file:
        lines = file.readlines()

    packages = {
        'django': None,
        'django-tailwind': None,
        'whitenoise': None
    }

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue  # Skip comments
        if '==' in line:
            package_name, version = line.split('==')
            packages[package_name.lower()] = version.strip()

    return packages

def main():
    project_name = "core"
    app_name = "app"

    # Check for necessary tools
    print("Checking for necessary tools...")
    run_command("command -v python3 >/dev/null 2>&1", "Python3 is not installed. Aborting.")
    run_command("command -v pip >/dev/null 2>&1", "pip is not installed. Aborting.")
    run_command("command -v npm >/dev/null 2>&1", "npm is not installed. Aborting.")

    # Create virtual environment
    print("Creating virtual environment...")
    run_command("python3 -m venv venv", "Could not create a virtual environment.")

    # Copying activate_this.py
    print("Copying activate_this.py...")
    run_command("cp resourses/activate_this.py venv/bin", "Could not copy activate_this.py.")

    # Activate virtual environment
    print("Activating virtual environment...")
    activate_this = os.path.join(os.getcwd(), "venv", "bin", "activate_this.py")
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

    # Upgrade pip in the virtual environment
    print("Upgrading pip...")
    run_command("venv/bin/pip install --upgrade pip", "Could not upgrade pip.")

        # Install dependencies
    print("Installing dependencies...")
    if os.path.exists("requirements.txt"):
        package_versions = check_package_versions("requirements.txt")
        for package, version in package_versions.items():
            if version is not None:
                print(f"Installing {package} {version}...")
                run_command(f"venv/bin/pip install {package}=={version}", f"Could not upgrade {package}.")
    else:
        run_command("venv/bin/pip install django django-tailwind whitenoise", "Could not install dependencies.")

    # Create Django project
    print(f"Creating Django project: {project_name}...")
    run_command(f"django-admin startproject {project_name}", "Could not create Django project.")

    # Change dir to project_name
    os.chdir(project_name)

    # Create Django app
    print(f"Creating Django app: {app_name}...")
    run_command(f"python manage.py startapp {app_name}", "Could not create Django app.")

    # Install Tailwind and Flowbite
    print("Installing Tailwind CSS and Flowbite...")
    run_command("npm install -D tailwindcss@latest postcss@latest autoprefixer@latest", "Could not install Tailwind CSS.")
    run_command("npm install flowbite", "Could not install Flowbite.")

    # Initialize Tailwind CSS
    print("Initializing Tailwind CSS...")
    run_command("npx tailwindcss init", "Could not initialize Tailwind CSS.")

    # Edit tailwind.config.js
    print("Editing tailwind.config.js for Django and Flowbite...")
    with open("tailwind.config.js" , 'w') as file:
        file.write("/** @type {import('tailwindcss').Config} */\n")
        file.write("module.exports = {\n")
        file.write("  content: [\n")
        file.write("    './templates/**/*.html',\n")
        file.write("    './node_modules/flowbite/**/*.js'\n")
        file.write("  ],\n")
        file.write("  theme: {\n")
        file.write("    extend: {},\n")
        file.write("  },\n")
        file.write("  plugins: [\n")
        file.write("    require('flowbite/plugin')\n")
        file.write("  ],\n")
        file.write("}") 

    # Changning settings.p
    print("Changing settings.py....")
    # Define the lines to be inserted
    lines_to_insert = {
        1: "import os\n",
        "INSTALLED_APPS = [": [
            "    'tailwind',\n"
        ],
        "django.contrib.messages" : [
            "    'whitenoise.runserver_nostatic',\n"
        ],
        "django.middleware.security.SecurityMiddleware": [
            "    'whitenoise.middleware.WhiteNoiseMiddleware',\n"  
        ],
        "STATIC_URL": [
            'STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"\n',
            'STATIC_ROOT = BASE_DIR / "staticfiles"\n',
            'STATICFILES_DIRS = [\n',
            '\tos.path.join(BASE_DIR, "static"),\n',
            ']\n',
            'WHITENOISE_USE_FINDERS = True\n'
        ]
    }

    # Read the file and apply the transformations
    with fileinput.FileInput(f"{project_name}/settings.py", inplace=True) as file:
        for i, line in enumerate(file, start=1):
            if i == 1:
                # Insert import at the beginning
                print(lines_to_insert[1], end="")
            if "INSTALLED_APPS = [" in line:
                # Append lines after INSTALLED_APPS
                print(line, end="")
                print("".join(lines_to_insert["INSTALLED_APPS = ["]), end="")
                continue
            if "'django.contrib.messages'," in line:
                # Append lines after INSTALLED_APPS
                print(line, end="")
                print("".join(lines_to_insert["django.contrib.messages"]), end="")
                continue
            if "django.middleware.security.SecurityMiddleware" in line:
                # Append lines after INSTALLED_APPS
                print(line, end="")
                print("".join(lines_to_insert["django.middleware.security.SecurityMiddleware"]), end="")
                continue
            if "STATIC_URL" in line:
                # Append lines after STATIC_URL
                print(line, end="")
                print("".join(lines_to_insert["STATIC_URL"]), end="")
                continue
            if "'DIRS': []" in line:
                # Replace the DIRS line
                line = line.replace("'DIRS': []", "'DIRS': [BASE_DIR / 'templates']")
            print(line, end="")

    # Create Tailwind CSS input file
    print("Creating Tailwind CSS input file...")
    run_command("mkdir -p static/src/", "Could not create static/src")
    run_command("mkdir -p static/images/", "Could not create static/images")
    run_command("mkdir -p templates/", "Could not create templates")
    run_command("cp ../resourses/_base.html templates/", "Could not copy _base.html")
    run_command("cp ../resourses/index.html templates/", "Could not copy index.html")
    run_command("cp ../images/* static/images", "Could not copy images")
    
    # editing urls.py in app
    print("Editing urls.py in app")
    with open(f"{app_name}/urls.py" , 'w') as file:
        file.write("from .views import index\n")
        file.write("from django.urls import path\n\n")
        file.write("urlpatterns = [\n")
        file.write("    path('', index, name='index')\n")
        file.write("]\n")

    # editing urls.py in project
    print("Editing urls.py in project")
    with open(f"{project_name}/urls.py" , 'w') as file:
        file.write("from django.contrib import admin\n")
        file.write("from django.urls import path, include\n\n")
        file.write("urlpatterns = [\n")
        file.write("    path('admin/', admin.site.urls),\n")
        file.write("    path('', include('app.urls')), \n")
        file.write("]\n")
 
    # editing views.py in app
    print("Editing views.py in app")
    with open(f"{app_name}/views.py" , 'w') as file:
        file.write("from django.shortcuts import render\n\n")
        file.write("def index(request):\n")
        file.write("    return render(request, 'index.html')")

    # creating and editing input.css
    print("Creating and editing input.css")
    os.makedirs(os.path.dirname("static/src/input.css"), exist_ok=True)
    with open("static/src/input.css" , 'w') as file:
        file.write("@tailwind base;\n")
        file.write("@tailwind components;\n")
        file.write("@tailwind utilities;\n")
    
    # Collect static files
    print("Collecting static files...")
    run_command("python manage.py collectstatic --noinput", "Could not collect static files.")
    run_command("npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css", "Could not compile Tailwind CSS.")
    run_command("python manage.py migrate", "Could not migrate database.")

    # Done
    print("Setup complete. Run the following commands to start your project:")
    print("source venv/bin/activate")
    print(f"cd {project_name}")
    print("python manage.py runserver")

if __name__ == "__main__":
    main()
