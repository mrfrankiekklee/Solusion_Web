from flask import Flask, flash, redirect, render_template,request, url_for, session, send_from_directory
import pymysql
import sshtunnel
import mysql.connector
import requests 
import random
import json
import os
# Import create_engine function
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pathlib import Path


# Create an engine to the census database
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI']='mysql://mrfrankiekklee:ZXcv1199**@mrfrankiekklee.mysql.pythonanywhere-services.com/mrfrankiekklee$Solusion'
#db=SQLAlchemy(app)
UPLOAD_FOLDER = './json/'
ALLOWED_EXTENSIONS = set(['json'])
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposetobesecret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 15.0

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"




## 0 = login fetchone 
## 1 = insert
## 2 = SELECT fetchall

def connect(number,sql):

    with sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
            ssh_username='mrfrankiekklee', ssh_password='ZXcv1199**',
            remote_bind_address=('mrfrankiekklee.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            connection = mysql.connector.connect(
            user='mrfrankiekklee', password='ZXcv1199**',
            host='127.0.0.1', port=tunnel.local_bind_port,
            database='mrfrankiekklee$default',
        )
            
            
                
            if number==0:
                cursor = connection.cursor()
                cursor.execute(sql) 
                query = cursor.fetchone()
                print(query)
                return query
            elif number==1:
                cursor = connection.cursor()
                cursor.execute(sql) 
                connection.commit()
            elif number==2:     
                cursor = connection.cursor(dictionary=True)
                cursor.execute(sql) 
                query = cursor.fetchall()
                        

                print(query)
                return query


@app.route("/",methods=['GET','POST'])
@app.route("/login",methods=['GET','POST'])
def login():
    
        
        if request.method=='POST':
            email = request.form["email"]
            password = request.form["password"]

            x = "SELECT*FROM Account WHERE email='"+email+"'"
            result = connect(0,x)
            if result is not None:
                if len(result)==4:
                    for x in result:
                        print(x)
                    if check_password_hash(result[2], password):
                        session['user-id']=result[0]
                        
                        session['logged_in'] = True
                        return redirect(url_for("classroom"))
                    else: 
                        flash("Wrong email address or Password")
                        return redirect(url_for("login"))
            else:
                flash("The system doesn't have your account")
                return redirect(url_for("login"))


        else:
            return render_template('index.html')

 


 
@app.route("/classroom",methods=['GET','POST'])
def classroom():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    
        classrooms = "SELECT * FROM Classroom WHERE `user-id` = " +str(session['user-id'])
        result = connect(classrooms)
        
    if request.method=='POST':
        classroomName = request.form["classroomName"]
        classroomNotes = request.form["classroomNotes"]
        year = request.form["year"]
   

        x = "INSERT INTO Classroom (classroomName,classroomNotes,`user-id`,Year) VALUES('"+str(classroomName)+"','"+str(classroomNotes)+"',"+str(session['user-id'])+","+str(year)+")"
        
        connect(1,x)
        flash(" Classroom created successfully")
        return redirect(url_for("classroom"))
        

    else:
        classrooms = "SELECT * FROM Classroom WHERE `user-id` = " +str(session['user-id'])
        result = connect(2,classrooms)
       
       
        return render_template('createClassroom.html', classrooms = result)
    
    
@app.route("/deleteClassroom/<classroomid>", methods=['GET','POST'])
def deleteClassroom(classroomid):
    
#    checkuserid = "SELECT `user-id` FROM CLassroom WHERE classroomID ="+classroomid 
#    result = connect(0,checkuserid)
#    print (result) 
    
    if not session.get('logged_in'):
        return redirect(url_for("login"))
            
    
    else:
        print(classroomid)

        x = "DELETE FROM Classroom WHERE classroomID="+classroomid
        connect(1,x)


        return redirect(url_for("classroom"))
    
    
    
