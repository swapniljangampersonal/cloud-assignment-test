from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import os, csv, sqlite3

application = Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(application)
inmemory = sqlite3.connect(':memory:')

class Fall(db.Model):
    __tablename__ = 'fall'
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.Integer)
    section = db.Column(db.Integer)
    days = db.Column(db.String(20))
    start_time = db.Column(db.TIMESTAMP)
    end_time = db.Column(db.TIMESTAMP)
    instructor = db.Column(db.String(20))
    max_students = db.Column(db.Integer)

    def __init__(self, course, section,days,start_time,end_time,instructor,max_students):
        self.course = course
        self.section = section
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.instructor = instructor
        self.max_students = max_students

    def __repr__(self):
        return '<Course %r>' % self.course

class Mapping(db.Model):
    __tablename__ = 'mapping'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(20))
    course = db.Column(db.Integer)
    section = db.Column(db.Integer)

    def __init__(self, fname, lname, course, section):
        self.fname = fname
        self.lname = lname
        self.course = course
        self.section = section


port = int(os.getenv("PORT", 5000))

@application.route('/')
def myindex():
    courses = Fall.query.all()
    return render_template("index.html", result=courses)

@application.route('/enrollme')
def hello():
    fname = request.args['fname']
    lname = request.args['lname']
    inmemory = sqlite3.connect(':memory:')
    cur = inmemory.cursor()
    cur.execute("create table if not exists students (idnum INT PRIMARY KEY, fname varchar(20), lname varchar(20), age int, credit int);")
    inmemory.commit()
    cur.execute("SELECT COUNT(*) FROM students")
    res = cur.fetchone()
    if res[0] == 0:
        with open('static/students.csv','r') as fin: 
            dr = csv.DictReader(fin)
            to_db = [(i['IdNum'], i['Fname'], i['Lname'], i['Age'], i['Credit']) for i in dr]
        cur.executemany("INSERT INTO students (IdNum,Fname,Lname,Age,Credit) VALUES (?, ?, ?, ?, ?);", to_db)
        inmemory.commit()
    cur = inmemory.cursor()
    cur.execute("Select count(*) from students where Fname = ? and Lname = ?",(fname,lname))
    checkstu = cur.fetchone()
    if checkstu[0] == 0:
        return "Please enter valid student name"
    class_one = int(request.args['class_one'])
    class_two = int(request.args['class_two'])
    class_three = int(request.args['class_three'])
    res1 = ''
    res2 = ''
    res3 = ''
    course_one = Fall.query.filter_by(id=class_one).with_for_update().one()
    if course_one.max_students >= 1:
        course_one.max_students = course_one.max_students - 1
        db.session.commit()
        new_mapping = Mapping(fname, lname, course_one.course, course_one.section)
        db.session.add(new_mapping)
        db.session.commit()
        res1 = "Registered : " + course_one.instructor +" "+ str(course_one.section) +" "+ str(course_one.course)
    else:
        res1 = "Not registered : " + course_one.instructor +" "+ str(course_one.section) +" "+ str(course_one.course)

    course_two = Fall.query.filter_by(id=class_two).with_for_update().one()
    if course_two.max_students >= 1:
        course_two.max_students = course_two.max_students - 1
        db.session.commit()
        new_mapping = Mapping(fname, lname, course_two.course, course_two.section)
        db.session.add(new_mapping)
        db.session.commit()
        res2 = "Registered : " + course_two.instructor +" "+ str(course_two.section) +" "+ str(course_two.course)
    else:
        res2 = "Not registered : " + course_two.instructor +" "+ str(course_two.section) +" "+ str(course_two.course)

    course_three = Fall.query.filter_by(id=class_two).with_for_update().one()
    if course_three.max_students >= 1:
        course_three.max_students = course_three.max_students - 1
        db.session.commit()
        new_mapping = Mapping(fname, lname, course_three.course, course_three.section)
        db.session.add(new_mapping)
        db.session.commit()
        res3 = "Registered : " + course_three.instructor +" "+ str(course_three.section) +" "+ str(course_three.course)
    else:
        res3 = "Not registered : " + course_three.instructor +" "+ str(course_three.section) +" "+ str(course_three.course)
    return "<center><h1>"+res1+"<br>"+res2+"<br>"+res3+"</h1></center>"

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=port, debug=True)
