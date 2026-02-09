from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    name: str = "John Doe"
    age: int = 30
    email: str = "john.doe@example.com"
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
print(settings.Config);
print(settings.Config.env_file);
print(settings.name)
print(settings.age)
print(settings.email)