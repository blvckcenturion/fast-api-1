from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time 


app = FastAPI()

my_posts = [
    {"id": 1, "title": "Post 1", "content": "Hello World", "published": True},
    {"id": 2, "title": "Post 2", "content": "Hello God", "published": True},
]
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
            cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connected!")
        break

    except Exception as e:
        print("Error: ", e)
        time.sleep(2)
    

@app.get("/")
def root():
    return {"data": "Hello"}


## POSTS
# GET Methods
@app.get("/posts")
def get_posts():
    # DB Query to get all posts
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    # Return all posts
    return {"data": posts}


@app.get("/posts/latest")
def get_latest_post():
    return {"data": my_posts[-1]}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(post_id),))
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {"data": post}


# POST Methods
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    post: Post,
):
    #Best way to execute SQL queries as it will protect our DB from SQL injection
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

# DELETE Methods
@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(post_id),))
    new_post = cursor.fetchone()
    if not new_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# UPDATE Methods
@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
def update_post(updated_post: Post, post_id: int):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (updated_post.title, updated_post.content, updated_post.published, str(post_id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    conn.commit()
    return {"data": post}

