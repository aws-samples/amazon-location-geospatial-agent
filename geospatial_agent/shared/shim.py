import os
from abc import ABC, abstractmethod

from geospatial_agent.shared.location import get_map_style_uri


def get_shim_imports() -> str:
    shim_map_style_import = f'from {location_map_style.__module__} import {location_map_style.__name__} \n' \
                            f'from {get_data_file_url.__module__} import {get_data_file_url.__name__}\n' \
                            f'from {get_local_file_path.__module__} import {get_local_file_path.__name__}\n'
    return shim_map_style_import


def location_map_style():
    return get_map_style_uri()


LOCAL_STORAGE_MODE = 'local'


def get_data_file_url(file_path: str, session_id: str) -> str:
    if not file_path.startswith("agent://"):
        return file_path

    storage = LocalStorage()
    return storage.get_data_file_url(file_path=file_path, session_id=session_id)


def get_local_file_path(file_path: str, session_id: str, task_name: str = "") -> str:
    storage = LocalStorage()
    return storage.get_generated_file_url(file_path=file_path, session_id=session_id, task_name=task_name)


class Storage(ABC):
    @abstractmethod
    def create_session_storage(self, session_id: str):
        pass

    @abstractmethod
    def get_data_file_url(self, file_path_or_url: str, session_id: str) -> str:
        pass

    @abstractmethod
    def get_generated_file_url(self, file_path_or_url: str, session_id: str, task_name: str = "") -> str:
        pass

    @abstractmethod
    def write_file(self, file_path_or_name: str, session_id: str, task_name="") -> str:
        pass


class LocalStorage(Storage):
    def get_data_file_url(self, file_path: str, session_id: str) -> str:
        if file_path.startswith("agent://"):
            filename = file_path.removeprefix("agent://")
            root = self._get_root_folder()
            return os.path.join(root, session_id, "data", filename)
        else:
            # Check if the file path exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found")
            return file_path

    def get_generated_file_url(self, file_path: str, session_id: str, task_name: str = "") -> str:
        if file_path.startswith("agent://"):
            file_path = file_path.removeprefix("agent://")

        if not os.path.abspath(file_path):
            raise ValueError("Generated file path must be absolute")

        root = self._get_root_folder()

        return os.path.join(root, session_id, "generated", task_name, file_path)

    def write_file(self, file_name: str, session_id: str, task_name="", content="") -> str:
        if content == "":
            raise ValueError("To write a local file, content parameter must be provided")

        file_path = self.get_generated_file_url(
            file_path=file_name, session_id=session_id, task_name=task_name
        )

        parent_dir = os.path.dirname(file_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(file_path, 'w') as file:
            file.write(content)

        return file_path

    def create_session_storage(self, session_id: str):
        root = self._get_root_folder()

        data_folder = os.path.join(root, session_id, "data")
        generated_folder = os.path.join(root, session_id, "generated")

        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        if not os.path.exists(generated_folder):
            os.makedirs(generated_folder)

    @staticmethod
    def _get_root_folder():
        root = os.path.join(os.getcwd(), "geospatial-agent-session-storage")
        return root
