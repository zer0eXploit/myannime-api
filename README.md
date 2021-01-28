# Introduction

- This is a backend API for [(မြန်နီမေး) MyanNime](https://myanime-d5de4.web.app/).
- Frontend source code can be found [here](https://github.com/zer0eXploit/myannime).
- This API deals with anime information management and user management.
- This API backs the frontend with its necessities such as: user registration, authentication, password resets etc,.
- Authentication is done via JWTs.
- Database used is PostgreSQL.

# API Docs

The full documentation of the API is available at the followig url:

- [MyanNime API Docs](https://documenter.getpostman.com/view/8103362/TW6tMAB1)

## Running the server

Prerequisites:

- Please create an .env file with entires as in the .env.example file.
- Install required dependencies.

```
cmd: python3 -m venv your_venv # virturl env creation
cmd: source your_venv/bin/activate  # activating the venv
cmd: (your_venv) pip install requirements.txt
cmd: (your_venv) python app.py
```

## License

- MIT
