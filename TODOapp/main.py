
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from .database import engine, Base
from .routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles


app = FastAPI()

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="TODOapp/static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


@app.get("/")
def test():
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="/static/favicon.svg")


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}
