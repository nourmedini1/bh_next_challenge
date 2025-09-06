#!/usr/bin/env python3
import json
import signal
import sys
import traceback
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from clickhouse_driver import Client
from log_consumer import LogKafkaConsumer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka Topics (matching those defined in producer files)
TOOL_TOPICS = [
    'tool_get_complete_user_info',
    'tool_get_user_contracts',
    'tool_get_contract_details',
    'tool_get_user_claims',
    'tool_get_claim_details',
    'tool_check_user_existence',
    'tool_search_life_insurance_documents',
    'tool_search_health_insurance_documents',
    'tool_search_transport_marine_documents',
    'tool_search_property_casualty_documents',
    'tool_search_engineering_construction_documents',
    'tool_search_automobile_insurance_documents',
    'tool_search_general_knowledge_documents',
    'tool_get_automobile_insurance_quote',
    'tool_get_non_automobile_insurance_products_descriptions',
    'security_logs'
]

# ClickHouse Configuration
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_DATABASE = 'logs_db'
CLICKHOUSE_USER = 'default'  # Update if authentication is required
CLICKHOUSE_PASSWORD = 'your_secure_password'     # Update if authentication is required

# Email Configuration for Security Alerts
SMTP_SERVER = 'smtp.gmail.com'  # Update with your SMTP server
SMTP_PORT = 587
SENDER_EMAIL = 'your_sender_email@gmail.com'  # Update with your sender email
SENDER_PASSWORD = 'your_app_password'  # Use app password for Gmail
ADMIN_EMAIL = 'admin@yourdomain.com'  # Update with admin email

class LogManager(LogKafkaConsumer):
    """Log manager that consumes Kafka messages, persists them to ClickHouse, and sends email alerts for security logs."""
    
    def __init__(self, topics=TOOL_TOPICS, bootstrap_servers='localhost:9092', group_id='log-manager-group'):
        super().__init__(topics, bootstrap_servers, group_id)
        self.message_count = 0
        self.tool_log_count = 0
        self.security_log_count = 0
        
        # Initialize ClickHouse client
        self.ch_client = Client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
           # database=CLICKHOUSE_DATABASE
        )
        
        # Create database if not exists
        self.ch_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DATABASE}")
        
        # Create tables for each topic if not exists
        for topic in self.topics:
            table_name = f"{topic}_logs"
            if topic == 'security_logs':
                self.ch_client.execute(f"""
                    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE}.{table_name} (
                        timestamp DateTime,
                        message String,
                        status String,
                        details String,
                        response_time_ms Float64
                    ) ENGINE = MergeTree()
                    ORDER BY timestamp
                """)
            else:
                self.ch_client.execute(f"""
                    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE}.{table_name} (
                        timestamp DateTime,
                        tool_name String,
                        arguments String,
                        result String,
                        success Boolean,
                        error String,
                        response_time_ms Float64
                    ) ENGINE = MergeTree()
                    ORDER BY timestamp
                """)
        logger.info("ClickHouse tables initialized for all topics.")

    def process_message(self, message):
        """Process, persist, and handle alerts for log messages."""
        self.message_count += 1
        
        try:
            data = message.value
            topic = message.topic
            table_name = f"{topic}_logs"
            
            if topic == 'security_logs':
                self.security_log_count += 1
                log_type = "Security"
                
                # Format and print the log message
                log_details = (
                    f"[{log_type} Log] Message {self.message_count}\n"
                    f"  Topic: {topic}\n"
                    f"  Partition: {message.partition}\n"
                    f"  Offset: {message.offset}\n"
                    f"  Timestamp: {datetime.datetime.fromtimestamp(message.timestamp / 1000).isoformat()}\n"
                    f"  Message: {data.get('message', 'N/A')}\n"
                    f"  Status: {data.get('status', 'N/A')}\n"
                    f"  Details: {json.dumps(data.get('details', []), indent=2)}\n"
                    f"  Response Time (ms): {data.get('response_time_ms', 'N/A')}\n"
                )
                
                # Send email alert for security logs
                self.send_security_alert(data)
                
                # Persist to ClickHouse
                self.ch_client.execute(
                    f"INSERT INTO {CLICKHOUSE_DATABASE}.{table_name} "
                    "(timestamp, message, status, details, response_time_ms) VALUES",
                    [(
                        datetime.datetime.fromisoformat(data['timestamp']),
                        data.get('message', ''),
                        data.get('status', ''),
                        json.dumps(data.get('details', [])),
                        data.get('response_time_ms', 0.0)
                    )]
                )
            else:
                self.tool_log_count += 1
                log_type = "Tool"
                
                # Format and print the log message
                log_details = (
                    f"[{log_type} Log] Message {self.message_count}\n"
                    f"  Topic: {topic}\n"
                    f"  Partition: {message.partition}\n"
                    f"  Offset: {message.offset}\n"
                    f"  Timestamp: {datetime.datetime.fromtimestamp(message.timestamp / 1000).isoformat()}\n"
                    f"  Tool Name: {data.get('tool_name', 'N/A')}\n"
                    f"  Arguments: {data.get('arguments', 'N/A')}\n"
                    f"  Result: {data.get('result', 'N/A')}\n"
                    f"  Success: {data.get('success', 'N/A')}\n"
                    f"  Error: {data.get('error', 'N/A')}\n"
                    f"  Response Time (ms): {data.get('response_time_ms', 'N/A')}\n"
                )
                
                # Persist to ClickHouse
                self.ch_client.execute(
                    f"INSERT INTO {CLICKHOUSE_DATABASE}.{table_name} "
                    "(timestamp, tool_name, arguments, result, success, error, response_time_ms) VALUES",
                    [(
                        datetime.datetime.fromisoformat(data['timestamp']),
                        data.get('tool_name', ''),
                        data.get('arguments', ''),
                        data.get('result', ''),
                        data.get('success', False),
                        data.get('error', ''),
                        data.get('response_time_ms', 0.0)
                    )]
                )
            
            logger.info(log_details)
            print(log_details)
            
            # Log statistics every 10 messages
            if self.message_count % 10 == 0:
                logger.info(
                    f"Statistics: {self.message_count} messages processed "
                    f"({self.tool_log_count} tool logs, {self.security_log_count} security logs)"
                )
                
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in processing/persisting message for topic {message.topic}: {e}")

    def send_security_alert(self, data: dict):
        """Send an urgent email alert to the admin for security incidents."""
        try:
            msg = MIMEText(
                f"Security Incident Alert:\n\n"
                f"Timestamp: {data.get('timestamp', 'N/A')}\n"
                f"Message: {data.get('message', 'N/A')}\n"
                f"Status: {data.get('status', 'N/A')}\n"
                f"Details: {json.dumps(data.get('details', []), indent=2)}\n"
                f"Response Time (ms): {data.get('response_time_ms', 'N/A')}\n"
            )
            msg['Subject'] = 'URGENT: Security Log Incident Detected'
            msg['From'] = SENDER_EMAIL
            msg['To'] = ADMIN_EMAIL
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            logger.info("Security alert email sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send security alert email: {e}")

def signal_handler(signum, frame):
    """Handle graceful shutdown."""
    logger.info("Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the log manager."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the log manager
    log_manager = LogManager(TOOL_TOPICS, group_id='log-manager-group')
    
    try:
        # Get topic metadata (optional)
        log_manager.get_topic_metadata()
        
        # Start consuming and processing messages
        log_manager.start_consuming()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        log_manager.stop_consuming()

if __name__ == "__main__":
    main()