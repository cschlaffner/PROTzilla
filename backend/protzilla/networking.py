import requests
from pathlib import Path
from backend.protzilla.constants.protzilla_logging import logger


def download_file_from_url(url: str, dest: Path) -> Path | None:
    """
    Download a file from a URL and save it to the specified destination path.

    :param url: The URL of the file to download
    :param dest: The destination path where the file should be saved
    :return: The destination path if successful, None otherwise
    """
    with requests.Session() as session:

        r = session.get(url, timeout=30)
        r.raise_for_status()

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info("Downloaded %s -> %s", url, dest)
        return dest
    except requests.RequestException:
        logger.exception("Failed to download %s", url)
        return None
    except OSError:
        logger.exception("Failed to write file %s", dest)
        return None
