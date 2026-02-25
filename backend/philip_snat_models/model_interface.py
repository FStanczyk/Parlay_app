from abc import ABC, abstractmethod


class AiModelInterface(ABC):

    LEAGUE_NAME: str

    @abstractmethod
    def update_games(self):
        pass

    @abstractmethod
    def download_new_games(self):
        pass

    @abstractmethod
    def predict(self):
        pass
