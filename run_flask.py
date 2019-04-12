from src.flaskapp.app import app

if __name__ == '__main__':
    flaskapp_args = {"debug": False,"host": "0.0.0.0","port": 5000}
    app.run(**flaskapp_args)