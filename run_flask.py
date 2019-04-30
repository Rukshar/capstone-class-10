from src.flaskapp import create_app
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()

    flaskapp_args = {"debug": False, "host": "0.0.0.0", "port": 5000}
    app = create_app()
    app.run(**flaskapp_args)
