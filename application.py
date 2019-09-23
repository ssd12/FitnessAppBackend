from flask import Flask, jsonify, abort, request
from flask_pymongo import PyMongo
from bson.json_util import *
import DatabaseUtilities as dbUtil
from flask_mail import Mail, Message
import json, os
import datetime

application = Flask(__name__)
currentLoggedInUsers = list()

mail_settings = {"MAIL_SERVER" : "smtp.gmail.com",
"MAIL_PORT"  : 465,
"MAIL_USE_SSL" : True,
"MAIL_USERNAME" : "",
"MAIL_PASSWORD" :""}

application.config.update(mail_settings)
mail = Mail(application)

if __name__ == "__main__":
    application.run(host='0.0.0.0')

@application.route('/')
@application.route('/index')
def main():
    header = 'This is a flask app running on a docker container on an aws ec2 instance at ' + str(datetime.datetime.now())
    return header

#create message to response to client
def createMessage(messageType, messageBody):
    response = dict()
    response['type'] = messageType
    response['body'] = messageBody
    return response

#returns all users
@application.route('/users', methods=['GET'])
def getAllUsers():
    currentUsers = dbUtil.getAllUsers()
    for user in currentUsers:
       print("Printing user below: ")
       print(user)
    return "Current Users: "

@application.route('/login', methods=['POST'])
def userLogin():
    requestJSON = request.get_json()
    username = requestJSON["username"]
    password = requestJSON["password"]
    allUsers = dbUtil.getAllUserNames()
    print("All users: ", allUsers, " type: ", type(allUsers))
    print("User exists: ", (username in allUsers))
    if (username in allUsers):
        print("user: ", username, "exits")
	print("Checking user password")
	loginResult = dbUtil.checkUserPassword(username, password) 
	if (loginResult is "loggedIn"):
	    currentLoggedInUsers.append(username)
	    print("Current logged in users", currentLoggedInUsers)
            response = createMessage("loginSuccessful", "User login successful.")
            return response
        else:
            response = createMessage("loginError", "Incorrect password")
            return response
    else:
	print("User", username," doesn't exist")
        response = createMessage("loginError", "Username does not exist")
	return response

@application.route('/logout', methods=['POST'])
def userLogout():
    requestJSON = request.get_json()
    username = requestJSON["username"]
    print("Request to logout user: ", username)
    if (username in currentLoggedInUsers):
        currentLoggedInUsers.remove(username)
	print("Current logged in users", currentLoggedInUsers)
        response = createMessage("logoutSuccessful", "User logged out")
        return response
    else:
        response = createMessage("error","Error logging user out. User not logged in.")
        return response


@application.route('/getUserActivities', methods=['POST'])
def getUserActivities():
    print("Getting activities")
    requestJSON = request.get_json()
    username = requestJSON["username"]
    print("Getting activities for username: ", username)
    user = dbUtil.getUser(username)
    allActivities = list(user.distinct("activities"))
    allActivitiesDict = dict()
    allActivitiesDict['username'] = username
    allActivitiesDict['allActivities'] = allActivities
    print("allActivities: ", allActivities)
    response = createMessage("userActivitiesFetched", allActivitiesDict)
    return response

@application.route('/addUserActivity', methods=['PUT'])
def addUserActivity():
    print("addUserActivity")
    json = request.get_json()
    print("Request json: ", json, "type: ", type(json))
    parseJSONtoAddActivity(json)
    response = createMessage("activityAdded", "User activity added")
    print(' /addUserActivity: ', response)
    return response

def parseJSONtoAddActivity(json):
    activityToAdd = dbUtil.newActivity(json["activityID"], json["activityType"], json["distance"], json["time"])
    dbUtil.addActivity(json["username"], activityToAdd)
    print("Added activity")

#removes a specific user activity
@application.route('/removeUserActivity', methods=['DELETE'])
def removeUserActivity():
    json = request.get_json()
    print("remove user activity json received: ", json)
    dbUtil.removeActivity(json['activityID'], json['username'])
    response = createMessage("activityDeleted", "activity successfully deleted")
    return response

@application.route('/createNewUser', methods=['PUT'])
def addNewUser():
    json = request.get_json()
    username = json["username"]
    password = json["password"]
    email = json["email"]
    securityQuestion = json["securityQuestion"]
    securityQuestionAnswer = json["securityQuestionAnswer"]
    invalidUserCredentials = checkUserCredentials(json)
    if (len(invalidUserCredentials['invalidCredentials']) is 0):
	dbUtil.createUserDoc(username, password, email, securityQuestion, securityQuestionAnswer)
        response = createMessage("registrationSuccessful", "User Successfully registered.")
	return response
    else: 
	print("Failure. Unable to add user due to: ", invalidUserCredentials['invalidCredentials'][0])
	print("All Invalid credentials", invalidUserCredentials['invalidCredentials'])
        allInvalidCreds = invalidUserCredentials['invalidCredentials']
        invalidCredDescription = " ".join(str(x) for x in allInvalidCreds)
        response = createMessage("registrationError", invalidCredDescription)
	return response

def checkUserCredentials(requestJSON):
    print("Checking user credentials")
    username = requestJSON["username"]
    email = requestJSON["email"]
    invalidCreds = dict()
    invalidCreds['invalidCredentials'] = []
    allUsers = dbUtil.getAllUserNames()
    if (username in allUsers):
	invalidCreds['invalidCredentials'].append('Username Taken')
    elif (dbUtil.checkEmailExists(email)):
        invalidCreds['invalidCredentials'].append('Email Taken')
    elif (checkEmailInValid(email)):
        invalidCreds['invalidCredentials'].append('Invalid Email')
    return invalidCreds

def checkEmailInValid(email):
    mailResponse = sendUserEmail(email)
    print("Email invalid: ", mailResponse)
    if (mailResponse is "sent"):
	return False
    else: 
	return True

@application.route('/deleteUser', methods=['DELETE'])
def deleteUser():
    json = request.get_json()
    print("request json: ", json)
    currentLoggedInUsers.remove(json["username"])
    deletionResult = dbUtil.deleteUserDoc(json["username"])
    return deletionResult

def sendUserEmail(email):
    try:
	print("Sending mail to: ", email)
	msg = Message("Sending sample mail", sender="afitnessapp@gmail.com", recipients=[email])
	msg.body = "Sending sample mail to newly registered user"
	mail.send(msg)
	print("mail sent")
	return "sent"
    except Exception, e:
	print("mail not sent:", str(e))
	return(str(e))

