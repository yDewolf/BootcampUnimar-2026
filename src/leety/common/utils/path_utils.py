import sys
from pathlib import Path
import leety.common as common

ROOT_PATH = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent.parent.parent.parent
SRC_PATH = Path(common.__file__).resolve().parent.parent.parent
pass