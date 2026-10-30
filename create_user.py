from pymongo import MongoClient
import bcrypt

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.moviesDB     
users = db.users        

user_list = [
          { 
            "name" : "Meredith Grey",
            "username" : "meredith",  
            "password" : b"meredith_g",
            "email" : "meredith@greysloan.com",
            "admin" : False
          },
          { 
            "name" : "Derek Sheppered",
            "username" : "derek",  
            "password" : b"derek_s",
            "email" : "derek@greysloan.com",
            "admin" : False
          },
          { 
            "name" : "Lexi Grey",
            "username" : "lexi",  
            "password" : b"lexi_g",
            "email" : "lexi@greysloan.com",
            "admin" : False
          },        
          { 
            "name" : "Mark Sloan",
            "username" : "mark",  
            "password" : b"mark_s",
            "email" : "mark@greysloan.com",
            "admin" : True
          },
          { 
            "name" : "Cristina Yang",
            "username" : "cristina",  
            "password" : b"cristina_y",
            "email" : "cristina@greysloan.com",
            "admin" : False
          }
       ]

for new_user in user_list:
      new_user["password"] = bcrypt.hashpw(new_user["password"], bcrypt.gensalt())
      users.insert_one(new_user)
