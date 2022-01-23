# JLBankingAPI

JLBankingAPI is an API made with [Django Framework](https://www.django-rest-framework.org/) and [Django REST Framework](https://www.django-rest-framework.org/) that tries to simulate the functionality of a simple bank webservice: create and delete accounts with email verification, make and get transactions from a user.

# Installation

To run this project after you downloaded it you have to follow this steps:

1. You need to have installed python on your computer.
2. You need to have installed pip package manager.
3. Run the following command to install necessary python packages 
>pip install -r requirements.txt
5. You have to modify the email account from which the verifications emails are sent (it is configured with my own Google email account for testing. I hide my password with an environment variable for obvious reasons.). In order to do so go to `/JLBanking_api/my_api/settings.py` and change the following lines with your Gmail account credentials:
> -`EMAIL_HOST_USER = 'your_email@gmail.com'`<br/>-`EMAIL_HOST_PASSWORD = 'your_password'`<br/> -`DEFAULT_FROM_EMAIL = 'JLBankingAPI<your_email@gmail.com>'`
6. Run the following command to make an initial setup
>python manage.py makemigrations && python manage.py migrate
7. Standing on `/JLBanking_api/my_api` run the server with the following command
>python manage.py runserver
