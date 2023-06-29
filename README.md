# BB-API-Exercise

Design and implement a RESTful web API that can be used to maintain a database of GUIDs (Globally Unique Identifier) and associated metadata.

## Prerequisites

- brew tap mongodb/brew
- brew install mongodb-community
- brew services start mongodb/brew/mongodb-community
- brew services start redis
- brew services start mongodb-community
- brew services start redis

## How to run the code

- Enter Virtual Environment (use python version 3.8.6)
  1. python3.8 -m venv venv38
  2. source venv38/bin/ activate
- Start the redis server: <br>
  run command redis-server in one terminal
- Open another terminal: <br>
  run the command redis-cli to see the connection, to terminate that use Control+C in Mac
- Install all the requirements in the virtual environment: <br> 
  pip install -r requirements.txt
- Then run the python script: <br>
  python3 guid_api.py
- Either use curl commands or any URL testing tool(Postman) to test the communication of the api
- Run the test class: <br>
  coverage run -m unittest discover

## Testing

Testing was done using unit tests embedded into the test class.

- Download and setup Postman or use Curl commands
- Download and setup MongoDB Compass

## To view the entries in the database:

1.  Open MongoDB Compass and connect to the following URI: `mongodb://localhost:27017/`
2.  Go to the database named **_test_db_**.
3.  Go to the document named **_guids_**.

## Problems you might run into

1. When you are running redis-server, you can encounter a problem for the port as it is already in use
2. When you are running the python script, you can encounter a problem for the port as it is already in use

## How to solve them

You can kill the specific port number you want to use.

## References

1. https://realpython.com/python-redis/
2. https://www.mongodb.com/developer/code-examples/python/python-quickstart-tornado/
3. https://www.tornadoweb.org/en/stable/
4. https://toolsqa.com/postman/guid/
5. https://redis.io/docs/
6. https://www.tornadoweb.org/en/stable/guide/structure.html
7. https://www.youtube.com/watch?v=DQNW9qhl4eA&list=PLzMcBGfZo4-kwmIcMDdXSuy_wSqtU-xDP
8. https://www.youtube.com/watch?v=Hbt56gFj998
