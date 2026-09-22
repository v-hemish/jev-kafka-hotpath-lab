import csv
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from confluent_kafka import Consumer, Producer

TOPICS = {
    "NORMAL": "events.normal",
    "RETRY": "events.retry",
    "HUMAN_REVIEW": "events.human_review",
    "QUARANTINE": "events.quarantine",
}

QUESTION = {
    "route": {
        "type": "choice",
        "instructions": "Choose the operational route for this commerce event.",
        "criteria": {
            "NORMAL": "A valid business event; continue processing.",
            "RETRY": "A temporary dependency or infrastructure failure.",
            "HUMAN_REVIEW": "An ambiguous or high-risk case needing a person.",
            "QUARANTINE": "An impossible or corrupt business event, or unexpected sensitive data.",
        },
    }
}

MAX_EVENTS = 200
CONFIDENCE_THRESHOLD = 0.70

def ask_jev(event):
    body = {
        "model": "jev-latest",
        "state": event,
        "questions": QUESTION,
    }
    request = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}",
            "Content-Type": "application/json",
        },
    )

    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=20) as response:
        result = json.load(response)
    latency_ms = (time.perf_counter() - start) * 1000

    answer = result["answers"]["route"]
    choice = answer["choice"]
    probabilities = answer["probabilities"]

    if choice not in TOPICS or set(probabilities) != set(TOPICS):
        raise ValueError(f"Unexpected Jev answer: {answer}")

    return choice, float(probabilities[choice]), latency_ms, result["usage"]

def main():
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY is missing")

    Path("results").mkdir(exist_ok=True)
    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "jev-experiment-v1",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    producer = Producer({"bootstrap.servers": "localhost:9092"})
    consumer.subscribe(["events.raw"])

    fields = [
        "event_id", "decision", "routed_to", "chosen_probability",
        "latency_ms", "input_tokens", "output_tokens",
    ]
    processed = 0

    try:
        with open("results/scale_decisions.csv", "w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()

            while processed < MAX_EVENTS:
                message = consumer.poll(15)
                if message is None:
                    print("No event received for 15 seconds; stopping.")
                    break
                if message.error():
                    raise RuntimeError(message.error())

                event = json.loads(message.value())
                choice, probability, latency_ms, usage = ask_jev(event)

                route = (
                    choice if probability >= CONFIDENCE_THRESHOLD
                    else "HUMAN_REVIEW"
                )
                decision = {
                    "event_id": event["event_id"],
                    "decision": choice,
                    "routed_to": TOPICS[route],
                    "chosen_probability": probability,
                    "latency_ms": round(latency_ms, 2),
                    "input_tokens": usage["input_tokens"],
                    "output_tokens": usage["output_tokens"],
                }

                producer.produce(
                    TOPICS[route],
                    key=event["event_id"],
                    value=json.dumps({"event": event, "decision": decision}),
                )
                producer.flush(10)
                consumer.commit(message=message, asynchronous=False)
                writer.writerow(decision)
                output.flush()

                processed += 1
                print(
                    f'{processed:02d}/{MAX_EVENTS} {event["event_id"]} '
                    f'{choice} → {TOPICS[route]} '
                    f'{latency_ms:.0f} ms'
                )
    finally:
        consumer.close()

    print(f"Saved {processed} decisions to results/scale_decisions.csv")

if __name__ == "__main__":
    main()
