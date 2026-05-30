import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from confluent_kafka import Consumer
from sqlalchemy import text

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.db import get_engine
from src.seed_dimensions import main as seed_dimensions

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "streamflix_events")


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def insert_event(engine, event):
    sql = text("""
        INSERT INTO raw_events
        (event_id, event_type, user_id, content_id, country, device, event_timestamp, event_payload)
        VALUES
        (:event_id, :event_type, :user_id, :content_id, :country, :device, :event_timestamp, CAST(:payload AS JSONB))
        ON CONFLICT (event_id) DO NOTHING
    """)
    with engine.begin() as conn:
        conn.execute(sql, {
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "user_id": event.get("user_id"),
            "content_id": event.get("content_id"),
            "country": event.get("country"),
            "device": event.get("device"),
            "event_timestamp": parse_ts(event["timestamp"]),
            "payload": json.dumps(event),
        })


def main():
    seed_dimensions()
    engine = get_engine()
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": "streamflix-consumer-group",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([TOPIC])
    print(f"Consuming from {TOPIC} at {BOOTSTRAP}. Press Ctrl+C to stop.")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            event = json.loads(msg.value().decode("utf-8"))
            insert_event(engine, event)
            print(f"inserted {event['event_type']} | {event['user_id']} | {event['country']}")
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
