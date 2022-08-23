from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Image Optimisation"
    image_path: str = "images"
    items_per_user: int = 50


settings = Settings()