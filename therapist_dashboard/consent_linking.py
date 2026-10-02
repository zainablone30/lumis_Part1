import sqlite3
import time


class ConsentLinker:
    def __init__(self, db_path="lumis.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def grant_consent(self, client_user_id, professional_id):
        self.conn.execute(
            "INSERT INTO consent_links (client_user_id, professional_id, consent_given, consent_date, revoked) "
            "VALUES (?,?,1,?,0)", (client_user_id, professional_id, time.time())
        )
        self.conn.commit()

    def revoke_consent(self, client_user_id, professional_id):
        self.conn.execute(
            "UPDATE consent_links SET revoked=1 WHERE client_user_id=? AND professional_id=?",
            (client_user_id, professional_id)
        )
        self.conn.commit()

    def get_consented_clients(self, professional_id):
        rows = self.conn.execute(
            "SELECT DISTINCT client_user_id FROM consent_links "
            "WHERE professional_id=? AND consent_given=1 AND revoked=0",
            (professional_id,)
        ).fetchall()
        return [r[0] for r in rows]

    def has_consent(self, client_user_id, professional_id) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM consent_links WHERE client_user_id=? AND professional_id=? "
            "AND consent_given=1 AND revoked=0", (client_user_id, professional_id)
        ).fetchone()
        return row is not None