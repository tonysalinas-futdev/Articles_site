from database.database import Base
from sqlalchemy import String, Integer, ForeignKey, Column, DateTime, Table
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
    title=Column(String, index=True,nullable=False)
    content=Column(String)
    date=Column(DateTime, default=datetime.datetime.now)
    tags=relationship("Tags", secondary=post_and_tag ,back_populates="posts")
    pics=relationship("Pics",back_populates="article")
    autor_id=Column(Integer)
    comments=relationship("Comment", back_populates="article")
    reactions=relationship("Reaction", back_populates="article")
    

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
    post_id=Column(Integer, ForeignKey("articles.id"))
    article=relationship("Article", back_populates="comments")


class Reaction(Base):
    __tablename__="reactions"
    id=Column(Integer,primary_key=True, autoincrement=True, index=True)
    name=Column(String)
    article_id=Column(Integer, ForeignKey("articles.id"))
    article=relationship("Article", back_populates="reactions")
