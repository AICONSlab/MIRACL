import ujson
import uuid
from datetime import datetime


class UserInputPairsManager:
    def __init__(self, window_name):
        self.window_name = window_name
        self.unique_id = str(uuid.uuid4())
        self.last_saved = None
        self.last_loaded = None
        self.user_input_pairs = {}

    def set_user_input_pairs(self, user_input_pairs):
        self.user_input_pairs = user_input_pairs

    def save_to_json(self, file_path):
        data = {
            "unique_id": self.unique_id,
            "window_name": self.window_name,
            "last_saved": str(datetime.now()),
            "last_loaded": str(self.last_loaded) if self.last_loaded else None,
            "user_input_pairs": self.user_input_pairs,
        }

        with open(file_path, "w") as file:
            ujson.dump(data, file, indent=4)

        self.last_saved = datetime.now()

    def load_from_json(self, file_path):
        with open(file_path, "r") as file:
            loaded_data = ujson.load(file)

        self.__dict__.update(loaded_data)  # Update instance var

        loaded_data["last_loaded"] = str(datetime.now())

        with open(file_path, "w") as file:
            ujson.dump(loaded_data, file, indent=4)

        return self.user_input_pairs
