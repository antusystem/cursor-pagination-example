"""Codigo de ejemplo para implementar el Patron de empaginado del tipo Cursor (Cursor Paging/Pagination Pattern)."""
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
        self, cursor: ObjectId | None, prev_at_start: bool, page_size: int | None = None, 
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
            if prev_at_start:
                # in case before was at the starting page
                next_cursor = results[0]['_id']
            else:
                # in case before was not at the starting page
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
                    results, next_cursor, prev_cursor, at_start = self._fetch_previous_page(prev_cursor, at_start, page_size)
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