@app.route("/experiments/<classroomid>", methods=['GET','POST'])
def experiments(classroomid):
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    
    if request.method=="POST":
        experimentName = request.form["experimentName"]
        experimentNotes = request.form["experimentNote"]
        verification_code = generate_code();
        
        
        mixA = request.form["mElementA"]
        mixAType= request.form["mElementAType"]
        mixB = request.form["mElementB"]
        mixBType =request.form["mElementBType"]
        mixR = request.form["mReaction"]
        mixRevR = request.form["mReverseReaction"]

        
        mic1 = request.form["sElement"]
        mic2 = request.form["sElement1"]
        mic3 = request.form["sElement2"]
        mic4 = request.form["sElement3"]
        mic5 = request.form["sElement4"]
        mic6 = request.form["sElement5"]
        mic7 = request.form["sElement6"]

        
        heat1 = request.form["hElement"]
        heatT = request.form["hType"]
        heatL = request.form["hTime"]
        heatR = request.form["hReaction"]
        
     
        data ={  
        'experimentNote' : experimentNotes,
        'mixElementA' : mixA,
        'mixElementAType' : mixAType,
        'mixElementB': mixB,
        'mixElementBType' : mixBType,
        'mixElementReaction' : mixR,
        'mixReverseReaction' : mixRevR,
            
        'microscope1' : mic1,
        'microscope2' : mic2,
        'microscope3' : mic3,
        'microscope4' : mic4,
        'microscope5' : mic5,
        'microscope6' : mic6,
        'microscope7' : mic7,
            
        'heatElement1' : heat1,
        'heatElementType' : heatT,
        'heatLevel' : heatL,
        'heatReaction' : heatR
        }
        
        json_str = json.dumps(data)
    
        
        print(json_str)
        print("Passed JSON")
        with open("./json/" + verification_code+'.json','w') as outfile:
            json.dump(data, outfile)
            
       # outfile.save(os.path.join(app.config['UPLOAD_FOLDER'],outfile.filename))
            
        
        
        
        
        
        x = "INSERT INTO Experiment (experimentName,experimentNotes,verificationCode,classroomID,json) VALUES('"+str(experimentName)+"','"+str(experimentNotes)+"','"+verification_code+"',"+classroomid+",'"+json_str+"')"
        
        
        connect(1,x)
        flash(" Experiment created successfully")
        return redirect(url_for('experiments', classroomid = classroomid))

       
    
    else:
        experiments = "SELECT * FROM Experiment WHERE classroomID="+classroomid
        result = connect(2,experiments)
        return render_template('createExperiment.html', experiments = result, classroomid = classroomid)
    

def generate_code():
    
    alphabetnletter = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    code_length = 10
    vC = ""
    
    for i in range(code_length):
        next_code = random.randrange(len(alphabetnletter))
        vC = vC + alphabetnletter[next_code]
    
    return vC

@app.route("/deleteExperiment/<experimentid>/<classroomid>",methods=['GET','POST'])
def deleteExperiment(experimentid,classroomid):
    if not session.get('logged_in'):
        return redirect(url_for("login"))
   
    else:
        print(experimentid)

        x = "DELETE FROM Experiment WHERE `experimentID`="+experimentid
        connect(1,x)


        return redirect(url_for('experiments', classroomid = classroomid))
@app.route("/checkVerificationCode/<verificationCode>", methods=['GET','POST']) 
def checkVerificationCode(verificationCode):
    if request.method=='GET':
        print(verificationCode)
        json_dir=Path("./json/")
        
        file_name =verificationCode+".json"
        file_list = os.listdir(json_dir)
        if file_name in file_list:
            print("Yes file is here")
            return send_from_directory(directory=json_dir, filename=file_name)
        else:
            print("nope not here")
        
        
    return verificationCode
   
            

    


@app.route("/members/<string:name>/")
def getMember(name):
    return name

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    print("You logged out")
    return redirect(url_for('login'))
 
if __name__ == "__main__":
    app.run()
    