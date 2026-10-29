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


    def test_info_message_is_emitted_once_with_expected_format(self):
        """Repeated setup should not duplicate INFO output."""
        import io
        from unittest.mock import patch

        name = "neo_screener.test_logging.single_message"
        logger = logging.getLogger(name)
        stream = io.StringIO()
        try:
            with patch("sys.stdout", stream):
                first = setup_logger(name)
                second = setup_logger(name)
                self.assertIs(first, second)
                logger.info("logger smoke check")

            output = stream.getvalue()
            self.assertEqual(output.count("logger smoke check"), 1)
            self.assertIn("INFO - logger smoke check", output)
            self.assertEqual(logger.level, logging.INFO)
        finally:
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
                handler.close()


    def test_does_not_forward_records_to_root_logger(self):
        """A configured root logger must not duplicate application messages."""
        import io
        from unittest.mock import patch

        name = "neo_screener.test_logging.no_root_propagation"
        logger = logging.getLogger(name)
        local_output = io.StringIO()
        root_output = io.StringIO()
        root_handler = logging.StreamHandler(root_output)
        try:
            with patch("sys.stdout", local_output), patch.object(
                logging.getLogger(), "handlers", [root_handler]
            ):
                setup_logger(name)
                logger.info("single output")

            self.assertEqual(local_output.getvalue().count("single output"), 1)
            self.assertEqual(root_output.getvalue(), "")
            self.assertFalse(logger.propagate)
        finally:
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
                handler.close()
            root_handler.close()


if __name__ == "__main__":
    unittest.main()
