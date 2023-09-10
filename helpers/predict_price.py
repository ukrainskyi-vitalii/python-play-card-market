from models.card import Card
from sklearn.linear_model import LinearRegression


class PredictPriceHelper:
    def __init__(self, session):
        self.__session = session

    def predict_and_update_prices(self):
        # Load all card data from the database
        cards = self.__session.query(Card).all()

        # Separate features for prediction
        predict_X = [(float(card.age), float(card.skill)) for card in cards]

        # Train a Linear Regression model
        model = LinearRegression()
        model.fit(predict_X, [card.market_value for card in cards])

        # Predict prices for all cards
        predicted_prices = model.predict(predict_X)

        # Update the Card table with the predicted prices
        for card, predicted_price in zip(cards, predicted_prices):
            card.market_value = int(predicted_price)

        # Commit the changes to the database
        self.__session.commit()
