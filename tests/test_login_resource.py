import unittest
from unittest.mock import Mock, patch

from sqlalchemy.exc import DataError

from resources.login_resource import LoginResource
from itsdangerous import URLSafeTimedSerializer


class TestLoginResource(unittest.TestCase):
    def setUp(self):
        self.session_mock = Mock()
        self.login_resource = LoginResource(self.session_mock)

    def test_post(self):
        mock_parsed_args = {'email': 'test@example.com', 'password': 'test_password'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                mock_user_data = Mock(id=2, username='username', email='email@example.com', country='country',
                                      role='regular', budget=500, collection_value=500)

                session_mock.query().filter_by().first.return_value = mock_user_data

                with patch('bcrypt.checkpw', return_value=True):
                    with patch.object(URLSafeTimedSerializer, 'dumps', return_value='mocked_token'):
                        result = self.login_resource.post()

                expected_result = {
                    'message': 'success',
                    'token': 'mocked_token'
                }, 201

                self.assertEqual(result, expected_result)

    def test_post_user_not_found(self):
        mock_parsed_args = {'email': 'usernotexist@mail.com', 'password': 'test_password'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                session_mock.query().filter_by().first.return_value = None

                with patch('bcrypt.checkpw', return_value=False):
                    result = self.login_resource.post()

                    expected_result = {'error': 'Forbidden'}, 404

                    self.assertEqual(result, expected_result)

    def test_missing_email(self):
        # Test case for missing email in request
        mock_parsed_args = {'password': 'test_password'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                result = self.login_resource.post()

                expected_result = {'error': "'email'"}, 400

                self.assertEqual(result, expected_result)

    def test_missing_password(self):
        # Test case for missing password in request
        mock_parsed_args = {'email': 'test@example.com'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                result = self.login_resource.post()

                expected_result = {'error': "'password'"}, 400

                self.assertEqual(result, expected_result)

    def test_invalid_email_format(self):
        # Test case for invalid email format
        mock_parsed_args = {'email': 'invalid_email', 'password': 'test_password'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                with patch('bcrypt.checkpw', return_value=False):
                    result = self.login_resource.post()

                    expected_result = {'error': 'Forbidden'}, 404

                    self.assertEqual(result, expected_result)

    def test_invalid_password(self):
        # Test case for invalid password
        mock_parsed_args = {'email': 'test@example.com', 'password': 'wrong_password'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                mock_user_data = Mock(id=2, username='username', email='email@example.com', country='country',
                                      role='regular', budget=500, collection_value=500)
                session_mock.query().filter_by().first.return_value = mock_user_data

                with patch('bcrypt.checkpw', return_value=False):
                    result = self.login_resource.post()

                    expected_result = {'error': 'Forbidden'}, 404

                    self.assertEqual(result, expected_result)

    def test_data_error_exception(self):
        # Test case for DataError exception
        mock_parsed_args = {'email': 'test@example.com', 'password': 'test_password'}

        with patch.object(self.login_resource, 'get_args', return_value=mock_parsed_args):
            with patch.object(self.login_resource, '_LoginResource__session') as session_mock:
                session_mock.query().filter_by().first.side_effect = DataError("Database error", {}, None)

                with patch('bcrypt.checkpw', return_value=False):
                    result = self.login_resource.post()

                    expected_result = {'error': 'Forbidden'}, 404

                    self.assertEqual(result, expected_result)

    @patch('flask_restful.reqparse.RequestParser')
    def test_get_args(self, mock_request_parser):
        mock_parser_instance = Mock()
        mock_request_parser.return_value = mock_parser_instance

        mock_parsed_args = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        mock_parser_instance.parse_args.return_value = mock_parsed_args

        args = self.login_resource.get_args()

        self.assertEqual(args['email'], 'test@example.com')
        self.assertEqual(args['password'], 'test_password')


if __name__ == '__main__':
    unittest.main()
