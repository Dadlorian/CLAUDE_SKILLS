#!/usr/bin/env python3
"""Message Queue Processor - Process healthcare messages asynchronously"""

from typing import Callable, Dict, Any, Optional
import json
import logging
from datetime import datetime
from queue import Queue
import threading

logger = logging.getLogger(__name__)

class MessageQueueProcessor:
    """Process healthcare messages from queue"""

    def __init__(self, max_retries: int = 3, batch_size: int = 100):
        self.queue = Queue()
        self.max_retries = max_retries
        self.batch_size = batch_size
        self.processed_count = 0
        self.failed_count = 0
        self.handlers = {}

    def register_handler(self, message_type: str, handler: Callable):
        """Register handler for message type"""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for {message_type}")

    def enqueue_message(self, message: Dict, priority: int = 0):
        """Add message to queue"""
        wrapped = {
            'id': len(self.queue.qsize()),
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'retries': 0,
            'priority': priority
        }
        self.queue.put((priority, wrapped))

    def process_messages(self, stop_event: Optional[threading.Event] = None):
        """Process queued messages"""
        while True:
            if stop_event and stop_event.is_set():
                break

            try:
                priority, wrapped = self.queue.get(timeout=1)
            except:
                continue

            success = self._process_message(wrapped)

            if not success and wrapped['retries'] < self.max_retries:
                wrapped['retries'] += 1
                self.queue.put((priority, wrapped))
                logger.warning(f"Message {wrapped['id']} requeued")
            elif not success:
                self._log_failed_message(wrapped)
                self.failed_count += 1
            else:
                self.processed_count += 1

            self.queue.task_done()

    def _process_message(self, wrapped: Dict) -> bool:
        """Process single message"""
        try:
            message = wrapped['message']
            msg_type = message.get('type')

            if msg_type not in self.handlers:
                logger.error(f"No handler for message type: {msg_type}")
                return False

            handler = self.handlers[msg_type]
            result = handler(message)

            logger.info(f"Processed message {wrapped['id']}: {msg_type}")
            return result

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            return False

    def _log_failed_message(self, wrapped: Dict):
        """Log permanently failed message"""
        logger.error(f"Message {wrapped['id']} failed after {wrapped['retries']} retries")

    def get_stats(self) -> Dict:
        """Get processor statistics"""
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'queued': self.queue.qsize()
        }


if __name__ == '__main__':
    processor = MessageQueueProcessor()

    # Register handler
    def handle_adt(message: Dict) -> bool:
        print(f"Processing ADT: {message}")
        return True

    processor.register_handler('ADT', handle_adt)

    # Enqueue messages
    processor.enqueue_message({'type': 'ADT', 'data': 'test'})

    # Process
    stop = threading.Event()
    thread = threading.Thread(target=processor.process_messages, args=(stop,))
    thread.start()

    processor.queue.join()
    stop.set()
    thread.join()

    print(processor.get_stats())
