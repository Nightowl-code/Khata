# KhataApp

KhataApp is a Django-based ledger application designed to help users manage their financial transactions. This application provides a simple and efficient way to keep track of credits and debits, making it ideal for personal or small business accounting.

## Features

- **User Authentication**: Secure login and registration with Django's built-in authentication system.
- **Transaction Management**: Add, edit, and delete credit/debit transactions.
- **Customer Management**: Keep track of customers and their associated transactions.
- **Reports**: Generate detailed reports to analyze financial data.
- **Export Data**: Export transaction records in various formats (CSV, PDF, etc.).
- **Responsive Design**: User-friendly interface optimized for both desktop and mobile devices.

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML, CSS, JavaScript (with Django templates)
- **Database**: SQLite (default), PostgreSQL, or MySQL
- **Authentication**: Django's built-in authentication system
- **Deployment**: Docker, AWS, Heroku


## Installation

To use KhataApp, follow these steps:

1. Clone this repository to your local machine.
2. Create and activate virtual environemt. 
3. Install the required dependencies by running `pip install -r requirements. txt`.
4. Create a superuser by running `python manage.py createsuperuser`
4. Start the app by running `python manage.py runserver`.

## Usage

Once the app is running, you can access it through your web browser at `http://127.0.0.1:8000/`. From there, you can create an account, log in, and start managing your finances.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
