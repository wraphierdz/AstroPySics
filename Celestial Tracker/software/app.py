from flask import Flask, request, render_template
from skyfield.api import Topos, load
# from utils import degDecimal, celesCoor, vectorFrom, vec_eq, HA, eq_altz
from services import calculate

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def compute():
    result = calculate() 
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
    