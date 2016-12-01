from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey, Table
from database import Base, db_session, engine
from sqlalchemy.orm import mapper

class Voter(Base):
    __tablename__ = 'voters'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    voter_id = Column(Integer, nullable=False, unique=True)
    __table_args__ = (UniqueConstraint('name', 'voter_id', name='uix_1'),)

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    voter = Column(String(512), ForeignKey(Voter.voter_id), nullable=False, unique=True)




def initialize_election():
    #need to blow away the votes table for each election
    #this is because columns change with number of candidates
    try:
        Vote.__table__.drop(bind=engine)
    except:
        pass
    


    Candidate.query.delete()
    #construct tables for a specific election
    #candidate list could be loaded from something if need be
    running_candidates = ["John Smith", "Bob Parker", "Mike McClay"]

    #add the candidates to the table
    for rc in running_candidates:
        c = Candidate()
        c.name = rc
        db_session.add(c)
    db_session.commit()

    for i,c in enumerate(running_candidates):
        setattr(Vote, "vote%d"%i, Column(String(512), unique=False))

    Vote.__table__.create(bind=engine)

initialize_election()
