from flask import Flask, render_template, Response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('live.html')
