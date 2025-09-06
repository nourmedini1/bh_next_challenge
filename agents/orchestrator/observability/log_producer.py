import datetime
from kafka import KafkaProducer
import json
import logging
import parlant.sdk as p
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogProducer:
    _instances = []  # class-level list to track all producers

    def __init__(self, bootstrap_servers="localhost:9092", client_id="log-producer"):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                client_id=client_id,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            # Register this instance
            LogProducer._instances.append(self)
            self._closed = False
            logger.info(f"Kafka producer {client_id} initialized and registered.")
        except Exception as e:
            logger.error(f"Failed to initialize KafkaProducer: {e}")
            raise

    def send(self, topic, message):
        if self._closed:
            logger.warning("Attempted to send message with a closed producer.")
            return
        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)  # ensure delivery
            logger.info(f"Message sent to topic '{topic}': {message}")
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")

    def close(self):
        if not self._closed:
            try:
                self.producer.flush()
                self.producer.close()
                self._closed = True
                # Remove from registry
                if self in LogProducer._instances:
                    LogProducer._instances.remove(self)
                logger.info("Kafka producer closed successfully.")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")
        else:
            logger.debug("Producer already closed, ignoring.")

    @staticmethod
    def close_all_producers():
        logger.info("Closing all Kafka producers...")
        for producer_instance in list(LogProducer._instances):
            try:
                producer_instance.close()
            except Exception as e:
                logger.error(f"Error closing a producer: {e}")
        LogProducer._instances.clear()
        logger.info("All Kafka producers closed.")

def log_tool_call(producer: LogProducer, tool_topic: str):
    """Factory function to create a decorator that logs tool calls using the provided Kafka producer."""
    def decorator(tool_func):
        @wraps(tool_func)  # Preserve the original function's metadata
        async def wrapper(context: p.ToolContext, **kwargs):
            tool_name = tool_func.__name__
            start_time = datetime.datetime.now()
            try:
                result = await tool_func(context, **kwargs)
                success = True
                error = "None"
            except Exception as e:
                result = "None"
                success = False
                error = str(e)
            end_time = datetime.datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            log_data = {
                'timestamp': start_time.isoformat(),
                'tool_name': tool_name,
                'arguments': json.dumps(kwargs),
                'result': json.dumps(result.data if hasattr(result, 'data') else None),
                'success': success,
                'error': error,
                'response_time_ms': response_time_ms
            }

            producer.send(tool_topic, log_data)
            if not success:
                raise  # Re-raise exception if failed
            return result
        return wrapper
    return decorator