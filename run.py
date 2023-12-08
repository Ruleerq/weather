from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def display_gif():
    return send_file('animation.gif', mimetype='image/gif')

if __name__ == '__main__':
    app.run(debug=True)
