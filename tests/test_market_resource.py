import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

from resources import MarketResource


class TestMarketResource(TestCase):
    def setUp(self):
        self.session_mock = Mock()
        self.authorization_helper_mock = Mock()
        self.predict_price_mock = Mock()

        self.market_resource = MarketResource(self.session_mock, self.authorization_helper_mock,
                                              self.predict_price_mock)

    def test_post(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        mock_request_data = {
            'card_id': 1,
            'market_price': 100
        }

        # Mock the get_args method
        with patch.object(self.market_resource, 'get_args', return_value=mock_request_data):
            # Mock the session context using a context manager
            with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
                # Set up the mock session card_id
                session_mock.query().filter_by().first.return_value = user_card

                # Call the post method
                result = self.market_resource.post()

                # Assert that the result is as expected
                expected_result = {
                    'message': 'Card placed to the market successfully',
                    'card_id': mock_request_data['card_id'],
                    'market_price': mock_request_data['market_price']
                }, 201
                self.assertEqual(result, expected_result)

    def test_post_card_not_found(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        mock_request_data = {
            'card_id': 2,
            'market_price': 100
        }

        # Mock the get_args method
        with patch.object(self.market_resource, 'get_args', return_value=mock_request_data):
            # Mock the session context using a context manager
            with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
                # Set up the mock session card_id
                session_mock.query().filter_by().first.return_value = None

                # Call the post method
                result = self.market_resource.post()

                # Assert that the result is as expected
                expected_result = {
                    'message': 'Card was not found',
                    'card_id': mock_request_data['card_id'],
                    'user_id': authorized_user.id
                }
                self.assertEqual(result, expected_result)

    def test_post_card_validation(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        mock_request_data = {
            'card_id': 'a',
            'market_price': 100
        }

        # Mock the get_args method
        with patch.object(self.market_resource, 'get_args', return_value=mock_request_data):
            # Mock the session context using a context manager
            with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
                # Set up the mock session card_id
                session_mock.query().filter_by().first.return_value = None

                # Call the post method
                result = self.market_resource.post()

                # Assert that the result is as expected
                expected_result = {
                    'error': 'Invalid card_id'
                }, 400
                self.assertEqual(result, expected_result)

    def test_post_market_price_validation(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        mock_request_data = {
            'card_id': 1,
            'market_price': 'a'
        }

        # Mock the get_args method
        with patch.object(self.market_resource, 'get_args', return_value=mock_request_data):
            # Mock the session context using a context manager
            with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
                # Set up the mock session card_id
                session_mock.query().filter_by().first.return_value = None

                # Call the post method
                result = self.market_resource.post()

                # Assert that the result is as expected
                expected_result = {
                    'error': 'Invalid market_price'
                }, 400
                self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
