from app.database.database import Base
from sqlalchemy import String, Integer, ForeignKey, Column, DateTime, Table,Boolean
from sqlalchemy.orm import relationship
import datetime



post_and_tag=Table(
    "posts_tags",
    Base.metadata,
    Column("post_id", ForeignKey("articles.id"), primary_key=True),
    Column("tags_id", ForeignKey("tags.id"), primary_key=True)

)




class Article(Base):
    __tablename__="articles"
    id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    title=Column(String, index=True,nullable=False,unique=True)
    content=Column(String)
    date=Column(DateTime, default=datetime.datetime.now)
    in_favorites=Column(Boolean, default=False)
    tags=relationship("Tags", secondary=post_and_tag ,back_populates="posts")
    pics=relationship("Pics",back_populates="article")
    autor_id=Column(Integer,ForeignKey("writer.id"))
    autor=relationship("Writer", back_populates="articles")
    is_suspended=Column(Boolean, default=False)
    likes=relationship("Like", back_populates="article")
    comments=relationship("Comment", back_populates="article")

    


class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    firstname=Column(String,nullable=False)
    lastname=Column(String, nullable=False)
    email=Column(String, nullable=False, index=True, unique=True)
    password=Column(String, nullable=False)
    user_type=Column(String, default="user")
    likes=relationship("Like", back_populates="user")
    
    joined=Column(DateTime, default=datetime.datetime.now)
    comments=relationship("Comment", back_populates="user",cascade="all, delete-orphan")
    __mapper_args__={
        "polymorphic_on": user_type,
        "polymorphic_identity": "user"

    }
    

class Writer(User):
    __tablename__ = 'writer'
    id=Column(Integer, ForeignKey("users.id"), primary_key=True)
    bio=Column(String)
    profile_pic=Column(String, nullable=True, default=None)

    articles=relationship("Article", back_populates="autor")

    
    __mapper_args__={
        "polymorphic_identity": "writer"

    }
    

class Admin(User):
    __tablename__="admin"
    id=Column(Integer, ForeignKey("users.id"), primary_key=True)
    __mapper_args__={
        "polymorphic_identity": "admin"

    }



class Like(Base):
    __tablename__="likes"
    id=Column(Integer, primary_key=True)
    user_id=Column(Integer, ForeignKey("users.id"))
    article_id=Column(Integer, ForeignKey("articles.id"))
    user=relationship("User", back_populates="likes")
    article=relationship("Article", back_populates="likes")


class OTP(Base):
    __tablename__="otp"
    id=id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    code=Column(Integer)
    exp_time=Column(DateTime, default=lambda: datetime.datetime.now()+datetime.timedelta(minutes=10))
    expired=Column(Boolean, default=False)
    user_id=Column(Integer, ForeignKey("users.id"))



    
class Tags(Base):
    __tablename__="tags"
    id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    name=Column(String, index=True)
    posts=relationship("Article", secondary=post_and_tag ,back_populates="tags")




class Pics(Base):
    __tablename__="media"
    id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    link=Column(String)
    post_id=Column(Integer, ForeignKey("articles.id"))
    article=relationship("Article",back_populates="pics")


class Comment(Base):
    __tablename__="comments"
    id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    text=Column(String)
    article_id=Column(Integer, ForeignKey("articles.id"))
    user_id=Column(Integer, ForeignKey("users.id"))
    user=relationship("User", back_populates="comments")
    article=relationship("Article", back_populates="comments")


