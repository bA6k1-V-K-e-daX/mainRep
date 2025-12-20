from pydantic_settings import BaseSettings  # или BaseSettings из pydantic v1/v2

class Settings(BaseSettings):
    PROJECT_NAME: str = "My ML API"
    MODEL_PATH: str = "models/my_model.pkl"
    API_V1_STR: str = "/api/v1"
    
    # Можно читать из .env
    class Config:
        env_file = ".env"

settings = Settings()