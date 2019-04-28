[![Build Status](https://travis-ci.com/Rukshar/capstone-class-10.svg?branch=master)](https://travis-ci.com/Rukshar/capstone-class-10)

# Xomnia Capstone Project Class 10: Jukebox App
Jukebox app to make the friday afterwork social drinks more fun by having a voting-based music system. Additionally 
our capstone project which will conclude our traineeship. 

## Dependencies

Make sure to install all dependencies, either with conda or pip. 


### Conda

##### New environment
If you don't have an environment yet:


```conda env create -f environment.yml```

##### Existing environment
If you already have created the environment:

```conda env update -f environment.yml```

##### Activate the environment

```source activate borrelai```

### Pip

Optionally you can also use pip to install the requirements:

```pip install -r requirements.txt```


##### Potential psycopg2 issues

In addition to the dependencies in `requirements.txt`, you may need to install additional dependencies for the 
postgres database. Run the following command only if installing of `psycopg2` dependency fails:

For ubuntu:

`sudo apt-get install libpq-dev`

For Mac OS X:

`brew install postgresql`

### Spotify API

To able to use Spotify's API, we have to get credentials for our account. Please follow the 
steps provided [here](https://developer.spotify.com/documentation/general/guides/app-settings/). 

Once you have registered, rename the `spotipy_config_example.py` to `spotipy_config.py` and add the `CLIENT_ID` and `CLIENT_SECRET` to this file. 

Find a playlist with your song collection in the Spotify desktop app and right click on it to get the Spotify URI 
and add it to the config as `SOURCE_PLAYLIST_URI`. 

Then, create an empty playlist, get the URI and add it as `TARGET_PLAYLIST_URI` to the config. 

__Optionally, you  can also set them as environment variables like so:__

```
export SPOTIPY_CLIENT_ID='your-spotify-client-id'
export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
```

Last, but not least, whitelist the `http://localhost/` in the Spotify frontend as described 
[here](https://developer.spotify.com/documentation/general/guides/app-settings/) 

# Launching the app

## Docker Compose

The easiest way to launch is to use docker-compose. Make sure to adjust the value for `volumes` in the `docker-compose.yml`
file to match your desired volume mapping. 

If you choose to follow this README, adjusting is not necessary, but we have to create a local volume for the database:
```
mkdir -p $HOME/docker/volumes/postgres
```

Then to launch you can simply run the following command from project root:

```
docker-compose up
```

For now, the jukebox has to be started seperately and locally due to an authentication prompt from Spotify API. To do so
run from root:


```
python run_jukebox.py
```

And follow the authentication steps.

## Run seperately
You can also choose to run the services seperately.
 
#### PostgreSQL Database

When launching the container we map the exposed port 5432 to our local port and map our local volume
that we created in the previous step to the `/var/lib/postgresql/data` volume in the container:

```
docker run --rm \
--name pg-docker \
-e POSTGRES_PASSWORD=docker -d \
-p 5432:5432 \
-v $HOME/docker/volumes/postgres:/var/lib/postgresql/data \
  postgres
```

For more background info on postgreSQL in docker look 
[here](https://hackernoon.com/dont-install-postgres-docker-pull-postgres-bee20e200198)


### Webapp


##### Development server

To start the flask app on a development server, simply run: 

```
python run_flask.py
```


##### WSGI server

For `gunicorn`:

```
gunicorn -w 4 -b 0.0.0.0:8080 src.flaskapp.app:app
```

For `gevent`:

```
python run_flask_gevent.py
```



After launching, the Flask app is available at:
 
 `http://localhost:5000`


#### Jukebox

To launch the jukebox, simply run:

```
python run_jukebox.py
```
