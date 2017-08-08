To launch the project locally you should install packages from requirements.txt and that's it.

To launch the project on the webserver, you may follow any instruction for such process, which you can find
in the Internet. For example, like this one:
http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/

Static and media file for webserver are hosted on 3s bucket on AWS

In terms of project settings, the only point which you should to adjust is deleting "_2" in this line in settings.py:
from .prod_settings_2 import *

File tourzan/prod_settings contains some settings for Production server, which overwrite original settings
from setting.py: for example db settings, braintree credentials, email sending credentials.