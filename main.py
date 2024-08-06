from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth, todos, users  
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/auth/")
