import random
import time
from locust import HttpUser, task, between, events
from typing import Dict, List

class LocalizationManagerUser(HttpUser):
    """Load test user for the Localization Manager Backend"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user data on start"""
        self.languages = ["en", "es", "fr", "de"]
        self.components = ["welcome", "navigation", "user_profile", "footer"]
        self.cache_hits = 0
        self.cache_misses = 0
        
    @task(4)
    def get_welcome_component(self):
        """Test welcome component endpoint - high frequency"""
        lang = random.choice(self.languages)
        with self.client.get(
            f"/api/component/welcome?lang={lang}",
            name="/api/component/welcome",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("cached", False):
                    self.cache_hits += 1
                else:
                    self.cache_misses += 1
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def get_navigation_component(self):
        """Test navigation component endpoint - medium frequency"""
        lang = random.choice(self.languages)
        with self.client.get(
            f"/api/component/navigation?lang={lang}",
            name="/api/component/navigation",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("cached", False):
                    self.cache_hits += 1
                else:
                    self.cache_misses += 1
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def get_user_profile_component(self):
        """Test user profile component endpoint - medium frequency"""
        lang = random.choice(self.languages)
        with self.client.get(
            f"/api/component/user_profile?lang={lang}",
            name="/api/component/user_profile",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("cached", False):
                    self.cache_hits += 1
                else:
                    self.cache_misses += 1
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def get_footer_component(self):
        """Test footer component endpoint - medium frequency"""
        lang = random.choice(self.languages)
        with self.client.get(
            f"/api/component/footer?lang={lang}",
            name="/api/component/footer",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("cached", False):
                    self.cache_hits += 1
                else:
                    self.cache_misses += 1
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_health_check(self):
        """Test health check endpoint - low frequency"""
        with self.client.get(
            "/health",
            name="/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class CacheTestUser(HttpUser):
    """Specialized user for testing cache behavior"""
    
    wait_time = between(0.5, 1.5)  # Faster requests to test cache
    
    def on_start(self):
        """Initialize user data on start"""
        self.languages = ["en", "es", "fr", "de"]
        self.components = ["welcome", "navigation"]
        
    @task(5)
    def test_cache_behavior(self):
        """Repeatedly request same component to test cache effectiveness"""
        lang = random.choice(self.languages)
        component = random.choice(self.components)
        
        # Make multiple requests to the same endpoint to test cache
        for i in range(3):
            with self.client.get(
                f"/api/component/{component}?lang={lang}",
                name=f"/api/component/{component} (cache test)",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    cache_status = "cached" if data.get("cached", False) else "not_cached"
                    response.success()
                else:
                    response.failure(f"Status code: {response.status_code}")
            
            # Small delay between requests
            time.sleep(0.1)


class StressTestUser(HttpUser):
    """User for stress testing with high load"""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    def on_start(self):
        """Initialize user data on start"""
        self.languages = ["en", "es", "fr", "de"]
        self.components = ["welcome", "navigation", "user_profile", "footer"]
        
    @task(10)
    def stress_test_components(self):
        """High-frequency component requests"""
        lang = random.choice(self.languages)
        component = random.choice(self.components)
        
        with self.client.get(
            f"/api/component/{component}?lang={lang}",
            name="/api/component/[component] (stress test)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def stress_test_health(self):
        """High-frequency health check requests"""
        with self.client.get(
            "/health",
            name="/health (stress test)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


# Custom event listeners for additional metrics
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Custom request handler for additional metrics"""
    if exception:
        print(f"Request failed: {name} - {exception}")
    else:
        # You can add custom logging or metrics here
        pass


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a test is starting"""
    print("🚀 Load test starting for Localization Manager Backend")
    print(f"Target URL: {environment.host}")
    print(f"Number of users: {environment.runner.user_count}")
    print("📋 Testing endpoints:")
    print("   - GET /health")
    print("   - GET /api/component/{component_type}?lang={lang}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test is stopping"""
    print("🏁 Load test completed for Localization Manager Backend") 