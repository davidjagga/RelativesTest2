import pyrebase

#-------------------------------------------------------------------------------
# Variables & Setup



config = {
  "apiKey": "AIzaSyDCe_5uQYZrSH87RQ9kp9pfJgG8PA8IHsk",
  "authDomain": "relatives-test.firebaseapp.com",
  "databaseURL": "https://relatives-test-default-rtdb.firebaseio.com",
  "projectId": "relatives-test",
  "storageBucket": "relatives-test.appspot.com",
  "messagingSenderId": "1063389234635",
  "appId": "1:1063389234635:web:5c4a04ce56ced7af2f624e"
}


firebase_storage = pyrebase.initialize_app(config)
storage = firebase_storage.storage()

#-------------------------------------------------------------------------------
# Uploading And Downloading Images
def pushFile(filename, location='l'):
    storage.child(filename).put('static/files/mountains.png')

