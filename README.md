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

## Secrets 

Copy your .secrets file to the `FlaskApp/` folder.


## Music directory

Create a `music/` directory in the project root folder:

```mkdir music```

Place several `.mp3` or `.m4a` files in this folder. Make sure the songs have metadata available related to:
- Song
- Artist
- Filename
- Duration

## Launching the app

You can launch the app with Docker inside of a container, or with  your local Python.
### With Docker

First we have to build the docker image. From root, run:

```docker build -t capstone:latest .```

In order to be able to access the Flask app from our localhost, we have to run the docker image and map the ports accordingly:

```docker run -p 5000:5000 capstone:latest```

### With Python

From root, simply run:

```python run.py```

### Access the Flask app

After launching, the Flask app is available at: `localhost:5000`






