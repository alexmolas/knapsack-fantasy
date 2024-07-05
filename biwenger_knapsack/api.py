import requests

BASE_PATH = "https://cf.biwenger.com/api/v2/"


class APIHandler:
    def __init__(self, base_path: str = BASE_PATH):
        self.base_path = base_path

    def get_players_info(self, competition: str = "la-liga", score: int = 5, **kwargs):
        data = self.get_all_data(competition=competition, score=score, **kwargs)
        return data["data"]["players"]

    def get_all_data(self, competition: str = "la-liga", score: int = 5, **kwargs):
        parsed_kwargs = "&".join([f"{k}={v}" for k, v in kwargs.items()])
        data = requests.get(
            f"{self.base_path}/competitions/{competition}/data?score={score}/{parsed_kwargs}"
        ).json()
        return data
