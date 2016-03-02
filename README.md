# ExcludeMyIP
A Google Analytics tool to exclude your own (home/work) IP. See it live at
www.excludemyip.com. The source code of this project may also serve as a good
starting point for creating your own web application utilizing Google APIs.

## Development
To run this web application locally on your computer, all you need is Python
2.7.x where `x >= 10`, and [virtualenv]
(http://docs.python-guide.org/en/latest/dev/virtualenvs/). In theory, the 
following commands should then allow you to run the development version of the
application on `http://localhost:8000`:

```bash
# Clone the git repository:
git clone https://github.com/mherrmann/ExcludeMyIP.git
cd ExcludeMyIP/
# Create virtual environment in venv/ (ensure `python` is Python 2.7 not 3.x):
python -m virtualenv venv
# Activate virtual environment:
source venv/bin/activate
# Install dependencies:
pip install -r requirements.txt
# Initialize database for Django (not that it is actually used):
python manage.py migrate
# Run server:
python manage.py runserver
```

To really interface with the Google APIs, you also need to generate and place
a file `google_api_credentials.json` into the `public/` directory of this app.
To do this, follow these steps:

1. Create a new project in the [Google Developer Console]
(https://console.developers.google.com).
2. Enable the Google Analytics API for that project.
3. When the Developer Console asks you whether you want to create credentials
for the API, click yes and say you want to create credentials for a web server.
4. On the screen that lets you create an *OAuth 2.0 client ID*, add
`http://localhost:8000/install/callback` as an *Authorized redirect URI*.
5. The same screen lets you download the credentials as JSON (`client_id.json`).
Place this file in `public/google_api_credentials.json`.

When you now run `python manage.py runserver` and go to `http://localhost:8000`
(not `http://127.0.0.1:8000`!) you should also be able to use the entire Google
Analytics-related functionality of this web application.

## Deployment
This web application can be deployed on a bare Ubuntu 14.04 installation
by copying the script `bin/install.sh` to the server and executing it as root.
You will need to edit the global variables defined at the top of the script
to match your environment. Please also note that the current configuration
throughout the code base assumes that the server runs on domain
`www.excludemyip.com`. If you want to run it on a different domain, you need
to replace all occurrences of `excludemyip.com` in the code base with your
domain.