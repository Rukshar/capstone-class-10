from src.jukebox import create_jukebox
from dotenv import load_dotenv
import time

load_dotenv()

if __name__ == '__main__':
    time.sleep(20)
    jukebox = create_jukebox()
    jukebox.start_jukebox()
