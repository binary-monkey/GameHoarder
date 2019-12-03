# GameHoarder
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

## Table of Contents
+ [About](#about)
+ [Getting Started](#getting_started)
+ [Deployment](#deployment)
    + [Prerequisites](#prerequisites)
    + [Additional Manual requirements](#additional-manual-requirements)
    + [Additional Docker requirements](#additional-docker-requirements)
    + [Running the containers](#running-the-containers)
+ [Usage](#usage)
+ [Credits](#credits)

## About <a name = "about"></a>
GameHoarder is a django web app aimed to help you organize your video game 
collection and track titles you are interested in.

## Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your 
local machine for development and testing purposes.
See [deployment](#deployment) for notes on how to deploy the project on a
live system.

## Deployment <a name = "deployment"></a>

### Prerequisites <a name = "prerequisites"></a>

A file named `./GameHoarder/local_settings.py` has to be created with the following content:

```python
ALLOWED_HOSTS = ['*']  # or configure your allowed hosts

API_KEY = "<GiantBomb API key>"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gamecollection',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
```

The only parameter that requires changes is `API_KEY`, your GiantBomb API key
should be placed here.

### Additional manual requirements <a name = "additional-manual-requirements"></a>

> Note: **this section is only for manual deployment**.
> Skip if Docker will be used.

* Any GNU/Linux distro. It has been tested on Arch Linux and Windows 10.

* `python3` and `redis-remote` packages.

* Additional Python packages

##### Arch based distros <a name = "arch-based-distros"></a>

```
sudo pacman -S python redis
sudo pip install -r requirements.txt
```

### Additional Docker requirements <a name = "additional-docker-requirements"></a>

> Note: **this section is only for Docker deployment**.
> Skip if it will be deployed manually.

* In order for the MySQL container to work and retain data, an empty folder
needs to be created at the path `$HOME/.var/lib/mysql`. Data from the DB
will be stored there. This path can be changed in `docker-compose.yml`.

* The MySQL and Redis parameters can be configured at will, but they must be
present in the file for `docker-compose` to work. If `Docker` will be used,
do not modify the following parameters: `BROKER_URL`, `CELERY_RESULT_BACKEND`,
`DATABASES.default.HOST`.

### Running the containers <a name = "running-the-containers"></a>

If no additional changes were made to `local_settings.py`, simply run:

```
docker-compose up
```

This should create Redis, MySQL and GameHoarder containers named `redis_iw13`,
`mysql_iw13` and `gamehoarder` respectively.

If `local_settings.py` has additional changes, `Dockerfile` and
`docker-compose.yml` must be changed first.




## Usage <a name = "usage">

> Note: this steps are not required if Docker is the deployment method

GameHoarder uses celery to run asyncronous tasks, to allow celery to work one
should start a redis-server:

```
redis-server
```

and start the celery worker before running the django app:

```
celery -A GameHoarder worker -l info
```

## Credits

https://colorlib.com/wp/template/cloud83/

https://www.flaticon.com/packs/essential-collection

## Credits
- Bootstrap Template based on [Gentelella](https://github.com/ColorlibHQ/gentelella) by Colorlib,
- Landing Page based on [Cloud83](https://colorlib.com/wp/template/cloud83/) by Colorlib, 
- All static photos taken from [Unsplash](https://www.unsplash.com), see detailed information [here](CREDITS.MD).
- Icon Pack from [Essential Collection](https://www.flaticon.com/packs/essential-collection)