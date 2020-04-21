import serial
ser = serial.Serial('/dev/ttyUSB0')  # open serial port
pm25 = None
from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def index():
    pm25=readdata()
    templateData = { 'pm25' : pm25}
    return render_template('index.html',**templateData)


def readdata():
    chunk = ser.read_until(b'\xab\xaa')
    pm25 = chunk[1]
    print(chunk)
    print(pm25)
    return pm25

if __name__ == '__main__':       
    app.run(host='0.0.0.0',port=8080)

