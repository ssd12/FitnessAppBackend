import pymongo
import os
from pymongo import MongoClient

client = MongoClient('mongodb://mongodb:27017/')
dbName = "fitnessAppTestDB"
allDBs = client.list_database_names()

if dbName in allDBs:
        print("Database for fitness app exists.")
        db = client["fitnessAppTestDB"]
        collection = db["testCollection"]
else:
        db = client["fitnessAppTestDB"]
        collection = db["testCollection"]
        collection.insert_one({"info":"fitness app test db test collection info entry"})
        print("Created fitness app db.")

print("Finished setting up database")
print("Current databases: ", allDBs)
        
print("Connecting to DB")
print("MongoClient: ", client)
print("Database: ", db)
print("Current users: ", collection.find().distinct("userName"))

def getAllUsers():
	return collection.find() 	

def checkEmailExists(email):
	allEmails = collection.find().distinct("email")
	print("Current emails in use: ", allEmails)
	if (email in allEmails):
		return True
	else:
		return False

def checkUserPassword(username, password):
	user = getUser(username)
	print("Password sent by login: ", password)
	userPassword = user.distinct("userPassword")
	print(userPassword, " type: ", type(userPassword))
	if (password == userPassword[0]):
		print("Correct Password. User Logged In")
		return "loggedIn"
	else:
		print("Incorrect Password. Login error.")
		return "loginError"

def createUserDoc(username, password, email, securityQuestion, securityQuestionAnswer):
    newUserDoc = {"userName":username, "userPassword":password,"activities":[], "email":email, "securityQuestion":securityQuestion, "securityQuestionAnswer":securityQuestionAnswer}
    allUserNames = collection.find()
    if (username in allUserNames.distinct("userName")):
        print("User name already taken.")
    else:
        collection.insert_one(newUserDoc)
        print("User Added")

def deleteUserDoc(username):
    if (username in collection.find().distinct("userName")):
        userDocObject = getUser(username)
        nameCursor = userDocObject.distinct("userName")
        collection.remove({"userName":nameCursor[0]})
        if (username not in collection.find().distinct("userName")):
            print("User deleted")
            return "deleted"
    else:
        print("User does not exist")
        return "error"

def getUser(username):
    user = collection.find({"userName":username})
    if (user is not None):
        return user
    else:
        return None 

def addActivity(username,activityToAdd):
    user = getUser(username)
    if (user is not None):
        print("No. of current acitvities: ", len(user.distinct("activities")))
        collection.update_one({"userName":username} , {"$push" : {"activities":activityToAdd}})
        print("No. of current activities: ", len(user.distinct("activities")))
        print("Current activities: ", user.distinct("activities"))
        
def newActivity(activityID, activityType, distance, time):
    return {"activityID":activityID,"activityType":activityType,"distance":distance,"time":time}   

def removeActivity(activityID, username):
    user = getUser(username)
    if (user is not None):
        collection.update_one({"userName":username}, {"$pull": {  "activities":  {"activityID":activityID}}} )
        print("Activity removed")
        print("Current activities: ", user.distinct("activities"))

def getActivity(activityID, username):
	user = getUser(username)
	if (user is not None):
		activity = user.distinct("activities")
		print("activity", activity, type(activity[0]))

def printAllDocs():
    cursor = collection.find({})
    for doc in cursor:
        print(doc)
    print(collection.count())

def getAllUserNames():
	return collection.find().distinct("userName")

def changePassword(username, newPassword):
    user = getUser(username)
    if (user is not None):
        collection.update_one({"userName":username}, {"$set":{"userPassword":newPassword}} )
