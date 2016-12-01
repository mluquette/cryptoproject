from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey, Table, Boolean
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

class TVote(Base):
    __tablename__ = 'tentative_votes'
    id = Column(Integer, primary_key=True)
    voter = Column(String(512), ForeignKey(Voter.voter_id), nullable=False, unique=True)
    correct = Column(Integer, default=0)
    failed = Column(Boolean, default=False)


NUM_CANDIDATES = None

def initialize_election():
    #need to blow away the votes table for each election
    #this is because columns change with number of candidates
    try:
        Vote.__table__.drop(bind=engine)
        TVote.__table__.drop(bind=engine)
    except:
        pass
    


    Candidate.query.delete()
    #construct tables for a specific election
    with open("candidates.txt","r") as f:
        running_candidates = f.read().split("\n")    
    global NUM_CANDIDATES
    NUM_CANDIDATES = len(running_candidates)
    #add the candidates to the table
    for rc in running_candidates:
        c = Candidate()
        c.name = rc
        db_session.add(c)
    db_session.commit()

    for i,c in enumerate(running_candidates):
        setattr(Vote, "vote%d"%i, Column(String(512), unique=False))
        setattr(TVote, "vote%d"%i, Column(String(512), unique=False))
        setattr(TVote, "u%d"%i, Column(String(512), unique=False))
        setattr(TVote, "e%d"%i, Column(Integer, unique=False))

    Vote.__table__.create(bind=engine)
    TVote.__table__.create(bind=engine)

initialize_election()
