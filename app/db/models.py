from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base  
from datetime import datetime, timezone

Base = declarative_base()  

class PullRequest(Base):
    __tablename__ = "pull_requests"  

    id                = Column(Integer, primary_key=True)  
    repo_full_name    = Column(String)   
    pr_number         = Column(Integer)  
    pr_title          = Column(String)
    pr_url            = Column(String)
    head_sha          = Column(String)   
    risk_score        = Column(Float)    
    risk_label        = Column(String)   
    complexity_signal = Column(Float)    
    fanout_signal     = Column(Float)
    lines_signal      = Column(Float)
    files_analyzed    = Column(Integer)
    created_at        = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FileAnalysis(Base):
    __tablename__ = "file_analyses"

    id                    = Column(Integer, primary_key=True)
    pull_request_id       = Column(Integer, ForeignKey("pull_requests.id"))  # links to parent PR
    filename              = Column(String)
    cyclomatic_complexity = Column(Float)
    max_function_depth    = Column(Integer)
    lines_changed         = Column(Integer)
    dependent_count       = Column(Integer)
    created_at            = Column(DateTime, default=lambda: datetime.now(timezone.utc))