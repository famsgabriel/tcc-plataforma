import socket

import pytest


def pytest_collection_modifyitems(items):  # sem servidor carla pula inegracao
    try:
        socket.create_connection(("localhost", 2000), timeout=1.0).close()
    except OSError:
        for item in (i for i in items if "integracao" in str(i.fspath)):
            item.add_marker(pytest.mark.skip(reason="servidor carla não responde em localhost:2000"))
