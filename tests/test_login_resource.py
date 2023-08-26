import unittest
from unittest.mock import Mock, patch
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
