import unittest
from unittest import TestCase, mock
from unittest.mock import Mock, patch, MagicMock

from exceptions.authorization_exception import AuthorizationException
from exceptions.card_exception import CardException
from resources import UserResource


class TestUserResource(TestCase):
    def setUp(self):
        self.session_mock = Mock()
        self.authorization_helper_mock = Mock()
        self.user_resource = UserResource(self.session_mock, self.authorization_helper_mock)

    def test_post_success(self):
        mock_parsed_args = {'username': 'test_user', 'email': 'test@gmail.com', 'password': 'test_password',
                            'country': 'USA', 'role': 'regular'}
        mock_player_cards = [{'name': 'L. Foster', 'age': '22', 'skill': '10'}]
        # Mock the get_args method
        with patch.object(self.user_resource, 'get_args', return_value=mock_parsed_args):
            # Mock the required methods for post method
            with patch.object(self.user_resource, 'hash_password', return_value='hashed_password'), \
                    patch.object(self.user_resource, 'generate_player_cards', return_value=mock_player_cards), \
                    patch.object(self.user_resource, 'is_new_user_validation'), \
                    patch.object(self.user_resource, 'role_validation'):
                # Mock the session context using a context manager
                with patch.object(self.user_resource, '_UserResource__session') as session_mock:
                    # Call the post method
                    result = self.user_resource.post()

        # Assert the result
        expected_result = {'message': 'User registered successfully', 'user_id': None}, 201
        self.assertEqual(result, expected_result)

    @patch('resources.user_resource.asyncio.run')
    def test_post_generate_player_cards_exception(self, mock_run):
        mock_run.side_effect = CardException('Get Players API returns error')

        mock_parsed_args = {'username': 'test_user', 'email': 'test@gmail.com', 'password': 'test_password',
                            'country': 'USA', 'role': 'regular'}

        # Mock the get_args method
        with patch.object(self.user_resource, 'get_args', return_value=mock_parsed_args):
            # Mock the required methods for post method
            with patch.object(self.user_resource, 'hash_password', return_value='hashed_password'), \
                    patch.object(self.user_resource, 'is_new_user_validation'), \
                    patch.object(self.user_resource, 'role_validation'):
                # Mock the session context using a context manager
                with patch.object(self.user_resource, '_UserResource__session') as session_mock:
                    # Call the post method and catch the result
                    result = self.user_resource.post()

        # Assert that the returned result matches the expected response for CardException
        expected_result = {'error': 'Get Players API returns error'}, 401
        self.assertEqual(result, expected_result)

    def test_post_email_not_valid_exception(self):
        mock_parsed_args = {'email': ''}

        # Mock the get_args method
        with patch.object(self.user_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.user_resource, '_UserResource__session') as session_mock:
                # Call the post method and catch the result
                result = self.user_resource.post()

        # Assert that the returned result matches the expected response for CardException
        expected_result = {'error': 'The email address is not valid. It must have exactly '
                                    'one @-sign.'}, 400
        self.assertEqual(result, expected_result)

    def test_get_authorization_failed(self):
        self.authorization_helper_mock.authorization.side_effect = AuthorizationException('Authorization failed')

        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Call the delete method and catch the result
            result = self.user_resource.get()

        # Assert that the returned result matches the expected response for AuthorizationException
        expected_result = {'error': 'Authorization failed'}, 401
        self.assertEqual(result, expected_result)

    def test_get_permission_error(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(role='regular', id=1)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Mock the session
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Set up the mock session behavior
            mock_session = session_mock.return_value
            mock_session.query().filter_by().first.return_value = authorized_user  # Mock user exists

            # Call the delete method and catch the result
            result = self.user_resource.get()

        # Assert that the result matches the expected response for successful deletion
        expected_result = {'error': 'Forbidden'}, 403
        self.assertEqual(result, expected_result)

    def test_get_success(self):
        # Mock the authorization helper to return an authorized user
        mock_authorized_user = Mock(id=1, role='admin')
        self.authorization_helper_mock.authorization.return_value = mock_authorized_user

        # Mock the session
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Mock the user data
            mock_user_data = Mock(id=2, username='username', email='email@example.com', country='country',
                                  role='regular', budget=500)

            # Mock the request parameters
            with patch.object(self.user_resource, 'get_user_by_id', return_value=mock_user_data):
                # Mock the user cards query
                mock_user_cards = [
                    Mock(market_value=100),
                    Mock(market_value=200)
                ]

                session_mock.query().filter_by().all.return_value = mock_user_cards

                # Mock the sum function to calculate the collection value
                with patch('resources.user_resource.sum', return_value=sum(card.market_value for card in mock_user_cards)):
                    # Call the get method
                    result = self.user_resource.get(2)

        # Assert the result
        expected_result = [{
            "id": 2,
            "username": "username",
            "email": "email@example.com",
            "country": "country",
            "role": "regular",
            "budget": 500,
            "collection_value": 300
        }], 200

        self.assertEqual(result, expected_result)

    def test_patch_authorization_failed(self):
        self.authorization_helper_mock.authorization.side_effect = AuthorizationException('Authorization failed')

        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Call the delete method and catch the result
            result = self.user_resource.patch(1)

        # Assert that the returned result matches the expected response for AuthorizationException
        expected_result = {'error': 'Authorization failed'}, 401
        self.assertEqual(result, expected_result)

    def test_patch_permission_error(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(role='regular', id=1)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Mock the session
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Set up the mock session behavior
            mock_session = session_mock.return_value
            mock_session.query().filter_by().first.return_value = authorized_user  # Mock user exists

            # Call the delete method and catch the result
            result = self.user_resource.patch(2)

        # Assert that the result matches the expected response for successful deletion
        expected_result = {'error': 'Forbidden'}, 403
        self.assertEqual(result, expected_result)

    def test_patch_not_found(self):
        # Mock the authorization helper to return an authorized user
        mock_authorized_user = Mock(id=1, role='admin')
        self.authorization_helper_mock.authorization.return_value = mock_authorized_user

        # Mock the session to return None, simulating user not found
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            session_mock.query().filter_by().first.return_value = None

            # Call the patch method and catch the result
            result = self.user_resource.patch(1)

        # Assert the result for NotFoundException
        expected_result = {'error': 'No user found'}, 404
        self.assertEqual(result, expected_result)

    def test_patch_success(self):
        # Mock the authorization helper to return an authorized user
        mock_authorized_user = Mock(id=1, role='admin')
        self.authorization_helper_mock.authorization.return_value = mock_authorized_user

        # Mock the session
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Mock the user data
            mock_user_data = Mock(id=1, username='old_username', country='old_country')
            session_mock.query().filter_by().first.return_value = mock_user_data

            # Mock the request parameters
            mock_parsed_args = {'username': 'new_username', 'country': 'new_country'}
            with patch.object(self.user_resource, 'get_args', return_value=mock_parsed_args):
                # Call the patch method
                result = self.user_resource.patch(1)

        # Assert the result
        expected_result = {'message': 'User updated successfully'}, 201
        self.assertEqual(result, expected_result)

        # Assert that user data was updated
        self.assertEqual(mock_user_data.username, 'new_username')
        self.assertEqual(mock_user_data.country, 'new_country')

    def test_delete_authorization_failed(self):
        self.authorization_helper_mock.authorization.side_effect = AuthorizationException('Authorization failed')

        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Call the delete method and catch the result
            result = self.user_resource.delete(1)

        # Assert that the returned result matches the expected response for AuthorizationException
        expected_result = {'error': 'Authorization failed'}, 401
        self.assertEqual(result, expected_result)

    def test_delete_permission_error(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(role='regular', id=1)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Mock the session
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Set up the mock session behavior
            mock_session = session_mock.return_value
            mock_session.query().filter_by().first.return_value = authorized_user  # Mock user exists

            # Call the delete method and catch the result
            result = self.user_resource.delete(2)

        # Assert that the result matches the expected response for successful deletion
        expected_result = {'error': 'Forbidden'}, 403
        self.assertEqual(result, expected_result)

    def test_delete_success(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(role='regular', id=1)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Mock the session
        with patch.object(self.user_resource, '_UserResource__session') as session_mock:
            # Set up the mock session behavior
            mock_session = session_mock.return_value
            mock_session.query().filter_by().first.return_value = authorized_user  # Mock user exists

            # Call the delete method and catch the result
            result = self.user_resource.delete(1)

        # Assert that the result matches the expected response for successful deletion
        expected_result = {'message': 'User deleted successfully'}, 201
        self.assertEqual(result, expected_result)

    @patch('flask_restful.reqparse.RequestParser')
    def test_get_args_with_required(self, mock_request_parser):
        mock_parser_instance = MagicMock()
        mock_request_parser.return_value = mock_parser_instance

        mock_parsed_args = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'test_password',
            'country': 'USA',
            'role': 'regular'
        }
        mock_parser_instance.parse_args.return_value = mock_parsed_args

        args = self.user_resource.get_args(True)

        self.assertEqual(args['username'], 'test_user')
        self.assertEqual(args['email'], 'test@example.com')
        self.assertEqual(args['password'], 'test_password')
        self.assertEqual(args['country'], 'USA')
        self.assertEqual(args['role'], 'regular')

    def test_role_validation(self):
        self.assertRaises(Exception, self.user_resource.role_validation, 'invalid_role')

    def test_is_new_user_validation(self):
        self.session_mock.query().filter().first.return_value = Mock()
        self.assertRaises(Exception, self.user_resource.is_new_user_validation, 'test@example.com')

    @patch('models.user.User')
    def test_get_user_by_id(self, user_mock):
        self.session_mock.query().filter_by().first.return_value = user_mock
        user = self.user_resource.get_user_by_id(1)
        self.assertEqual(user, user_mock)

    def test_hash_password(self):
        hashed_password = self.user_resource.hash_password('password')
        self.assertTrue(isinstance(hashed_password, str))


if __name__ == '__main__':
    unittest.main()
