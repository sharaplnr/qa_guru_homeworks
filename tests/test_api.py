import json
from http import HTTPStatus

import pytest
import requests
from app.models.User import User

DELETED_MESSAGE = {"message": "User deleted"}
USER_NOT_FOUND = {"detail": "User not found"}

@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")

@pytest.fixture()
def create_user(app_url):
    user_data = dict(email="vasya.pupov@reqres.in", first_name="Vasya", last_name="Pupov",
                         avatar="https://reqres.in/img/faces/10-image.jpg")
    response = requests.post(f"{app_url}/api/users/", json=user_data)
    assert response.status_code == HTTPStatus.CREATED
    created_user_id = response.json()["id"]
    yield created_user_id

@pytest.fixture()
def create_user_and_delete(app_url):
    user_data = dict(email="tobias.funke@reqres.in", first_name="Ilnur", last_name="Sharapov",
                         avatar="https://reqres.in/img/faces/9-image.jpg")
    response = requests.post(f"{app_url}/api/users/", json=user_data)
    assert response.status_code == HTTPStatus.CREATED
    created_user_data = response.json()
    yield created_user_data

    delete_user_response = requests.delete(f"{app_url}/api/users/{created_user_data['id']}")
    assert delete_user_response.status_code == HTTPStatus.OK

@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()

class TestApi:

    @pytest.mark.usefixtures("fill_test_data")
    def test_users(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK

        user_list = response.json()
        for user in user_list:
            User.model_validate(user)


    @pytest.mark.usefixtures("fill_test_data")
    def test_users_no_duplicates(self, users):
        users_ids = [user["id"] for user in users]
        assert len(users_ids) == len(set(users_ids))


    def test_user(self, app_url, fill_test_data):
        for user_id in (fill_test_data[0], fill_test_data[-1]):
            response = requests.get(f"{app_url}/api/users/{user_id}")
            assert response.status_code == HTTPStatus.OK
            user = response.json()
            User.model_validate(user)


    @pytest.mark.parametrize("user_id", [13])
    def test_user_nonexistent_values(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND


    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_user_invalid_values(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("user_data", [dict(email="test1.test1@reqres.in", first_name="Test1", last_name="Test1",
                         avatar="https://reqres.in/img/faces/9-image.jpg")])
    def test_create_user(self, app_url, user_data):
        created_user_response = requests.post(f"{app_url}/api/users/", json=user_data)
        assert created_user_response.status_code == HTTPStatus.CREATED
        created_user_data = created_user_response.json()
        assert created_user_data["email"] == user_data["email"]
        assert created_user_data["first_name"] == user_data["first_name"]
        assert created_user_data["last_name"] == user_data["last_name"]
        assert created_user_data["avatar"] == user_data["avatar"]

    def test_update_user(self, app_url, create_user):
        user_id = create_user
        update_data = dict(first_name="PATCH1", last_name="METHOD")

        update_data_response = requests.patch(f"{app_url}/api/users/{user_id}", json=update_data)
        assert update_data_response.status_code == HTTPStatus.OK

        updated_data = update_data_response.json()
        assert updated_data["first_name"] == update_data["first_name"]
        assert updated_data["last_name"] == update_data["last_name"]


    def test_delete_user(self, app_url, create_user):
        user_id = create_user

        delete_response = requests.delete(f"{app_url}/api/users/{user_id}")
        assert delete_response.status_code == HTTPStatus.OK
        assert delete_response.json() == DELETED_MESSAGE

        get_user_response = requests.get(f"{app_url}/api/users/{user_id}")
        assert get_user_response.status_code == HTTPStatus.NOT_FOUND
        assert get_user_response.json() == USER_NOT_FOUND


    def test_get_after_create_and_update(self, app_url, create_user_and_delete):
        user_data = create_user_and_delete
        user_id = user_data["id"]

        get_user_by_id = requests.get(f"{app_url}/api/users/{user_id}")

        assert get_user_by_id.status_code == HTTPStatus.OK

        get_user_data = get_user_by_id.json()

        assert get_user_data["first_name"] == user_data["first_name"]

        user_update_data = dict(email="tobias.funke@reqres.in", first_name="Test", last_name="Funke",
                         avatar="https://reqres.in/img/faces/9-image.jpg")
        update_user_response = requests.patch(f"{app_url}/api/users/{user_id}", json=user_update_data)

        assert update_user_response.status_code == HTTPStatus.OK

        updated_user_response = requests.get(f"{app_url}/api/users/{user_id}")
        updated_data = updated_user_response.json()

        assert update_user_response.status_code == HTTPStatus.OK
        assert updated_data["first_name"] == user_update_data["first_name"]

    def test_method_not_allowed(self, app_url):
        response = requests.put(f"{app_url}/api/users/1")
        assert response.status_code == 405

    def test_delete_nonexistent_user(self, app_url):
        response = requests.delete(f"{app_url}/api/users/99999999")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_nonexistent_user(self, app_url):
        response = requests.patch(f"{app_url}/api/users/99999999", json=dict(first_name="User", last_name="Nonexistent",))
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_missing_field(self, app_url):
        response = requests.post(f"{app_url}/api/users")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_email(self, app_url):
        data = dict(email="tobias.funke", first_name="Test", last_name="Funke",
                         avatar="https://reqres.in/img/faces/9-image.jpg")
        response = requests.post(f"{app_url}/api/users", json=data)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
