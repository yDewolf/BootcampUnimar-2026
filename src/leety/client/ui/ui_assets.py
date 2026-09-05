from pathlib import Path
from PIL import Image

from leety.common.utils.path_utils import ROOT_PATH
ASSETS_FOLDER: Path = ROOT_PATH / "assets"
assert ASSETS_FOLDER.exists(), f"A pasta de assets não existe ou o caminho está errado {ASSETS_FOLDER}"

UNIMAR_LOGO_PATH = ASSETS_FOLDER / "unimar_logo.png"
UNIMAR_LOGO = Image.open(UNIMAR_LOGO_PATH)
logo_height = 20
factor = logo_height / UNIMAR_LOGO.size[1]
UNIMAR_LOGO = UNIMAR_LOGO.resize((int(UNIMAR_LOGO.size[0] * factor), logo_height), Image.Resampling.LANCZOS)
