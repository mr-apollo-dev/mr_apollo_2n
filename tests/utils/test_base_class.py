import logging
from io import StringIO

import pytest

from mr_apollo_2n.utils.base_class import BaseClass


@pytest.fixture
def base_instance():
    return BaseClass()


def test_logger_msg(base_instance):
    logger_output = StringIO()
    handler = logging.StreamHandler(logger_output)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # Registra un mensaje de prueba en el logger
    base_instance.logger.debug("This is a test message")

    # Obtiene el registro de salida del logger
    log_output = logger_output.getvalue()

    # Verifica que el nombre del logger sea el nombre de la clase base por
    # defecto
    assert "This is a test message" in log_output

    handler.close()
    logger.removeHandler(handler)
