import json
import os
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from confluent_kafka import Producer

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "streamflix_events")

COUNTRIES = ["Pakistan", "Saudi Arabia", "UAE", "Egypt", "Kuwait", "Qatar", "Bahrain"]
DEVICES = ["Android TV", "iOS", "Android Mobile", "Web", "Samsung TV", "LG TV"]
EVENT_TYPES = [
    "watch_event", "watch_event", "watch_event", "watch_event",
    "search_event", "payment_success", "payment_failed",
    "subscription_started", "subscription_cancelled", "playback_quality_event"
]
SEARCH_TERMS = ["thriller", "football", "turkish drama", "arabic comedy", "kids", "action", "pakistani drama"]


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")


def make_event():
    event_type = random.choice(EVENT_TYPES)
    user_id = f"u_{random.randint(1, 500):04d}"
    content_id = f"c_{random.randint(1, 20):04d}"
    country = random.choice(COUNTRIES)
    device = random.choice(DEVICES)
    base = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": user_id,
        "content_id": content_id if event_type in ["watch_event", "playback_quality_event"] else None,
        "country": country,
        "device": device,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if event_type == "watch_event":
        base.update({
            "watch_minutes": round(random.uniform(1, 120), 2),
            "completion_rate": round(random.uniform(0.05, 1.0), 3),
            "buffering_count": random.choices([0, 1, 2, 3, 4, 5], weights=[55, 20, 12, 7, 4, 2])[0],
            "quality_score": round(random.uniform(0.55, 1.0), 3),
        })
    elif event_type == "playback_quality_event":
        base.update({
            "watch_minutes": 0,
            "completion_rate": 0,
            "buffering_count": random.randint(1, 7),
            "quality_score": round(random.uniform(0.2, 0.85), 3),
        })
    elif event_type == "search_event":
        base.update({"search_query": random.choice(SEARCH_TERMS)})
    elif event_type in ["payment_success", "payment_failed"]:
        base.update({
            "amount": random.choice([350, 499, 700, 999, 1499]),
            "status": "success" if event_type == "payment_success" else "failed",
        })
    elif event_type in ["subscription_started", "subscription_cancelled"]:
        base.update({"status": event_type.replace("subscription_", "")})
    return base


def main():
    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    print(f"Producing OTT events to {TOPIC} at {BOOTSTRAP}. Press Ctrl+C to stop.")
    try:
        while True:
            event = make_event()
            producer.produce(TOPIC, json.dumps(event).encode("utf-8"), callback=delivery_report)
            producer.poll(0)
            print(f"sent {event['event_type']} | {event['user_id']} | {event['country']}")
            time.sleep(0.15)
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.flush()


if __name__ == "__main__":
    main()
