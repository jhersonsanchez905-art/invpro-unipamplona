import psycopg2
from decouple import config

try:
    params = dict(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT')
    )
    print(f"Connection params: {params}")
    conn = psycopg2.connect(**params)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Error type: {type(e)}")
    try:
        print(f"Error message: {e}")
    except UnicodeDecodeError:
        print("Caught UnicodeDecodeError during printing of error.")
        # This usually happens when the error message from psycopg2 has bad bytes.
        # But wait, 'e' is an exception object.
        pass
    
    # Try to connect with a different approach to see if we can get the raw error
    import traceback
    traceback.print_exc()
