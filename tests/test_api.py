import json
from http import HTTPStatus

import pytest
import requests
from app.models.User import User


@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("../users.json") as f:
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

    def test_get_after_create_and_update(self, app_url, create_user):
        # user_data = dict(email="tobias.funke@reqres.in", first_name="Tobias", last_name="Funke",
        #                  avatar="https://reqres.in/img/faces/9-image.jpg")
        #
        # create_user_response = requests.post(f"{app_url}/api/users/", json=user_data)
        #
        # assert create_user_response.status_code == HTTPStatus.CREATED
        #
        # user_id = create_user_response.json()["id"]

        user_data = create_user

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


