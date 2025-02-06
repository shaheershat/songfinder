import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SPOTIPY_CLIENT_ID = os.getenv('135b52048f4c4ce4801c9be8346fe9e1')
    SPOTIPY_CLIENT_SECRET = os.getenv('a51270e0529646cca51f9ab1d3cc28cf')
