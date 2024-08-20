# Cursor Pagination Example

This example show how you can use Cursor Pagination Pattern (or Cursor Paging Pattern) with python and MongoDB. This example will assume you know how to set up [Python Poetry](https://python-poetry.org) to handle dependencies.

The need for this example is because when I was searching for Cursor Pagination I could only find examples that go forward but not backward, and to also handle the data at the start and end.

## TO DO

* Re-read about traversing arrays or linked list to apply those algorithms in this example. The current version is base on them from memory not by comparing to them 1-1.
* Add a note that you can encrypt the `_id` or similar to protect the data.

## Requeriments

You first need a local Mongo database working, for that you must download [MongoDB Community Edition](https://www.mongodb.com/try/download/community-edition). Afterwards, you must start the process, for that you can use [this page](https://www.prisma.io/dataguide/mongodb/setting-up-a-local-mongodb-database#setting-up-mongodb-on-linux) to guide yourself, there are examples for Windows, MacOS, and Linux.

Don't forget to use `poetry install` to install the dependencies. Be aware of the python version on `pyproject.toml` in case you need to change it.

## How to use

Before you start the example you must go to the file `main.py` an in there you must uncomment the second line in the `main` function: `my_cursor.add_data()`, this will write the example data. After that, you must comment that line again and uncomment the next one: `my_cursor.start_pagination()`. Now you can use `poetry shell` and `python main.py` (or `poetry run python main.py`).

The example will show the results from the query (`results`), the value of the next cursor (`next_cursor`), the value of the previous cursor (`prev_cursor`), indicate you if it is at the start of the data (`at_start`), and indicate you if it is at the end of the data (`at_end`). Then, in case there is enough data (which is the case unless you alter the value of `page_size`) you will be prompted to move **forward** with `f` or **cancel** with `c`. If you send `f`, in the next page you will have the extra option of going **backward** with `b`.

And that's it, straightforward the example for Cursor pagination.

## Version

V. 1.0.0
