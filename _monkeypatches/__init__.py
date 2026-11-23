
import importlib
import pkgutil
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).parents[1].resolve()
ODOO_ROOT = ROOT / ".odoo"


if str(ODOO_ROOT) not in sys.path:
    sys.path.insert(0, str(ODOO_ROOT))


class PatchImportHook:
    """Register hooks that are run on import."""

    def __init__(self):
        self.hooks = set()

    def add_hook(self, fullname: str) -> None:
        """Register a hook after a module is loaded.
        If already loaded, run hook immediately."""
        self.hooks.add(fullname)
        if fullname in sys.modules:
            print(fullname)
            patch_module(fullname)

    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.hooks:
            return None  # let python use another import hook to import this fullname

        # skip all finders before this one
        idx = sys.meta_path.index(self)
        for finder in sys.meta_path[idx + 1:]:
            spec = finder.find_spec(fullname, path, target)
            if spec is not None:
                # we found a spec, change the loader

                def exec_module(module: ModuleType, exec_module=(
                        spec.loader.exec_module
                        if spec.loader
                        else lambda mod: None
                    )) -> None:
                    exec_module(module)
                    patch_module(module.__name__)

                spec.loader = SimpleNamespace(
                    create_module=(
                        spec.loader.create_module
                        if spec.loader
                        else lambda spec: None
                    ),
                    exec_module=exec_module
                )
                return spec
        raise ImportError(f"Could not load the module {fullname!r} to patch")


HOOK_IMPORT = PatchImportHook()
sys.meta_path.insert(0, HOOK_IMPORT)


def patch_init() -> None:
    for submodule in pkgutil.iter_modules(__path__):
        if not submodule.name.startswith('_'):
            HOOK_IMPORT.add_hook(submodule.name)


def patch_module(name: str) -> None:
    module = importlib.import_module(f'.{name}', __name__)
    module.patch_module()
