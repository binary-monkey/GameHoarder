# GameHoarder
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

## Table of Contents
+ [About](#about)
+ [Getting Started](#getting_started)
+ [Usage](#usage)

## About <a name = "about"></a>
GameHoarder is a django web app aimed to help you organize your video game collection and track titles you are interested in.
## Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.


## Prerequisites

* Any GNU/Linux Distro, i have tested it on Arch, although it should run on Windows.
* A Transmission Server, see [Deployment](https://github.com/rafaelromon/RSSTorrentDownloader#deployment) for additional information.
* python3 and transmission-remote packages.
* Additional Python packages: feedparser and pytz.

##### Arch based Distros
```
sudo pacman -S python redis
sudo pip install -r requirements.txt

```


## Usage <a name = "usage"></a>

GameHoarder uses celery to run asyncronous tasks, to allow celery to work one should start a redis-server:

```
redis-server
```

and start the celery worker before running the django app:

```
celery -A GameHoarder worker -l info
```
