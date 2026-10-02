class ProfessionalUser(Base):
    __tablename__ = "professional_users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    license_id = Column(String, nullable=True)
    role = Column(String, default="therapist")  # or "career_coach"


class ConsentLink(Base):
    __tablename__ = "consent_links"
    id = Column(Integer, primary_key=True)
    client_user_id = Column(String)
    professional_id = Column(Integer)
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)


class PhysiologicalLog(Base):
    __tablename__ = "physiological_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    stress_level = Column(String)
    stress_score = Column(Integer)
    heart_rate_bpm = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)