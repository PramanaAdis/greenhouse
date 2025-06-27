import firebase_admin
from firebase_admin import credentials
from firebase_admin import db  

class FirebaseConnector:
    def __init__(self, cred_path, database_url):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
        self.db = db  

    def get_data(self, path):
        ref = self.db.reference(path)
        return ref.get()
