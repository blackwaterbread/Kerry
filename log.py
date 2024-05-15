from datetime import datetime

def printLog(message: str):
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    print(f'{timestamp} {message}')