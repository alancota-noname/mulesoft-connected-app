import logging

from rich.logging import RichHandler


def config_logger(log_level: int) -> logging.Logger:
	# Create a logger
	logger = logging.getLogger()
	logger.setLevel(log_level)

	# Create a stream handler (console handler) and set the log level
	stream_handler = RichHandler()

	# Create a formatter
	formatter = logging.Formatter("%(message)s")

	# Set the formatter to the stream handler
	stream_handler.setFormatter(formatter)

	# Add the stream handler to the logger
	logger.addHandler(stream_handler)
	stream_handler.setLevel(log_level)

	return logger
