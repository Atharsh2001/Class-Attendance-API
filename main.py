from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from datetime import datetime
from operator import itemgetter

Myapp = Flask(__name__)
Myapp.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'


db = SQLAlchemy(Myapp)
class Student(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    roll = db.Column(db.String(20),unique=True,nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_roll = db.Column(db.Integer,db.ForeignKey('student.roll'),nullable=False)
    Date = db.Column(db.String(20),nullable=False)
    attendance_value = db.Column(db.String(20))


@Myapp.route('/login',methods=['POST'])
def login():
    if request.method=='POST':
        Ad_name = request.form['login']
        Ad_pass = str(request.form['pass'])
        if Ad_name == 'admin' and Ad_pass == '1234':
            return jsonify({"message":"Welcome"}),200
        else:
            return jsonify({"message":"Incorrect credentials"}),401

@Myapp.route('/students',methods=['GET'])
def students():
    if request.method=='GET':
        u1 = Student.query.all()
        if len(u1)>0:
            _ = []
            for i in u1:
                st = Attendance.query.filter_by(user_roll=i.roll).all()
                temp=0
                temp1=0
                for j in st:
                    if j.attendance_value == 'Present':
                        temp+=1
                    elif j.attendance_value == 'Absent':
                        temp1+=1
                _.append({'name':i.name,'roll':i.roll,'No of Days Present':temp,'No of Days Absent':temp1})
                newlist = sorted(_, key=itemgetter('roll')) 
            return jsonify(newlist),200
        else:
            return jsonify({"message":"No Records found"}),400

@Myapp.route('/students/add',methods=['POST'])
def student_add():
    if request.method=='POST':
        new_stu = request.get_json()
        u1 = Student(name=new_stu['name'],roll=new_stu['roll'])
        try:
            db.session.add(u1)
            db.session.commit()
            return jsonify({"message":"Student Added"}),200
        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({"message":"Roll no already exists"}),400



@Myapp.route('/students/delete/<string:id>',methods=['DELETE'])
def student_delete(id):
    if request.method=='DELETE':
        temp_roll = []
        temp = Student.query.all()
        for i in temp:
            temp_roll.append(i.roll)
        print(temp_roll)
        if id in temp_roll:
            Student.query.filter_by(roll=id).delete()
            Attendance.query.filter_by(user_roll=id).delete()
            db.session.commit()
            return 'Student Deleted',200
        else:
            return "Roll Does not exists",400

@Myapp.route('/students/attendance',methods=['POST'])
def student_attendance():
    if request.method=='POST':
        attendance = request.get_json()
        date = datetime.now().strftime("%d-%m-%Y")
        old_atten = Attendance.query.filter_by(Date=date)
        temp_atten=[]
        message = []
        for j in old_atten:
            if j.Date==date:
                temp_atten.append(str(j.user_roll))
        print(temp_atten)
        t=0
        for i in attendance:
            if i['roll'] not in temp_atten:
                u2 = Attendance(user_roll=i['roll'],Date=date,attendance_value=i['value'])
                db.session.add(u2)
                db.session.commit()
                t+=1
            else:
                message.append(f"Attendance already present for {i['roll']} on this Date")

        if t>=1:
            message.append("For remaining students attendance added")
        return jsonify(message),200


        

@Myapp.route('/students/<int:rol>',methods=['GET'])
def student_info(rol):
    if request.method=='GET':
        details = Attendance.query.all()
        temp_atten = []
        for j in details:
            if j.user_roll == rol:
                temp_atten.append({'Date':j.Date,'Attendance':j.attendance_value})
        if len(temp_atten)>0:
            return jsonify(temp_atten),200
        else:
            return jsonify({"message":"No Records found"}),400




if __name__ == '__main__':
    Myapp.run(debug=True)