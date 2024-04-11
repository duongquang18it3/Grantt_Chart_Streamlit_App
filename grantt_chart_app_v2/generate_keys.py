import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Admin", "Manager", "Employee1", "Employee2"]
username = ["admin", "manager", "employee1", "employee2"]
password = ["xxx", "xxx", "xxx", "xxx", "xxx"]

hashed_passwords = stauth.Hasher(password).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)