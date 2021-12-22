# uvicorn app.main:app --reload
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Post Schema
class Post(BaseModel):
    title: str
    content: str
    published: bool = False


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="santiago",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Connected!")
        break

    except Exception as e:
        print("Error: ", e)
        time.sleep(2)


@app.get("/")
def root():
    return {"data": "Hello"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": "success", "data": posts}


## POSTS
# GET Methods
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # DB Query to get all posts
    
    # Raw SQL Query
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()

    # Return all posts
    return {"data": posts}


@app.get("/posts/latest")
def get_latest_post():
    return {"data": my_posts[-1]}


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return {"data": post}


# POST Methods
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    post: Post,
    db: Session = Depends(get_db)
):
    # Raw SQL
    # Best way to execute SQL queries as it will protect our DB from SQL injection
    # cursor.execute(
    #     """INSERT INTO posts (title,content,published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # SQLAlchemy
    # Create a new post
    # Unpack the post object into a dict then pass it to the Post constructor
    new_post = models.Post(**post.dict())
    # Add the new post to the database
    db.add(new_post)
    # Save changes
    db.commit()
    # Return the new post from the database
    db.refresh(new_post)

    # Return the new post
    return {"data": new_post}


# DELETE Methods
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id)
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# UPDATE Methods
@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
def update_post(updated_post: Post, post_id: int, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))

    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
