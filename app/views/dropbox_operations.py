from urllib.parse import unquote, urlparse
from uuid import UUID, uuid4
import os
import dropbox
from dropbox.exceptions import ApiError

from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError
load_dotenv()

# DropBox credentials из переменных окружения
DROPBOX_APP_KEY = os.getenv('DROPBOX_APP_KEY')
DROPBOX_APP_SECRET = os.getenv('DROPBOX_APP_SECRET')
DROPBOX_REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN')

DROPBOX_FOLDER = '/covers'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
EXTENSION_TO_FORMAT = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "gif": "GIF"}
# Reject decompression bombs before the file is copied to permanent storage.
MAX_IMAGE_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def get_dropbox_client():
    """
    Создаёт клиент DropBox с автообновлением токена
    """
    if DROPBOX_APP_KEY and DROPBOX_APP_SECRET and DROPBOX_REFRESH_TOKEN:
        # Используем refresh token — токен обновится автоматически
        return dropbox.Dropbox(
            oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET
        )
    else:
        return None


def allowed_file(filename):
    """Проверяет расширение файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    """Получает расширение файла"""
    return filename.rsplit('.', 1)[-1].lower()


def _get_dropbox_path(path_or_url):
    """Возвращает путь созданной приложением обложки по пути или публичной ссылке."""
    if not path_or_url:
        return None
    if path_or_url.startswith(f"{DROPBOX_FOLDER}/"):
        return path_or_url

    parsed = urlparse(path_or_url)
    hostname = (parsed.hostname or '').lower()
    if hostname != 'dropbox.com' and not hostname.endswith(('.dropbox.com', '.dropboxusercontent.com')):
        return None

    filename = unquote(parsed.path.rstrip('/').rsplit('/', 1)[-1])
    stem, extension = os.path.splitext(filename)
    if extension.lstrip('.').lower() not in ALLOWED_EXTENSIONS:
        return None
    try:
        UUID(stem)
    except ValueError:
        return None
    return f"{DROPBOX_FOLDER}/{filename}"


def uploadToDropbox(photo):
    """
    Загружает файл в DropBox и возвращает публичную ссылку
    
    Args:
        photo: FileStorage объект из request.files
        
    Returns:
        dict: {'path': '/covers/...', 'url': 'https://...'} или None при ошибке
    """
    if not photo or photo.filename == '':
        return None
    
    # Валидация расширения
    if not allowed_file(photo.filename):
        return None

    try:
        image = Image.open(photo.stream)
        if image.width * image.height > MAX_IMAGE_PIXELS:
            return None
        image.verify()
        if image.format != EXTENSION_TO_FORMAT[get_extension(photo.filename)]:
            return None
        photo.stream.seek(0)
    except (UnidentifiedImageError, DecompressionBombError, OSError, ValueError):
        return None
    
    dbx = get_dropbox_client()
    if not dbx:
        print("ERROR: DropBox credentials не установлены")
        return None
    
    try:
        # Генерируем UUID имя
        uuid = str(uuid4())
        filename = f"{uuid}.{get_extension(photo.filename)}"
        dropbox_path = f"{DROPBOX_FOLDER}/{filename}"
        
        # Читаем содержимое файла
        file_content = photo.read()
        
        # Загружаем в DropBox
        try:
            dbx.files_upload(file_content, dropbox_path, mode=dropbox.files.WriteMode('add'))
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().reason.is_conflict():
                # Если файл уже существует, используем replace
                dbx.files_upload(file_content, dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
            else:
                raise
        
        # Получаем публичную ссылку
        public_url = getPublicLink(dropbox_path)
        if not public_url:
            deleteFromDropbox(dropbox_path)
            return None
        
        # Возвращаем путь и публичную ссылку
        return {
            'path': dropbox_path,
            'url': public_url
        }
        
    except Exception as e:
        print(f"ERROR uploading to DropBox: {str(e)}")
        return None


def deleteFromDropbox(path_or_url):
    """
    Удаляет файл из DropBox
    
    Args:
        path_or_url: Путь файла в DropBox или созданная приложением публичная ссылка
        
    Returns:
        bool: True если успешно, False при ошибке
    """
    dropbox_path = _get_dropbox_path(path_or_url)
    if not dropbox_path:
        return False
    
    dbx = get_dropbox_client()
    if not dbx:
        return False
    
    try:
        dbx.files_delete(dropbox_path)
        return True
    except Exception as e:
        print(f"ERROR deleting from DropBox: {str(e)}")
        return False


def getPublicLink(dropbox_path):
    """
    Получает публичную ссылку на файл в DropBox
    
    Args:
        dropbox_path: Путь файла в DropBox
        
    Returns:
        str: Публичная ссылка или None при ошибке
    """
    if not dropbox_path:
        return None
    
    dbx = get_dropbox_client()
    if not dbx:
        return None
    
    try:
        url = None
        # Пытаемся получить существующую ссылку
        try:
            links = dbx.sharing_list_shared_links(path=dropbox_path)
            if links.links:
                url = links.links[0].url
        except ApiError:
            pass
        
        if not url:
            # Если ссылки нет, создаём новую
            shared_link = dbx.sharing_create_shared_link_with_settings(
                dropbox_path,
                dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
            )
            url = shared_link.url

        # Формируем ссылку для скачивания (заменяем dl=0 на dl=1)
        # DropBox обычно возвращает ссылки вида ...?dl=0
        if '?dl=0' in url:
            return url.replace('?dl=0', '?dl=1')
        elif '?' in url:
            return url + '&dl=1'
        else:
            return url + '?dl=1'
        
    except Exception as e:
        print(f"ERROR getting public link: {str(e)}")
        return None


def downloadFromDropbox(dropbox_path):
    """
    Скачивает файл из DropBox
    
    Args:
        dropbox_path: Путь файла в DropBox
        
    Returns:
        bytes: Содержимое файла или None при ошибке
    """
    if not dropbox_path:
        return None
    
    dbx = get_dropbox_client()
    if not dbx:
        return None
    
    try:
        metadata, response = dbx.files_download(dropbox_path)
        return response.content
        
    except Exception as e:
        print(f"ERROR downloading from DropBox: {str(e)}")
        return None
