import json
from collections import Counter
from pathlib import Path

contexts = [
    ("order-101", "wireless headphones", "customer A"),
    ("order-102", "running shoes", "customer B"),
    ("order-103", "coffee maker", "customer C"),
    ("order-104", "desk lamp", "customer D"),
    ("order-105", "winter jacket", "customer E"),
    ("order-106", "laptop sleeve", "customer F"),
    ("order-107", "water bottle", "customer G"),
    ("order-108", "phone charger", "customer H"),
    ("order-109", "backpack", "customer I"),
    ("order-110", "keyboard", "customer J"),
    ("order-111", "monitor stand", "customer K"),
    ("order-112", "notebook", "customer L"),
    ("order-113", "fitness tracker", "customer M"),
    ("order-114", "desk chair", "customer N"),
    ("order-115", "travel mug", "customer O"),
    ("order-116", "camera strap", "customer P"),
    ("order-117", "USB hub", "customer Q"),
    ("order-118", "yoga mat", "customer R"),
    ("order-119", "bookcase", "customer S"),
    ("order-120", "speaker", "customer T"),
    ("order-121", "tablet case", "customer U"),
    ("order-122", "bike helmet", "customer V"),
    ("order-123", "mouse", "customer W"),
    ("order-124", "raincoat", "customer X"),
    ("order-125", "sunglasses", "customer Y"),
]

# Each context has two examples for each expected route.
scenarios = [
    (
        "Payment was authorized, inventory reserved, and the item is ready for fulfillment.",
        "NORMAL",
    ),
    (
        "The customer cancelled before shipment; the payment authorization was voided.",
        "NORMAL",
    ),
    (
        "The payment provider timed out before confirming whether authorization succeeded.",
        "RETRY",
    ),
    (
        "The inventory service returned HTTP 503 before confirming the reservation.",
        "RETRY",
    ),
    (
        "The customer disputes delivery; carrier proof and customer evidence conflict.",
        "HUMAN_REVIEW",
    ),
    (
        "The shipping address changed after dispatch; the fraud assessment is inconclusive.",
        "HUMAN_REVIEW",
    ),
    (
        "A refund was recorded before any payment or authorization existed.",
        "QUARANTINE",
    ),
    (
        "The item was marked delivered before the order creation timestamp.",
        "QUARANTINE",
    ),
]

Path("data").mkdir(exist_ok=True)
counts = Counter()

with open("data/scale_events.jsonl", "w") as events, \
     open("data/scale_ground_truth.jsonl", "w") as labels:
    for context_index, (order, product, customer) in enumerate(contexts):
        for scenario_index, (description, expected) in enumerate(scenarios):
            event_id = f"scale-{context_index:02d}-{scenario_index:02d}"
            event = {
                "event_id": event_id,
                "event_type": "commerce_event",
                "order_id": order,
                "product": product,
                "customer": customer,
                "description": description,
            }
            events.write(json.dumps(event) + "\n")
            labels.write(json.dumps({
                "event_id": event_id,
                "expected": expected,
                "context": order,
                "scenario": scenario_index,
            }) + "\n")
            counts[expected] += 1

print(f"Generated {sum(counts.values())} events")
print("Labels:", dict(counts))
print("Unique descriptions:", len({
    json.loads(line)["description"]
    for line in open("data/scale_events.jsonl")
}))
