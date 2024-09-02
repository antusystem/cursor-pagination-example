# Import libraries
from datetime import datetime
from pymongo import MongoClient

# Use token to connect to local database
token = "mongodb://localhost:27017"
client = MongoClient(token)
# Access cursor_db collection (it will be created if it does not exist)
cursor_db = client.cursor_db.content
# Data to add
sample_posts = [
    {"title": "Post 1", "content": "Content 1", "date": datetime(2023, 8, 1)},
    {"title": "Post 2", "content": "Content 2", "date": datetime(2023, 8, 2)},
    {"title": "Post 3", "content": "Content 3", "date": datetime(2023, 8, 3)},
    {"title": "Post 4", "content": "Content 4", "date": datetime(2023, 8, 4)},
    {"title": "Post 5", "content": "Content 5", "date": datetime(2023, 8, 5)},
    {"title": "Post 6", "content": "Content 6", "date": datetime(2023, 8, 6)},
    {"title": "Post 7", "content": "Content 7", "date": datetime(2023, 8, 7)},
    {"title": "Post 8", "content": "Content 8", "date": datetime(2023, 8, 8)},
    {"title": "Post 9", "content": "Content 9", "date": datetime(2023, 8, 9)},
    {"title": "Post 10", "content": "Content 10", "date": datetime(2023, 8, 10)},
    {"title": "Post 11", "content": "Content 11", "date": datetime(2023, 8, 11)},
]
# Adding data to collection
cursor_db.insert_many(sample_posts)
