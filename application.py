from flask import Flask, render_template, request, session
from datetime import datetime
import os
from flask_socketio import SocketIO
import pyinotify

SESSION_TYPE = 'filesystem'
application = Flask(__name__)

# application.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
# application.config['MYSQL_USER'] = os.environ['MYSQL_USERNAME']
# application.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
# application.config['MYSQL_DB'] = os.environ['MYSQL_DB']
application.secret_key = 'super secret key'
application.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(application)
# mysql = MySQL(application)

print(os.getenv("PORT"))
port = int(os.getenv("PORT", 5000))

thread = None


class ModHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, evt):
        socketio.emit('file updated')


def background_thread():
    handler = ModHandler()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, handler)
    wm.add_watch(session.get('static/test.txt', False), pyinotify.IN_CLOSE_WRITE)
    notifier.loop()

@socketio.on('connect')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)

@application.route('/')
def hello_world():
    request_received = datetime.now()
    res = 'a.jpg'
    if(session.get('toggle', False)):
        res = 'a.jpg'
        session['toggle'] = False
        f= open("static/test.txt","w+")
        f.write('False')
        f.close()
    else:
        res = 'b.jpg'
        session['toggle'] = True
        f= open("static/test.txt","w+")
        f.write('True')
        f.close()
    response_time = datetime.now()
    elapsed_time = response_time - request_received
    return render_template("index.html", result=res, request_received=request_received, response_time=response_time, elapsed_time=elapsed_time, async_mode=socketio.async_mode)

# @application.route('/earthquake', methods=['GET'])
# def get_earthquakes():
#     mag_from = request.args['magFrom'] if 'magFrom' in request.args else ''
#     mag_to = request.args['magTo'] if 'magTo' in request.args else ''
#     days = request.args['days'] if 'days' in request.args else ''
#     latitude = request.args['lat'] if 'lat' in request.args else ''
#     longitude = request.args['long'] if 'long' in request.args else ''
#     distance = request.args['distance'] if 'distance' in request.args else ''
#     CUR_cos_lat = ''
#     CUR_sin_lat = ''
#     CUR_cos_lng = ''
#     CUR_sin_lng = ''
#     cos_allowed_distance = ''
#     if latitude and longitude and distance:
#         # latitude = math.radians(float(latitude))
#         # longitude = math.radians(float(longitude))
#         CUR_cos_lat = math.cos(float(latitude) * math.pi / 180)
#         CUR_sin_lat = math.sin(float(latitude) * math.pi / 180)
#         CUR_cos_lng = math.cos(float(longitude) * math.pi / 180)
#         CUR_sin_lng = math.sin(float(longitude) * math.pi / 180)
#         cos_allowed_distance = math.cos(float(distance) / 6371) # This is in KM
#         print("CUR_cos_lat: " + str(CUR_cos_lat))
#         print("CUR_sin_lat: " + str(CUR_sin_lat))
#         print("CUR_cos_lng: " + str(CUR_cos_lng))
#         print("CUR_sin_lng: " + str(CUR_sin_lng))
#         print("cos_allowed_distance: " + str(cos_allowed_distance))
#     conn = get_connection()
#     cur = conn.cursor()
#     #cur.execute("SELECT time,latitude,longitude,depth,mag,rms,place FROM earthquake WHERE (%s = '' or %s = '' or mag BETWEEN %s AND %s) AND (%s = '' or time BETWEEN date('now', '-%s days') AND date('now')) AND (%s = '' OR %s * sin_lat + %s * cos_lat * (cos_long * %s + sin_long * %s) > %s)", (mag_from, mag_to, mag_from, mag_to, days, days,CUR_sin_lat, CUR_sin_lat, CUR_cos_lat, CUR_cos_lng, CUR_sin_lng, cos_allowed_distance))
#     cur.execute("SELECT * FROM earthquake WHERE (%s = '' or %s = '' or mag BETWEEN %s AND %s)", (mag_from, mag_to, mag_from, mag_to))
#     res = cur.fetchall()
#     return render_template('test.html', result=res, content_type='application/json')

