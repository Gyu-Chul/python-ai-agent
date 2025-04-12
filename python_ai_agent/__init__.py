import sys

try:
    from importlib.util import find_spec
except ImportError:
    find_spec = None
from .target_modules import TARGET_MODULES


def load_module(module, fullname):
    print(f"[HOOK] {fullname} 모듈이 실제 import 되었습니다.")
    return module


class _ImportHookLoader(object):
    def load_module(self, fullname):
        module = sys.modules[fullname]
        return load_module(module, fullname)


class _ImportHookChainedLoader(object):
    def __init__(self, loader):
        self.loader = loader

    def load_module(self, fullname):
        module = self.loader.load_module(fullname)
        return load_module(module, fullname)


class ImportFinder(object):

    def __init__(self):
        self._hooks = {}

    def find_module(self, fullname, path=None):

        if fullname not in TARGET_MODULES:
            return None

        if fullname in self._hooks:
            return None
        self._hooks[fullname] = True

        try:
            if find_spec:
                spec = find_spec(fullname, path)
                if spec and spec.loader:
                    return _ImportHookChainedLoader(spec.loader)
                else:
                    __import__(fullname)
                    return _ImportHookLoader()
            else:
                __import__(fullname)
                return _ImportHookLoader()

        except ImportError:
            return None


if not any(isinstance(finder, ImportFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, ImportFinder())
