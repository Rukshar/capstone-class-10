from src.jukebox import create_jukebox
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    jukebox = create_jukebox()
    jukebox.start_jukebox()
