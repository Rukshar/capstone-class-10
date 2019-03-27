# Xomnia Capstone Project Class 10: Jukebox App


## Dependencies

Make sure to install all dependencies. If you don't have an environment yet:

```conda env create -f environment.yml```

If you already have created the environment:

```conda env update -f environment.yml```

## Secrets 

Copy your .secrets file to the `FlaskApp/` folder.


## Music directory

Create a `music/` directory in the project root folder:

```mkdir music```

And place several `.mp3` or `.m4a` files in this folder. Make sure the songs have metadata available related to:
- Song
- Artist
- Filename
- Duration

## Launch the app

First, we have to make sure the database is populated and the jukebox is started:

```python Jukebox/jukebox_start.py```

Then we can run the flask application on localhost:5000:

```python FlaskApp/app.py```






