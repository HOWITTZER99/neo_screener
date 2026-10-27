"""Dependency-free tests for logger initialization."""

import logging
import unittest

from src.utils.logging import setup_logger


class TestSetupLogger(unittest.TestCase):
    def test_reuses_existing_handler(self):
        name = "neo_screener.test_logging.reuses_handler"
        logger = logging.getLogger(name)
        try:
            first = setup_logger(name)
            second = setup_logger(name)
            self.assertIs(first, second)
            self.assertEqual(len(logger.handlers), 1)
            self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        finally:
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
                handler.close()


if __name__ == "__main__":
    unittest.main()
