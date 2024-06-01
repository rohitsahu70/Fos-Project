# FOS DataBase Server

This is a server to Tag, Manage, and Analyze FOS Data.

## Getting Started

### Installing

Follow these steps to properly install your project:

1. **Clone the repository:**
  ```
   git clone https://github.com/hawkmeasurment/fos_database_server.git
   cd yourrepository
  ```
Setup virtual environments:
  ```
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
  ```
Install required packages:
  ```
   pip install -r requirements.txt
  ```

Configure Django settings:
Ensure you have PostgreSQL installed and ready on your machine.

Configure database settings in your settings.py:
  ```
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'yourdbname',
           'USER': 'yourdbuser',
           'PASSWORD': 'yourdbpassword',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
  ```
Configure where the data is stored:
  ```
   DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
   MEDIA_URL = '/rawdata/'
   MEDIA_ROOT = BASE_DIR / 'rawdata'
  ```
Configure admin approval email and new user activation link expiry:
  ```
ACCOUNT_ACTIVATION_DAYS = 7 
DEFAULT_ADMIN_EMAIL = 'haig.parseghian@hawk.com.au'
  ```
Configure email service:
  ```
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
    EMAIL_PORT = '2525'
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'User'
    EMAIL_HOST_PASSWORD = 'password'
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
  ```
Run migrations:
  ```
python3 manage.py migrate
  ```
Create a superuser:
  ```
python3 manage.py createsuperuser
  ```
Execute the program:
  ```
    python3 manage.py runserver
  ```
Test the application:
    Access the application through the web browser at http://localhost:8000/.

Authors

    Haig Parseghian

Contributors

    Rohit Sahu
    Arkit Patel
