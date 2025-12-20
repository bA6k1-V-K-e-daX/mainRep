from fastapi import FastAPI
from app.api.predict import router as predict_router
from app.services.model_loader import ModelLoader
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):

    model_loader = ModelLoader()
    app.state.model = model_loader.get_model()
   
    yield  


app = FastAPI(lifespan=lifespan)
app.include_router(predict_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)