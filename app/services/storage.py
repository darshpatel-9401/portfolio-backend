"""Storage abstraction: today files go to a local folder. To use S3 / Cloudinary later,
write another class with save() and delete(), and return it from get_storage()."""
import os
import uuid

from app.config import Config


class LocalStorage:
    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def save(self, data, extension):
        filename = f"{uuid.uuid4().hex}{extension}"
        with open(os.path.join(self.folder, filename), "wb") as f:
            f.write(data)
        return filename, f"/uploads/{filename}"

    def delete(self, filename):
        path = os.path.join(self.folder, os.path.basename(filename))
        if os.path.exists(path):
            os.remove(path)


def get_storage():
    return LocalStorage(Config.UPLOAD_DIR)
