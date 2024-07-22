import ujson
import uuid
from datetime import datetime


class UserInputPairsManager:
    def __init__(self, module_name):
        self.metadata = {
            "uuid": str(uuid.uuid4()),
            "module_name": module_name,
            "last_saved": None,
            "last_loaded": None,
        }
        self.user_input_pairs = {}

    def set_user_input_pairs(self, user_input_pairs):
        self.user_input_pairs = user_input_pairs

    def save_to_json(self, file_path):
        self.metadata["last_saved"] = str(datetime.now())
        data = {
            "metadata": self.metadata,
            "user_input_pairs": self.user_input_pairs,
        }

        with open(file_path, "w") as file:
            ujson.dump(data, file, indent=4)

    def load_from_json(self, file_path):
        with open(file_path, "r") as file:
            loaded_data = ujson.load(file)

        self.metadata = loaded_data.get("metadata", {})
        self.user_input_pairs = loaded_data.get("user_input_pairs", {})

        self.metadata["last_loaded"] = str(datetime.now())

        with open(file_path, "w") as file:
            ujson.dump(loaded_data, file, indent=4)

        return self.user_input_pairs, self.metadata
