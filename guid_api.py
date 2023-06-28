import tornado.ioloop
import tornado.web
import uuid
import time
import motor.motor_tornado
import aioredis
import json
import redis

# A tornado application with request handlers, that also establishes connections to a MongoDb database
# and a Redis Server.
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/guid/([A-F0-9]{32})", GUIDHandler),
            (r"/guid", GUIDHandler),
        ]
        super(Application, self).__init__(handlers)
        self.db = motor.motor_tornado.MotorClient().test_db
        self.redis = aioredis.from_url("redis://localhost")

class GUIDHandler(tornado.web.RequestHandler):

    # Function to handle the GET request for retrieving metadata
    async def get(self, guid=None):
        if guid is None:
            # Retrieves all GUIDS also handles the case when no specific GUID is mentioned
            guids = await self.application.db.guids.find().to_list(None)
            guids_serialized = []
            for guid in guids:
                guid['_id'] = str(guid['_id'])  # Convert ObjectId to string
                guids_serialized.append(guid)
            self.write(json.dumps(guids_serialized))
            print(self.get_status(), "Successful get request")
        else:
            # Retrieves metadata associated with the specified GUID
            cached_data = await self.application.redis.get(str(guid))  # Convert guid to string
            # Check if the data is still there in the database
            if cached_data is not None:
                data = await self.application.db.guids.find_one({"guid": guid})
                # If data is not found in the databse, remove it from the cache
                if data is None:
                    await self.application.redis.delete(guid)
                else:
                    self.set_header("Content-Type", "application/json")
                    self.write(cached_data)
                    return

            data = await self.application.db.guids.find_one({"guid": guid})
            # Checks if a data with the specified GUID exists in the MongoDB database, 
            # and if it does not exist or is expired, it raises a 404 Not Found HTTP error.
            if not data or await self.check_expired(guid):
                raise tornado.web.HTTPError(404, "GUID not found or expired")

            # Creates a dictionary named serialized_data with the values extracted from the MongoDB query result.
            serialized_data = {
                "guid": data["guid"],
                "expire": data.get("expire"),
                "user": data.get("user")
            }

            # Stores the serialized_data dictionary as a JSON string in Redis, using the GUID as the key.
            await self.application.redis.set(guid, json.dumps(serialized_data))

            # Sets the response header to specify the content type as JSON 
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(serialized_data))
            print(self.get_status(), "Successful get request")

    # Function to handle the POST request
    async def post(self, guid=None):
        # Get input data and if it is not in the correct JSON format raise an error
        try:
            input_data = tornado.escape.json_decode(self.request.body)
        except json.JSONDecodeError:
            raise tornado.web.HTTPError(400, "Invalid JSON format")

        # Validate input data
        if not await self.validate_json(input_data):
            raise tornado.web.HTTPError(400, "Invalid input format")

        # Generate a new GUID, if it is not provided
        if guid is None:
            guid = await self.generate_guid()
    
        # Set 'expire' to 30 days from the creation, if it is not provided
        if 'expire' not in input_data:
            input_data['expire'] = str(int(time.time()) + 30*24*60*60)

        # Save the input data with the given GUID
        input_data['guid'] = guid
        await self.application.db.guids.update_one({'guid': guid}, {"$set": input_data}, upsert=True)

        # Delete the GUID from cache so the updated value will be fetched next time
        await self.application.redis.delete(guid)

        # Respond with the updated data
        self.write({
            "guid": guid,
            "expire": input_data.get("expire"),
            "user": input_data.get("user")
        })
        print(self.get_status(), "Successful post request")

    # Function to handle the DELETE request
    async def delete(self, guid):
        # Return an error, if GUID doesn't exist
        if not await self.is_guid_exist(guid):
            raise tornado.web.HTTPError(404, "GUID not found")

        # Delete the GUID from MongoDB
        await self.application.db.guids.delete_one({'guid': guid})

        # Delete the GUID from cache
        await self.application.redis.delete(guid)

         # Check if the GUID is still in the cache after deletion
        cached_data = await self.application.redis.get(guid)
        if cached_data is not None:
            raise tornado.web.HTTPError(404, "GUID not found or expired")

        # Respond with a success message
        self.set_status(200)
        self.write({'message': 'GUID successfully deleted.'})
        print(self.get_status(), "Successfully deleted")

    # Function to check if GUID has expired or not
    async def check_expired(self, guid):
        # Fetch GUID data from MongoDB
        data = await self.application.db.guids.find_one({"guid": guid})

        # Return True as "expired", if GUID doesn't exist
        if not data:
            return True

        # Check if the expiration time has passed
        current_time = int(time.time())
        if "expire" in data and int(data["expire"]) < current_time:

            # If expired, delete it from both the cache and the database
            await self.application.db.guids.delete_one({"guid": guid})
            await self.application.redis.delete(guid)
            return True

        return False
        
    # Function to check if GUID exists or not
    async def is_guid_exist(self, guid):
        # Fetch GUID data from MongoDB
        data = await self.application.db.guids.find_one({"guid": guid})

        # Return False if GUID doesn't exist
        if not data:
            return False

        # Return True if GUID exists and is not expired
        if not await self.check_expired(guid):
            return True

        # Return False if GUID exists but is expired
        return False
        
    # Function to check if the data is in valid JSON format
    async def validate_json(self, json_data):
        # Check if "user" field exists
        if "user" not in json_data:
            return False

        # If "expire" field exists, check if it's a valid Unix Time
        if "expire" in json_data:
            try:
                int(json_data["expire"])
            except ValueError:
             return False

        return True
        
    # Function to generate random GUIDs
    async def generate_guid(self):
        # Generate a random UUID
        guid = uuid.uuid4()

        # Format the UUID as a 32-character hexadecimal string
        guid_str = guid.hex.upper()

        return guid_str

if __name__ == "__main__":
    app = Application()
    app.listen(8809)
    tornado.ioloop.IOLoop.current().start()