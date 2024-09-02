# Step by Step Guide

The first thing we need to do, after installing [MongoDB Community Edition](https://www.mongodb.com/try/download/community-edition) and configure it (for that you can use [this page](https://www.prisma.io/dataguide/mongodb/setting-up-a-local-mongodb-database#setting-up-mongodb-on-linux)), is to create a database and then add data to it. For this example we can do it like this:

```python
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
```

Now that we have information to paginate let's start by searching the data from the beginning and going forward to the end. But, you must remember that you are traversing the data, so you must identify the next position (or the next cursor) and the previous one so you can really traverse the information. Also, you must check if there is data in the next page. This is a way to do it:

```python
# Import libraries
from bson.objectid import ObjectId
from datetime import datetime

from loguru import logger
from pymongo import MongoClient

# Use token to connect to local database
token = "mongodb://localhost:27017"
client = MongoClient(token)
# Access cursor_db collection (it will be created if it does not exist)
cursor_db = client.cursor_db.content
default_page_size = 5

def fetch_next_page(cursor, page_size = None):
    # Use the provided page_size or use a default value
    page_size = page_size or default_page_size  

    # Check if there is a cursor
    if cursor:
        # Get documents with `_id` greater than the cursor
        query = {"_id": {'$gt': cursor}}
    else:
        # Get everything
        query = {}
    # Sort in ascending order by `_id`
    sort_order = 1 

    # Define the aggregation pipeline
    pipeline = [
        {"$match": query},  # Filter based on the cursor
        {"$sort": {"_id": sort_order}},  # Sort documents by `_id`
        {"$limit": page_size + 1},  # Limit results to page_size + 1 to check if there's a next page
        # {"$project": {"_id": 1, "title": 1, "content": 1}}  # In case you want to return only certain attributes
    ]
    
    # Execute the aggregation pipeline
    results = list(cursor_db.aggregate(pipeline))
    # logger.debug(results)

    # Validate if some data was found
    if not results: raise ValueError("No data found")

    # Check if there are more documents than the page size
    if len(results) > page_size:
        # Deleting extra document
        results.pop(-1)
        # Set the cursor for the next page
        next_cursor = results[-1]['_id']
        # Set the previous cursor
        if cursor:
            # in case the cursor have data
            prev_cursor = results[0]['_id']
        else:
            # In case the cursor don't have data (first page)
            prev_cursor = None
        # Indicate you haven't reached the end of the data
        at_end = False
    else:
        # Indicate that there are not more pages available (last page reached)
        next_cursor = None
        # Set the cursor for the previous page
        prev_cursor = results[0]['_id']
        # Indicate you have reached the end of the data
        at_end = True
    return results, next_cursor, prev_cursor, at_end


@logger.catch
def main():
    """Main function."""
    # Get the first page
    results, next_cursor, prev_cursor, at_end = fetch_next_page(None)
    logger.info(f"{results = }")
    logger.info(f"{next_cursor = }")
    logger.info(f"{prev_cursor = }")
    logger.info(f"{at_end = }")

if __name__:
    main()
    logger.info("--- Execution end ---")

```
That code return this:

```
2024-09-02 08:55:24.388 | INFO     | __main__:main:73 - results = [{'_id': ObjectId('66bdfdcf7a0667fd1888c20c'), 'title': 'Post 1', 'content': 'Content 1', 'date': datetime.datetime(2023, 8, 1, 0, 0)}, {'_id': ObjectId('66bdfdcf7a0667fd1888c20d'), 'title': 'Post 2', 'content': 'Content 2', 'date': datetime.datetime(2023, 8, 2, 0, 0)}, {'_id': ObjectId('66bdfdcf7a0667fd1888c20e'), 'title': 'Post 3', 'content': 'Content 3', 'date': datetime.datetime(2023, 8, 3, 0, 0)}, {'_id': ObjectId('66bdfdcf7a0667fd1888c20f'), 'title': 'Post 4', 'content': 'Content 4', 'date': datetime.datetime(2023, 8, 4, 0, 0)}, {'_id': ObjectId('66bdfdcf7a0667fd1888c210'), 'title': 'Post 5', 'content': 'Content 5', 'date': datetime.datetime(2023, 8, 5, 0, 0)}]
2024-09-02 08:55:24.388 | INFO     | __main__:main:74 - next_cursor = ObjectId('66bdfdcf7a0667fd1888c210')
2024-09-02 08:55:24.388 | INFO     | __main__:main:75 - prev_cursor = None
2024-09-02 08:55:24.388 | INFO     | __main__:main:76 - at_end = False
2024-09-02 08:55:24.388 | INFO     | __main__:<module>:79 - --- Execution end ---
```

You can see that the cursor points to a next page and the previous one is `None`, also, it identifies that it is not the end of the data. To obtain this values we must have a better look at the function `fetch_next_page`. In there we can see that we defined the `page_size`, the `query`, the `sort_order`, and then we create the pipeline to the **aggregation operation**. To identify if there is another page of information we use the `$limit` operator, we give the value of `page_size + 1` to check if there is, in fact, another page with that `+ 1`. To actually check it we use the expresion `len(results) > page_size`, in case the number of data returned is greater than `page_size` then there is another page; on the contrary, this is the last page.

For the case where there is a next page we must delete the last element from the list of information we queried, because that was the `+ 1` in the pipeline, we need to set `next_cursor` with the `_id` from the current last value from the list, and set the `prev_cursor` (the previous cursor) according to the case, if there was a cursor that means that there is data before this one, in the other case, that means this is the first group of data, so there is no previous information, therefore, the cursor should be the first `_id` from the data found or `None`.

Now that we know how to search the data and add some important validation we must enable a way to traverse it forward, for that we will use the `input` command to request from the user running the script to write the direction to move, though, right now it will only be forward (f). We can update our `main` function to do it like this:

```python

@logger.catch
def main():
    """Main function."""
    # Get the first page
    results, next_cursor, prev_cursor, at_end = fetch_next_page(None)
    logger.info(f"{results = }")
    logger.info(f"{next_cursor = }")
    logger.info(f"{prev_cursor = }")
    logger.info(f"{at_end = }")
    # Checking if there is more data to show
    if next_cursor:
        # Enter a cycle to traverse the data
        while(True):
            print(125 * "*")
            # Ask for the user to move forward or cancel the execution
            inn = input("Can only move Forward (f) or Cancel (c): ")

            # Execute action acording to the input
            if inn == "f":
                results, next_cursor, prev_cursor, at_end = fetch_next_page(next_cursor, default_page_size)
            elif inn == "c":
                logger.warning("------- Canceling execution -------")
                break
            else:
                # In case the user sends something that is not a valid option
                print("Not valid action, it can only move in the opposite direction.")
                continue
            logger.info(f"{results = }")
            logger.info(f"{next_cursor = }")
            logger.info(f"{prev_cursor = }")
            logger.info(f"{at_end = }")
    else:
        logger.warning("There is not more data to show")
```

With this we are able to traverse the data until the end, but when it reaches the end it returns to the beginning and the cycle starts again, so we must add some validations to avoid that and also to move backwards. For that we will create the function `fetch_previous_page` and add some changes to the *main* function:

```python
def fetch_previous_page(cursor, page_size = None):
    # Use the provided page_size or fallback to the class attribute
    page_size = page_size or default_page_size  

    # Check if there is a cursor
    if cursor:
        # Get documents with `_id` less than the cursor
        query = {'_id': {'$lt': cursor}}
    else:
        # Get everything
        query = {}
    # Sort in descending order by `_id`
    sort_order = -1  

    # Define the aggregation pipeline
    pipeline = [
        {"$match": query},  # Filter based on the cursor
        {"$sort": {"_id": sort_order}},  # Sort documents by `_id`
        {"$limit": page_size + 1},  # Limit results to page_size + 1 to check if there's a next page
        # {"$project": {"_id": 1, "title": 1, "content": 1}}  # In case you want to return only certain attributes
    ]
    
    # Execute the aggregation pipeline
    results = list(cursor_db.aggregate(pipeline))

    # Validate if some data was found
    if not results: raise ValueError("No data found")

    # Check if there are more documents than the page size
    if len(results) > page_size:
        # Deleting extra document
        results.pop(-1)
        # Reverse the results to maintain the correct order
        results.reverse()
        # Set the cursor for the previous page
        prev_cursor = results[0]['_id']
        # Set the cursor for the next page
        next_cursor = results[-1]['_id']
        # Indicate you are not at the start of the data
        at_start = False
    else:
        # Reverse the results to maintain the correct order
        results.reverse()
        # Indicate that there are not more previous pages available (initial page reached)
        prev_cursor = None
        # !!!!
        next_cursor = results[-1]['_id']
        # Indicate you have reached the start of the data
        at_start = True
    return results, next_cursor, prev_cursor, at_start
```

Extremely similar to `fetch_next_page`, but the query (in case the conditions are met) use the operator `$lt` and `sort_order` must be `-1` to bring the data in the needed order. Now, when validating if `len(results) > page_size`, in case the condition is *true*, then it removes the extra element and reverse the order of the data for it to be shown correctly then set the previous cursor to the first element of the data and the next cursor to the last. On the contrary, the data is reverse, the previous cursor is set to `None` (because there is not previous data), and set the next cursor to the last value of the list. In both cases, a boolean variable called `at_start` is defined to identify this situation. Now we must add the interaction with the user to go backwards in the `main` function, so there are 3 situation to handle in case we are at the beginning, the end, or in the middle of the data: only going forward, only going backwards, and going forward o backward:

```python
@logger.catch
def main():
    """Main function."""
    # Get the first page
    results, next_cursor, prev_cursor, at_end = fetch_next_page(None)
    logger.info(f"{results = }")
    logger.info(f"{next_cursor = }")
    logger.info(f"{prev_cursor = }")
    logger.info(f"{at_end = }")
    # Checking if there is more data to show
    if not(at_start and at_end):
        # Enter a cycle to traverse the data
        while(True):
            print(125 * "*")
            # Ask for the user to move forward or cancel the execution
            if at_end:
                inn = input("Can only move Backward (b) or Cancel (c): ")
                stage = 0
            elif at_start:
                inn = input("Can only move Forward (f) or Cancel (c): ")
                stage = 1
            else:
                inn = input("Can move Forward (f), Backward (b), or Cancel (c): ")
                stage = 2

            # Execute action acording to the input
            if inn == "f" and stage in [1, 2]:
                results, next_cursor, prev_cursor, at_end = fetch_next_page(next_cursor, page_size)
                # For this example, you must reset here the value, otherwise you lose the reference of the cursor
                at_start = False
            elif inn == "b" and stage in [0, 2]:
                results, next_cursor, prev_cursor, at_start = fetch_previous_page(prev_cursor, page_size)
                # For this example, you must reset here the value, otherwise you lose the reference of the cursor
                at_end = False
            elif inn == "c":
                logger.warning("------- Canceling execution -------")
                break
            else:
                print("Not valid action, it can only move in the opposite direction.")
                continue
            logger.info(f"{results = }")
            logger.info(f"{next_cursor = }")
            logger.info(f"{prev_cursor = }")
            logger.info(f"{at_start = }")
            logger.info(f"{at_end = }")
    else:
        logger.warning("There is not more data to show")

```

We added validation to the users input to identify the *stage* where we are while traversing the data, also note that `at_start` and `at_end` after the execution of `fetch_next_page` and `fetch_previous_page` respectively which are needed to reset after reaching those limits. Now you can reach the end of the data and go backwards until the start. The validation after getting the first page of data was update to check if the flags `at_start` and `at_end` are `True`, which will indicate that there is no more data to show.

***Note***: I was facing a bug at this point which I cannot reproduce right now, but it was causing problems when going backward and reaching the start, the cursor was pointing to the wrong place and when you wanted to go forward it skip 1 element. To solve it I added a validation in `fetch_previous_page` if a parameter called `prev_at_start` (which is the previous value of `at_start`) to assing `next_cursor` the value `results[0]['_id']` or, `results[-1]['_id']` in case the previous stage was not at the beginning of the data. This will be ommited from now on, but I think is worth the mention.

Now that we can traverse the data from beginning to end and going forward or backward in it, we can create a class that have all this functions and call it to use the example. Also we must add the docstring so everything is documents correctly. The result of that are is this code:

```python
"""Cursor Paging/Pagination Pattern Example."""
from bson.objectid import ObjectId
from datetime import datetime

from loguru import logger
from pymongo import MongoClient

class cursorPattern:
    """
    A class to handle cursor-based pagination for MongoDB collections.

    Attributes:
    -----------
    cursor_db : pymongo.collection.Collection
        The MongoDB collection used for pagination.
    page_size : int
        Size of the pages.

    """

    def __init__(self, page_size: int = 5) -> None:
        """Initializes the class.

        Sets up a connection to MongoDB and specifying 
        the collection to work with.

        """
        token = "mongodb://localhost:27017"
        client = MongoClient(token)
        self.cursor_db = client.cursor_db.content
        self.page_size = page_size

    def add_data(self,) -> None:
        """Inserts sample data into the MongoDB collection for demonstration purposes.

        Note:
        -----
        It should only use once, otherwise you will have repeated data.

        """
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
        self.cursor_db.insert_many(sample_posts)

    def _fetch_next_page(
        self, cursor: ObjectId | None, page_size: int | None = None
    ) -> tuple[list, ObjectId | None, ObjectId | None, bool]:
        """Retrieves the next page of data based on the provided cursor.

        Parameters:
        -----------
        cursor : ObjectId | None
            The current cursor indicating the last document of the previous page.
        page_size : int | None
            The number of documents to retrieve per page (default is the class's page_size).

        Returns:
        --------
        tuple:
            - results (list): The list of documents retrieved.
            - next_cursor (ObjectId | None): The cursor pointing to the start of the next page, None in case is the last page.
            - prev_cursor (ObjectId | None): The cursor pointing to the start of the previous page, None in case is the start page.
            - at_end (bool): Whether this is the last page of results.
        """
        # Use the provided page_size or fallback to the class attribute
        page_size = page_size or self.page_size  

        # Check if there is a cursor
        if cursor:
            # Get documents with `_id` greater than the cursor
            query = {"_id": {'$gt': cursor}}
        else:
            # Get everything
            query = {}
        # Sort in ascending order by `_id`
        sort_order = 1 

        # Define the aggregation pipeline
        pipeline = [
            {"$match": query},  # Filter based on the cursor
            {"$sort": {"_id": sort_order}},  # Sort documents by `_id`
            {"$limit": page_size + 1},  # Limit results to page_size + 1 to check if there's a next page
            # {"$project": {"_id": 1, "title": 1, "content": 1}}  # In case you want to return only certain attributes
        ]
        
        # Execute the aggregation pipeline
        results = list(self.cursor_db.aggregate(pipeline))
        # logger.debug(results)

        # Validate if some data was found
        if not results: raise ValueError("No data found")

        # Check if there are more documents than the page size
        if len(results) > page_size:
            # Deleting extra document
            results.pop(-1)
            # Set the cursor for the next page
            next_cursor = results[-1]['_id']
            # Set the previous cursor
            if cursor:
                # in case the cursor have data
                prev_cursor = results[0]['_id']
            else:
                # In case the cursor don't have data (first time)
                prev_cursor = None
            # Indicate you haven't reached the end of the data
            at_end = False
        else:
            # Indicate that there are not more pages available (last page reached)
            next_cursor = None
            # Set the cursor for the previous page
            prev_cursor = results[0]['_id']
            # Indicate you have reached the end of the data
            at_end = True
        return results, next_cursor, prev_cursor, at_end

    def _fetch_previous_page(
        self, cursor: ObjectId | None, page_size: int | None = None, 
    ) -> tuple[list, ObjectId | None, ObjectId | None, bool]:
        """Retrieves the previous page of data based on the provided cursor.

        Parameters:
        -----------
        cursor : ObjectId | None
            The current cursor indicating the first document of the current page.
        page_size : int
            The number of documents to retrieve per page.
        prev_at_start : bool
            Indicates whether the previous page was the first page.

        Returns:
        --------
        tuple:
            - results (list): The list of documents retrieved.
            - next_cursor (ObjectId | None): The cursor pointing to the start of the next page, None in case is the last page.
            - prev_cursor (ObjectId | None): The cursor pointing to the start of the previous page, None in case is the start page.
            - at_start (bool): Whether this is the first page of results.
        """
        # Use the provided page_size or fallback to the class attribute
        page_size = page_size or self.page_size  

        # Check if there is a cursor
        if cursor:
            # Get documents with `_id` less than the cursor
            query = {'_id': {'$lt': cursor}}
        else:
            # Get everything
            query = {}
        # Sort in descending order by `_id`
        sort_order = -1  

        # Define the aggregation pipeline
        pipeline = [
            {"$match": query},  # Filter based on the cursor
            {"$sort": {"_id": sort_order}},  # Sort documents by `_id`
            {"$limit": page_size + 1},  # Limit results to page_size + 1 to check if there's a next page
            # {"$project": {"_id": 1, "title": 1, "content": 1}}  # In case you want to return only certain attributes
        ]
        
        # Execute the aggregation pipeline
        results = list(self.cursor_db.aggregate(pipeline))

        # Validate if some data was found
        if not results: raise ValueError("No data found")

        # Check if there are more documents than the page size
        if len(results) > page_size:
            # Deleting extra document
            results.pop(-1)
            # Reverse the results to maintain the correct order
            results.reverse()
            # Set the cursor for the previous page
            prev_cursor = results[0]['_id']
            # Set the cursor for the next page
            next_cursor = results[-1]['_id']
            # Indicate you are not at the start of the data
            at_start = False
        else:
            # Reverse the results to maintain the correct order
            results.reverse()
            # Indicate that there are not more previous pages available (initial page reached)
            prev_cursor = None
            # if prev_at_start:
            #     # in case before was at the starting page
            #     logger.warning("Caso 1")
            #     next_cursor = results[0]['_id']
            # else:
            #     # in case before was not at the starting page
            #     logger.warning("Caso 2")
            #     next_cursor = results[-1]['_id']
            next_cursor = results[-1]['_id']
            # Indicate you have reached the start of the data
            at_start = True
        return results, next_cursor, prev_cursor, at_start

    def start_pagination(self):
        """Inicia la navegacion de datos."""
        # Change page size in case you want it, only leave it here for reference
        page_size = None
        # Retrieve the first page of results
        results, next_cursor, prev_cursor, at_end = self._fetch_next_page(None, page_size)
        at_start = True
        logger.info(f"{results = }")
        logger.info(f"{next_cursor = }")
        logger.info(f"{prev_cursor = }")
        logger.info(f"{at_start = }")
        logger.info(f"{at_end = }")
        # if next_cursor:
        if not(at_start and at_end):
            while(True):
                print(125 * "*")
                if at_end:
                    inn = input("Can only move Backward (b) or Cancel (c): ")
                    stage = 0
                    # =====================================================
                    # You could reset at_end here, but in this example that
                    # will fail in case the user sends something different
                    # from Backward (b) or Cancel (c)
                    # =====================================================
                    # at_end = False
                elif at_start:
                    inn = input("Can only move Forward (f) or Cancel (c): ")
                    stage = 1
                    # =====================================================
                    # You could reset at_end here, but in this example that
                    # will fail in case the user sends something different
                    # from Forward (f) or Cancel (c)
                    # =====================================================
                    # at_start = False
                else:
                    inn = input("Can move Forward (f), Backward (b), or Cancel (c): ")
                    stage = 2

                # Execute action acording to the input
                if inn == "f" and stage in [1, 2]:
                    results, next_cursor, prev_cursor, at_end = self._fetch_next_page(next_cursor, page_size)
                    # For this example, you must reset here the value, otherwise you lose the reference of the cursor
                    at_start = False
                elif inn == "b" and stage in [0, 2]:
                    # results, next_cursor, prev_cursor, at_start = self._fetch_previous_page(prev_cursor, at_start, page_size)
                    results, next_cursor, prev_cursor, at_start = self._fetch_previous_page(prev_cursor, page_size)
                    # For this example, you must reset here the value, otherwise you lose the reference of the cursor
                    at_end = False
                elif inn == "c":
                    logger.warning("------- Canceling execution -------")
                    break
                else:
                    print("Not valid action, it can only move in the opposite direction.")
                    continue
                logger.info(f"{results = }")
                logger.info(f"{next_cursor = }")
                logger.info(f"{prev_cursor = }")
                logger.info(f"{at_start = }")
                logger.info(f"{at_end = }")
        else:
            logger.warning("There is not more data to show")

@logger.catch
def main():
    """Main function."""
    my_cursor = cursorPattern(page_size=5)
    # my_cursor.add_data()
    my_cursor.start_pagination()

if __name__:
    main()
    logger.info("--- Execution end ---")

```

We added the page_size as an attribute to the class `cursorPattern` for it to be easier to define the size of every page and added docstrings to the class and its methods.


