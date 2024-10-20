#!/usr/bin/env python3
import fileinput
import os
import subprocess
import sys


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
    run_command("uv init", "Could not init a virtual environment.")
    run_command("uv venv", "Could not create a virtual environment.")

    # Install dependencies
    print("Installing dependencies...")
    if os.path.exists("requirements.txt"):
        package_versions = check_package_versions("requirements.txt")
        for package, version in package_versions.items():
            if version is not None:
                print(f"Installing {package} {version}...")
                run_command(f"uv add {package}=={version}", f"Could not upgrade {package}.")
    else:
        print("requirements.txt not found. Installing default dependencies...")
        run_command("uv add django django-tailwind whitenoise", "Could not install dependencies.")
    
    # Create Django project
    print(f"Creating Django project: {project_name}...")
    run_command(f"uv run django-admin startproject {project_name}", "Could not create Django project.")
    
    # Change dir to project_name
    os.chdir(project_name)
    
    # Create Django app
    print(f"Creating Django app: {app_name}...")
    run_command(f"uv run manage.py startapp {app_name}", "Could not create Django app.")
    
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

    # Changing settings.py....
    print("Changing settings.py....")
    settings_file = f"{project_name}/settings.py"
    lines_to_insert = {
        'import': "import os\n",
        'INSTALLED_APPS': "    'tailwind',\n",
        'MIDDLEWARE': "    'whitenoise.middleware.WhiteNoiseMiddleware',\n",
        'TEMPLATES': "        'DIRS': [BASE_DIR / 'templates'],\n",
        'STATIC_URL': [
            "STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'\n",
            "STATIC_ROOT = BASE_DIR / 'staticfiles'\n",
            "STATICFILES_DIRS = [\n",
            "    os.path.join(BASE_DIR, 'static'),\n",
            "]\n",
            "WHITENOISE_USE_FINDERS = True\n"
        ]
    }

    with open(settings_file, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    in_installed_apps = False
    installed_apps = []
    import_os_added = False

    for line in lines:
        if line.strip().startswith('from pathlib import Path'):
            modified_lines.append(line)
            modified_lines.append(lines_to_insert['import'])
            import_os_added = True
        elif line.strip().startswith('INSTALLED_APPS'):
            in_installed_apps = True
            installed_apps.append(line)
        elif in_installed_apps and line.strip().startswith(']'):
            installed_apps.append(lines_to_insert['INSTALLED_APPS'])
            installed_apps.append(line)
            modified_lines.extend(installed_apps)
            in_installed_apps = False
        elif in_installed_apps:
            installed_apps.append(line)
        elif line.strip().startswith('MIDDLEWARE'):
            modified_lines.append(line)
            modified_lines.append(lines_to_insert['MIDDLEWARE'])
        elif "'DIRS': []," in line:
            modified_lines.append(lines_to_insert['TEMPLATES'])
        elif line.strip().startswith('STATIC_URL'):
            modified_lines.append(line)
            modified_lines.extend(lines_to_insert['STATIC_URL'])
        else:
            modified_lines.append(line)

    # Add whitenoise.runserver_nostatic to INSTALLED_APPS
    for i, line in enumerate(modified_lines):
        if line.strip().startswith('INSTALLED_APPS'):
            modified_lines.insert(i + 2, "    'whitenoise.runserver_nostatic',\n")
            break

    # Ensure import os is added if it wasn't found
    if not import_os_added:
        modified_lines.insert(0, lines_to_insert['import'])

    with open(settings_file, 'w') as file:
        file.writelines(modified_lines)

    # Create Tailwind CSS input file
    print("Creating Tailwind CSS input file...")
    run_command("mkdir -p static/src/", "Could not create static/src")
    run_command("mkdir -p static/images/", "Could not create static/images")
    run_command("mkdir -p static/js/", "Could not create static/js")
    run_command("mkdir -p templates/", "Could not create templates")
    run_command("cp ../resourses/templates/* templates/", "Could not copy templates")
    run_command("cp ../resourses/js/* static/js/", "Could not copy js")
    run_command("cp ../resourses/images/* static/images", "Could not copy images")
    
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
    run_command("uv run manage.py collectstatic --noinput", "Could not collect static files.")
    run_command("npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css", "Could not compile Tailwind CSS.")
    run_command("uv run manage.py migrate", "Could not migrate database.")

    # Done
    print("Setup complete. Run the following commands to start your project:")
    print("source .venv/bin/activate")
    print(f"cd {project_name}")
    print("uv run manage.py runserver")

if __name__ == "__main__":
    main()
