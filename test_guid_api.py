import unittest
import json
import time
import tornado.testing
import tornado.ioloop
import motor.motor_tornado
import aioredis
import redis
from guid_api import Application, GUIDHandler
from tornado.testing import gen_test

class TestGUIDHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUp(self):
        super().setUp()
        self.db = motor.motor_tornado.MotorClient().test_db
        self.redis = aioredis.from_url("redis://localhost")

        # Insert a test GUID into MongoDB
        self.test_guid = "9094E4C980C74043A4B586B420E69CCC"
        self.io_loop.run_sync(lambda: self.db.guids.insert_one({
            "guid": self.test_guid,
            "expire": str(int(time.time()) + 30*24*60*60),
            "user": "test_user"
        }))

        serialized_document = {
            "guid": self.test_guid,
            "expire": str(int(time.time()) + 30*24*60*60),  # 30 days from now
            "user": "test_user"
        }
        self.io_loop.run_sync(lambda: self.redis.set(self.test_guid, json.dumps(serialized_document)))

    def tearDown(self):
        # Delete the test GUID from MongoDB
        self.io_loop.run_sync(lambda: self.db.guids.delete_one({"guid": self.test_guid}))

        # Delete the test GUID from Redis
        self.io_loop.run_sync(lambda: self.redis.delete(self.test_guid))

        super().tearDown()

    # Test function to verify the successful retrieval of all GUIDs by sending a GET request to the '/guid' endpoint
    @gen_test
    async def test_get_all(self):
        response = await self.http_client.fetch(self.get_url('/guid'), method='GET')
        self.assertEqual(response.code, 200)

    # Test function to verify creation of a new GUID by sending a POST request.
    @gen_test
    async def test_post(self):
        data = json.dumps({'user': 'test_user'})
        response = await self.http_client.fetch(self.get_url('/guid'), method='POST', body=data)
        self.assertEqual(response.code, 200)

    # Test function to verify the retrieval of a specific GUID by sending a GET request
    @gen_test
    async def test_get_specific(self):
        response = await self.http_client.fetch(self.get_url(f'/guid/{self.test_guid}'), method='GET')
        self.assertEqual(response.code, 200)

    # Test function to verify the successful deletion of a specific GUID by sending a DELETE request
    @gen_test
    async def test_delete(self):
        response = await self.http_client.fetch(self.get_url(f'/guid/{self.test_guid}'), method='DELETE')
        self.assertEqual(response.code, 200)
    

