from fastapi import FastAPI


app = FastAPI()

@app.get('/users')
def get_users():
    return "list of users"