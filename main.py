from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

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


@app.get("/")
def root():
    return {"data": "Hello"}


## POSTS
# GET Methods


@app.get("/posts")
def get_posts():
    return my_posts


@app.get("/posts/latest")
def get_latest_post():
    return {"data": my_posts[-1]}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    post_id = int(post_id)
    for post in my_posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# POST Methods


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    new_post: Post,
):
    post_dict = new_post.dict()
    post_dict["id"] = randrange(1, 100000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


# DELETE Methods


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    for index, post in enumerate(my_posts):
        if post["id"] == post_id:
            my_posts.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# UPDATE Methods


@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
def update_post(updated_post: Post, post_id: int):
    for index, post in enumerate(my_posts):
        if post["id"] == post_id:
            my_posts[index] = dict(updated_post)
            return {"data": my_posts[index]}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
