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
    file_url = storage.get_generated_file_url(file_path=file_path, session_id=session_id, task_name=task_name)
    print(f"Resolved local file file_url = {file_url}")
    return file_url


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
    @staticmethod
    def _validate_path(resolved: str, base_dir: str) -> str:
        abs_resolved = os.path.realpath(resolved)
        abs_base = os.path.realpath(base_dir)
        if not abs_resolved.startswith(abs_base + os.sep) and abs_resolved != abs_base:
            raise ValueError(f"Path traversal detected: path escapes {abs_base}")
        return abs_resolved

    def get_data_file_url(self, file_path: str, session_id: str) -> str:
        if file_path.startswith("agent://"):
            filename = file_path.removeprefix("agent://")
            root = self._get_root_folder()
            base_dir = os.path.join(root, session_id, "data")
            resolved = os.path.join(base_dir, filename)
            return self._validate_path(resolved, base_dir)
        else:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found")
            return file_path

    def get_generated_file_url(self, file_path: str, session_id: str, task_name: str = "") -> str:
        if file_path.startswith("agent://"):
            file_path = file_path.removeprefix("agent://")

        root = self._get_root_folder()
        base_dir = os.path.join(root, session_id, "generated", task_name)
        resolved = os.path.join(base_dir, file_path)
        return self._validate_path(resolved, base_dir)

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
