from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "all test cases passed! Ready to deploy in production and port also updated in the script for container"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
