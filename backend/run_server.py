import os
import sys

# Add the parent directory to the path so we can import the api package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.app import app

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5003)
