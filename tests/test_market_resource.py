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

    def test_post_invalid_market_price(self):
        # Configure the mock to return an authorized user with the same user_id
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        mock_request_data = {
            'card_id': 1,
            'market_price': -1
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

    def test_patch_withdraw_card(self):
        # Create a dummy user
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
            # Set up the mock session card_id
            session_mock.query().filter_by().first.return_value = user_card

            # Call the post method
            result = self.market_resource.patch(card_id=1)

            # Assert that the result is as expected
            expected_result = {
                'message': 'The card has been withdrawn from sale successfully',
                'owner_id': authorized_user.id,
                'card_id': user_card.id,
            }, 201
            self.assertEqual(result, expected_result)

    # def test_patch_buy_card(self):
    #     # Create a dummy user
    #     authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
    #     self.authorization_helper_mock.authorization.return_value = authorized_user
    #
    #     # Configure the mock to return a user card with the same user_id
    #     user_card = Mock(id=1, user_id=2, market_price=100, on_market=True)
    #
    #     with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
    #         # Set up the mock session card_id
    #
    #         session_mock.query().filter_by(id=user_card.id, on_market=True).first.return_value = user_card
    #
    #         owner = Mock(id=user_card.user_id, role='regular', budget='500', collection_value='500')
    #         buyer = Mock(id=authorized_user.id, role='regular', budget='500', collection_value='500')
    #         session_mock.query().filter_by(id=user_card.user_id).first.return_value = owner
    #         session_mock.query().filter_by(id=authorized_user.id).first.return_value = buyer
    #
    #         # Call the post method
    #         result = self.market_resource.patch(card_id=1)
    #
    #         # Assert that the result is as expected
    #         expected_result = {
    #             'card_id': user_card.id,
    #             'card_name': user_card.name,
    #             'card_age': user_card.age,
    #             'card_skill': user_card.skill,
    #             'market_value': user_card.market_value,
    #             'market_price': user_card.market_price,
    #             'owner_id': user_card.user_id,
    #             'buyer_id': authorized_user.id,
    #             'buyer_budget': authorized_user.budget,
    #             'owner_budget': 400,
    #             'card_on_market': False,
    #             'message': 'Card was bought successfully',
    #         }, 201
    #         self.assertEqual(result, expected_result)

    def test_patch_card_not_found(self):
        # Create a dummy user
        authorized_user = Mock(id=1, role='regular', budget=500, collection_value=500)
        self.authorization_helper_mock.authorization.return_value = authorized_user

        # Configure the mock to return a user card with the same user_id
        user_card = Mock(id=1, user_id=1, market_price=100, on_market=False)
        self.session_mock.query().filter_by().first.return_value = user_card

        with patch.object(self.market_resource, '_MarketResource__session') as session_mock:
            # Set up the mock session card_id
            session_mock.query().filter_by().first.return_value = None

            # Call the post method
            result = self.market_resource.patch(card_id=1)

            # Assert that the result is as expected
            expected_result = {
                'message': 'Card not found or not available for sale.',
            }, 404
            self.assertEqual(result, expected_result)

    def test_check_permission_admin(self):
        # Create a dummy user with admin role
        admin_user = Mock(id=1, role='admin')

        # Create an instance of MarketResource
        market_resource = MarketResource(session=None, authorization_helper=None, predict_price=None)

        # Call check_permission with the admin user and a user_id
        market_resource.check_permission(admin_user, user_id=2)

    def test_check_permission_non_admin(self):
        # Create a dummy user without admin role
        non_admin_user = Mock(id=3, role='regular')

        # Create an instance of MarketResource
        market_resource = MarketResource(session=None, authorization_helper=None, predict_price=None)

        # Call check_permission with the non-admin user and a user_id
        with self.assertRaises(PermissionError):
            market_resource.check_permission(non_admin_user, user_id=4)

    @patch('flask_restful.reqparse.RequestParser')
    def test_get_args(self, mock_request_parser):
        mock_parser_instance = Mock()
        mock_request_parser.return_value = mock_parser_instance
        # Mock the parse_args method
        mock_parser_instance.parse_args.return_value = {
            'card_id': 1,
            'market_price': 100
        }

        # Call the get_args method
        result = self.market_resource.get_args()

        # Assert that the result is as expected
        expected_result = {
            'card_id': 1,
            'market_price': 100
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
