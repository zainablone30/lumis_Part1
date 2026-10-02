from passlib.context import CryptContext
import sqlite3

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ProfessionalAuth:
    def __init__(self, db_path="lumis.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def register(self, name, email, password, license_id="", role="therapist"):
        hashed = pwd_context.hash(password)
        self.conn.execute(
            "INSERT INTO professional_users (name, email, hashed_password, license_id, role) "
            "VALUES (?,?,?,?,?)", (name, email, hashed, license_id, role)
        )
        self.conn.commit()

    def login(self, email, password):
        row = self.conn.execute(
            "SELECT id, name, hashed_password, role FROM professional_users WHERE email=?",
            (email,)
        ).fetchone()
        if row and pwd_context.verify(password, row[2]):
            return {"id": row[0], "name": row[1], "role": row[3]}
        return None