from http import HTTPStatus

from fast_api_from_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'Julio',
            'email': 'juliocd.bernardes@gmail.com',
            'password': 'Teste@123',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'Julio',
        'email': 'juliocd.bernardes@gmail.com',
        'id': 1,
    }


def test_create_user_with_existing_username_must_return_400_bad_request(
    client, user
):
    response = client.post(
        '/users/',
        json={
            'username': 'Teste',
            'email': 'juliocd.bernardes@gmail.com',
            'password': 'Teste@123',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_with_existing_email_must_return_400_bad_request(
    client, user
):
    response = client.post(
        '/users/',
        json={
            'username': 'Teste1',
            'email': 'test@test.com',
            'password': 'Teste@123',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_read_user(client, user):
    response = client.get('/user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Teste',
        'email': 'test@test.com',
        'id': 1,
    }


def test_read_user_with_invalid_id_must_return_404(client, user):
    response = client.get('/user/2')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Julio',
            'email': 'julioTeste@gmail.com',
            'password': 'Teste@123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Julio',
        'email': 'julioTeste@gmail.com',
        'id': user.id,
    }


def test_update_integrity_error(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    # Alterando user da fixture para fausto
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


# def test_update_invalid_userID_must_return_404(client, token):
#     response = client.put(
#         '/users/99',
#         json={
#             'username': 'TestInvalidUser',
#             'email': 'test@invalid.com',
#             'password': 'test@123',
#         },
#     )

#     assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


# def test_delete_invalid_userID_must_return_404(client, user, token):
#     response = client.delete(
#         '/users/99',
#         headers={'Authorization': f'Bearer {token}'},
#     )

#     assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
