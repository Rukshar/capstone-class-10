from src.jukebox.jukebox import JukeBox
from src.jukebox.config import *
from dotenv import load_dotenv

def create_jukebox():
    load_dotenv()

    env = os.environ.get('ENV')
    if env is None:
        raise ValueError('No environment specified')

    if env == 'prod':
        jukebox_config = ProdConfig
    elif env == 'test':
        jukebox_config = TestConfig
    elif env == 'dev':
        jukebox_config = DevConfig
    else:
        raise ValueError('Configuration not loaded')

    jukebox_instance = JukeBox(jukebox_config)

    return jukebox_instance
