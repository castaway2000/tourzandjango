GENERAL DESCRIPTION
To launch the project locally you should install packages from requirements.txt and that's it.

To launch the project on the webserver, you may follow any instruction for such process, which you can find
in the Internet. For example, like this one:
http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/

Static and media file for webserver are hosted on 3s bucket on AWS


PRODUCTION SETTING UP
In terms of project settings, the only point which you should to adjust is deleting "_2" in this line in settings.py:
from .prod_settings_2 import *

File tourzan/prod_settings contains some settings for Production server, which overwrite original settings
from setting.py: for example db settings, braintree credentials, email sending credentials.


A virtual environment is created on production server under python3 and it is situated in the /webapps/projects.
A virtual environment was created under user djangotourzan, which has limited access rights only for virtual environment
folder and for modifying files inside it.

A project folder is inside this virtual environment folder. A project's folder name is "tourzan".
A git repository is initialized inside this project folder, so it can be updated via git.

Django project is launched with combination of nginx server and gunicorn. Nginx serves static files.
Also nginx communicates with gunicorn via internal socket, what allows to use https connection on the server.

Also gunicorn is launched via ubuntu "supervisor", which works on background and will launch gunicron automatically if
server will be restarted.


PRODUCTION SERVER UPDATES

Main branch in the repository, which is used for server updates, is "master" branch.

Updates of the server can be make in the following way:
-sign up under djangotourzan user: sudo su - djangotourzan
-access project folder (with git repository inside): cd tourzan
-run git pull command using your connected "remote" instance. For example git pull origin master
-if any new migrations were created - run this command to apply them to Production db:
    python manage.py migrate

-exit virtual environment by typing "exit"
-run a command to restart supervisor and all the instances which it tracks (particulary gunicorn):
    sudo supervisorctl restart all
        or
    some certain instance: sudo supervisorctl restart [instane name] ("website" or "general" - need to doublecheck its name on Production)





