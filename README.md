# Project Guide

This project uses Docker and docker-compose to start-up. To launch navigate to the main directory (click2sureProject) and run:

    docker-compose build
    docker-compose run backend sh -c "python manage.py makemigrations"
    docker-compose run backend sh -c "python manage.py migrate"

this will build the backend and then create all tables required. 

    docker-compose up
This will launch the project and the app should be available on port 5000

## Initialize Users and DB

After project launches visit:

    localhost:5000/transaction/autofill

* This will create 10 users named **_user1_** - **_user10_** 
* user1 will be an admin user while the rest will be regular users
* passwords for all users is '**_click2sure_**'

## How to use API

### Create Users

    post localhost:5000/transaction/register/
    {
        "username": <_username_>,
        "email": <_email_>,
        "password": <_password_>
    }
Success status code **201**

### Create Credit account
    post localhost:5000/transaction/credit/
        {
            'user_id': <_user_id_>
            'max_credit': <_max_credit_>,
            'amount_owed': <_amount_owed_>,
            'balance': <_balance_>
        }
Success status code **201**

* Max credit should be 20000 but can be different
* amount_owed is needed as well as balance
* Balance which will be the difference between Max credit and amount owed

### Create Savings account
    post localhost:5000/transaction/savings/
        {
            'user_id': <_user_id_>
            'balance': <_balance_>
        }
Success status code **201**

### Transactions
    post localhost:5000/transaction/
    {
        "user_id": <user_id>,
        "amount": <int>,
        "type": <type>,
        "source": <source>
    }
Success status code **201**

* user_id is your unique id
* amount is the amount you are transacting for
* type should either "BUY" or "SELL" which is buying or depositing
* source should be either "SAVINGS" or "CREDIT" which is the account you are transacting from

### View transactions
    get localhost:5000/transaction/<pk=id>
Success status code **200**

### View Savings account
    get localhost:5000/transaction/savings/<pk=id>
Success status code **200**

### View Credit account
    get localhost:5000/transaction/credit/<pk=id>
Success status code **200**

The three transactions above use the id to get specific information and is only accessible
to admin users.

### View All accounts and transactions
    get localhost:5000/transaction/view/
Success status code **200**

The above will take the logged in User and display accounts.

First line will be savings account, next will be the Credit account and lastly will be the last 10 transactions

### Update Balances Credit

    put localhost:5000/transaction/credit/<pk=id>
        {
            'max_credit': max_credit,
            'amount_owed': amount_owed,
            'balance': balance
        }
Success status code **202**
### Update Balances Savings

    put localhost:5000/transaction/credit/<pk=id>
        {
            'balance': balance
        }
Success status code **202**
### Get CSV of all accounts, transactions and balances
    get localhost:5000/transaction/csv/

This will get each user and their associated data sorted by user


    