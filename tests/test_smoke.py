import requests

def test_health_check(app_url):
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == 200