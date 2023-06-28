## BB-API-Exercise

Design and implement a RESTful web API that can be used to maintain a database of GUIDs (Globally Unique Identifier) and associated metadata.

## Things that needs to be installed in your system

- Install Homebrew
- Brew install python3
- brew tap mongodb/brew
- brew install mongodb-community
- brew services start mongodb/brew/mongodb-community
- brew services start redis
- pip3 install pymongo tornado redis motor aioredis coverage
- brew services start mongodb-community
- brew services start redis

## How to run the code

- Enter Virtual Environment (use python version 3.8.6) - python3.8 -m venv venv38 source venv38/bin/ activate
- Start the redis server: run command redis-server in one terminal
- Open another terminal and run the command redis-cli to see the connection, to terminate that use Control+C in Mac
- Then run the python script - python3 guid_api.py
- Either use curl commands or any URL testing tool(Postman) to test the communication of the api
- Run the test class - coverage run -m unittest discover

## Testing

Testing was done using unit tests embedded into the test class.

- Download and setup Postman or use Curl commands
- Download and setup MongoDB Compass

## To view the entries in the database:

1.  Open MongoDB Compass and connect to the following URI: `mongodb://localhost:27017/`
2.  Go to the database named **_test_db_**.
3.  Go to the document named **_guids_**.

# Problems you might run into

1. When you are running redis-server, you can encounter a problem for the port as it is already in use
2. When you are running the python script, you can encounter a problem for the port as it is already in use

# How to solve them

You can kill the specific port number you want to use
