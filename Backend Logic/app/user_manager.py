import json
import hashlib
from datetime import datetime


class UserManager:
    def __init__(self, users_file_path):
        self.users_file_path = users_file_path

    def _read_users(self):
        try:
            with open(self.users_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _write_users(self, data):
        with open(self.users_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email, password, firstname, educational_level):
        users = self._read_users()

        if email in users:
            return False, "Email already exists"

        users[email] = {
            "firstname": firstname,
            "password": self._hash_password(password),
            "educational_level": educational_level,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self._write_users(users)
        return True, "User created successfully"

    def verify_user(self, email, password):
        users = self._read_users()

        if email not in users:
            return False, "User not found"

        if users[email]["password"] != self._hash_password(password):
            return False, "Invalid password"

        return True, {
            "firstname": users[email]["firstname"],
            "email": email,
            "educational_level": users[email]["educational_level"]
        }

    def get_user(self, email):
        users = self._read_users()
        user = users.get(email)
        if user:
            return {
                "firstname": user["firstname"],
                "email": email,
                "educational_level": user["educational_level"]
            }
        return None

    def update_user(self, email, firstname, educational_level):
        users = self._read_users()

        if email not in users:
            return False, "User not found"

        users[email]["firstname"] = firstname
        users[email]["educational_level"] = educational_level
        
        self._write_users(users)

        # return the user data
        return {
            "firstname": firstname,
            "email": email,
            "educational_level": educational_level
        }

