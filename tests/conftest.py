import pytest
from scripts.build_adapters import build
from scripts.package_release import package


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    return build(tmp_path_factory.mktemp("adapter-parent") / "generated")


@pytest.fixture(scope="session")
def release(tmp_path_factory):
    return package(tmp_path_factory.mktemp("release-parent") / "generated")