# @application.route('/csv', methods=['POST'])
# def upload_csv():
#     file = request.files['csvFile']
#     target = os.path.join(APP_ROOT, 'static')
#     file.save(os.path.join(target, file.filename))
#     f = open(os.path.join(target, file.filename), "r")
#     print(f)
#     conn = get_connection()
#     cur = conn.cursor()
#     sql = "LOAD DATA LOCAL INFILE '"+ os.path.join('./static', file.filename) +"' INTO TABLE earthquake FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\r' IGNORE 1 LINES (time,latitude,longitude,depth,mag,rms,place)"
#     print(sql)
#     cur.execute(sql)
#     conn.commit()
#     cur.close()
#     res = get_initial_data()
#     print(res)
#     return render_template("uploaded.html", result=res)

# def get_initial_data():
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*), MAX(mag) from earthquake")
#     res = cur.fetchall()
#     print(res[0][1])
#     cur.execute("SELECT place from earthquake where mag = "+str(res[0][1]))
#     res2 = cur.fetchall()
#     cur.close()
#     return [res[0][0],res[0][1],res2[0][0]]

# def get_timezone_date(longitude, latitude, dt):
#     datetime_obj_naive = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
#     mytimezone = tf.timezone_at(lng=float(longitude), lat=float(latitude))
#     if not mytimezone:
#         return datetime_obj_naive.strftime(fmt)[:-3]
#     utcmoment = datetime_obj_naive.replace(tzinfo=pytz.utc)
#     localDatetime = utcmoment.astimezone(pytz.timezone(str(mytimezone)))
#     return localDatetime.strftime(fmt)[:-3]

# @application.route('/delete', methods=['GET'])
# def deleteall():
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("DELETE FROM earthquake")
#     conn.commit()
#     cur.close()
#     return "Successfully deleted all data"

# @application.route('/magrange', methods=['GET'])
# def mag_range():
#     mag_from = request.args['magFrom'] if 'magFrom' in request.args else ''
#     mag_to = request.args['magTo'] if 'magTo' in request.args else ''
#     if mag_from and mag_to:
#         mag_from = float(mag_from)
#         mag_to = float(mag_to)
#         my_range = numpy.arange(mag_from, mag_to, 0.1)
#         i = 0
#         res = []
#         conn = get_connection()
#         cur = conn.cursor()
#         while i < len(my_range):
#             if(i+1 >= len(my_range)):
#                 break
#             cur.execute("SELECT COUNT(*) FROM earthquake where mag between "+str(my_range[i])+" and "+str(my_range[i+1]))
#             myres = cur.fetchall()
#             res.append([myres[0][0], my_range[i], my_range[i+1]])
#             i = i + 1
#         return render_template("test2.html", result=res)
#     return ""

# @application.route('/deleteme', methods=['GET'])
# def dele():
#     mag_from = request.args['magFrom'] if 'magFrom' in request.args else ''
#     mag_to = request.args['magTo'] if 'magTo' in request.args else ''
#     mydate = request.args['date'] if 'date' in request.args else ''
#     mydate = dateutil.parser.parse(mydate).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
#     print(mydate)
#     conn = get_connection()
#     cur = conn.cursor()
#     res2 = cur.execute("SELECT * FROM earthquake")
#     cur.execute("DELETE FROM earthquake where time = %s and mag between %s and %s", (mydate, mag_from, mag_to))
#     cur.execute("SELECT ROW_COUNT()")
#     res = cur.fetchall()
#     return render_template("test3.html", result=res)

if __name__ == '__main__':
    # application.run(host='0.0.0.0', port=port, debug=True)
    # sess.init_app(application)
    session.init_app(application)
    socketio.run(application, debug=True)
