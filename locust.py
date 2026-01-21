import random
from locust import HttpUser, task, between

class ProBoundUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def trigger_call(self):
        # Pick a random ID from the 100 we generated
        user_id = random.randint(1, 100)
        headers = {"X-API-KEY": f"key_{user_id}"}
        
        self.client.post("/agent/call", headers=headers)