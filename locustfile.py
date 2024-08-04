from locust import HttpUser, task, between

class APILoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_suggestions(self):
        self.client.post("/suggestions/", json={"sentence": "have a <blank> day"})

