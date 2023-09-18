# Collectable Player Cards API

This is a REST API for managing a collection of collectable player cards.
Users can create accounts, log in, and perform various actions related to player cards.
The project is developed using a Flask, and it follows the separation of concerns principles by defining different
packages for each logic layer of the application architecture.

## Functional Requirements

### User Management

- Users can create an account.
- Users can log in.
- Authentication is required for most endpoints (except login and register).

### User Roles

- Two user roles are implemented: **regular** and **admin**.
- Regular can CRUD on their owned records.
- Admins can CRUD all records and users, including other admins.

### User Collections

- Each user can have only one collection of player cards (identified by an email).
- When a user signs up, they receive a collection of 5 cards generated automatically.

### Player Cards

- Player card details (name, age, skill level, market value) are generated using a 3rd party API asynchronously.
- Each player card has an initial value of 100 coins.
- Each player has a budget of 500 coins to buy other cards.

### User Profile

- When logged in, users can view their information:
    - Username and country (editable)
    - Collection value (sum of player card values)

### Exchange Market

- Users can add their cards to an internal exchange market.
- When placing a card on the market, users set the asking price/value.
- The value is listed on the market and can be bought by other users.
- Each user can view all cards from the exchange market.

### Budget Updates

- Collection budgets are updated with each buy/sell transaction.
- When a card is bought by another player, its value is increased based on a machine learning algorithm.

### Data Persistence

- Data is persisted using a MySQL database

### Pagination

- The API will return all the info in the JSON format
- The API supports pagination for all endpoints returning lists of elements.

### Testing

- Use REST clients like Postman, cURL, etc., to test the API.
- Write unit tests (not integration tests) to achieve at least 50% code coverage.
- Use mocks for external dependencies.

## API Endpoints

- **POST /user**: Create a new user account.
- **POST /login**: Log in as a user.
- **GET /user**: Get all users (_only admin can get all users_).
- **GET /user/{user_id}**: Get user profile information (_Admin can get any user, regular user can get only himself_).
- **PATCH /user/{user_id}**: Update user information (_Admin can update any user, regular user can update only himself
  username and country can be updated_).
- **DELTE /user/{user_id}**: Delete a user (_Admin can delete any user, regular user can delete only himself_)
- **GET /market**: Get a list of cards in the exchange market.
- **GET /market/{card_id}**: Get a card in the exchange market.
- **POST /market**: Place a card on the exchange market.
- **PATCH /market/{card_id}**: Buy a card on the market or withdraw card from market.

## API Documentation

For detailed API documentation, including sample requests and responses for each endpoint, please refer to
our [API Documentation](https://documenter.getpostman.com/view/235086/2s9YC5xXaB).

## Usage

1. Clone the repository.
2. Set up a virtual environment (venv or pipenv).
3. Install the required dependencies.
4. Configure the database settings.
5. Run the application.
6. Use REST clients to interact with the API.
7. Write and run unit tests to ensure proper functionality.

## Data Models

### User

- Properties:
    - `id`: Unique identifier for the user.
    - `username`: User's username.
    - `email`: User's email address (used for identification).
    - `password`: User's hashed password.
    - `role`: User's role (regular user or admin).
    - `country`: User's country.
    - `budget`: User's budget.

### Card

- Properties:
    - `id`: Unique identifier for the card.
    - `name`: Name of the card.
    - `age`: Age of the card.
    - `skill`: Skill level of the card.
    - `market_value`: Market value of the player card.
    - `user_id`: ID of the user who owns the card.

### Exchange Market

- Properties:
    - `id`: Unique identifier for the market item.
    - `user_id`: ID of the buyer if the item is sold.
    - `card_id`: ID of the card listed on the market.
    - `price`: Asking price set by the seller.

## Testing

To run unit tests and achieve the desired code coverage, follow these steps:

Run

```
coverage run -m unittest .\tests\test_resources.py
```

Report

```
coverage report -m
```

HTML Report

```
coverage html
```

## Disclaimer

This project is developed for educational purposes and serves as a final project for a lesson or course. It is not
intended for production use and should not be considered a fully functional, real-world application. The features and
functionality provided here are for instructional purposes, and the project may contain limitations, known issues, or
incomplete components.

Please do not use this project in a production environment or with sensitive data. It is recommended to adapt and extend
the codebase for real-world scenarios, security considerations, and performance optimizations before deploying it in any
production setting.

The project's primary purpose is to demonstrate concepts related to REST API development, database integration, user
authentication, and other web development principles. It should be treated as a learning resource rather than a
production-ready solution.

