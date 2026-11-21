
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1].resolve()
ODOO_ROOT = ROOT / ".odoo"

if str(ODOO_ROOT) not in sys.path:
    sys.path.insert(0, str(ODOO_ROOT))

def patch_init() -> None:
    for submodule in pkgutil.iter_modules(__path__):
        print(submodule)