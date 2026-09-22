import json
from pathlib import Path

cases = [
    ("An order was placed, payment authorized, and inventory reserved.", "NORMAL"),
    ("A shipment was delivered after fulfillment was confirmed.", "NORMAL"),
    ("An order was cancelled before payment authorization.", "NORMAL"),
    ("Payment was captured after authorization and before fulfillment.", "NORMAL"),
    ("Inventory was reserved for an active order.", "NORMAL"),
    ("A refund was issued for a previously captured payment.", "NORMAL"),
    ("A customer updated the address before the order shipped.", "NORMAL"),
    ("A tracking number was recorded after the carrier accepted the parcel.", "NORMAL"),
    ("The payment gateway timed out before confirming a charge.", "RETRY"),
    ("The warehouse API returned HTTP 503 during inventory reservation.", "RETRY"),
    ("The card processor returned a temporary HTTP 429 response.", "RETRY"),
    ("The shipping provider timed out before returning a tracking number.", "RETRY"),
    ("The database connection dropped before commit was acknowledged.", "RETRY"),
    ("A downstream service is temporarily unavailable during order lookup.", "RETRY"),
    ("A network reset interrupted a product catalog request.", "RETRY"),
    ("The carrier API reported a temporary service outage.", "RETRY"),
    ("A high-value refund has conflicting delivery evidence.", "HUMAN_REVIEW"),
    ("A customer alleges a duplicate charge, but payment records disagree.", "HUMAN_REVIEW"),
    ("The shipping address changed after dispatch and fraud status is unclear.", "HUMAN_REVIEW"),
    ("A manual override was requested for a blocked transaction without explanation.", "HUMAN_REVIEW"),
    ("A customer disputes a delivered order with conflicting proof of receipt.", "HUMAN_REVIEW"),
    ("Two accounts claim ownership of the same purchase.", "HUMAN_REVIEW"),
    ("A refund request cites an exception that needs a manager decision.", "HUMAN_REVIEW"),
    ("A high-value order has inconsistent identity checks requiring investigation.", "HUMAN_REVIEW"),
    ("A shipment was created before its order was placed.", "QUARANTINE"),
    ("A refund amount exceeds the original payment amount.", "QUARANTINE"),
    ("An order was marked delivered without an order creation record.", "QUARANTINE"),
    ("A completed sale reports a negative item quantity.", "QUARANTINE"),
    ("An analytics event unexpectedly contains a full payment card number.", "QUARANTINE"),
    ("A payment capture exists without any authorization or payment intent.", "QUARANTINE"),
    ("The same order is marked cancelled before creation.", "QUARANTINE"),
    ("A shipment event refers to an impossible negative order total.", "QUARANTINE"),
]

Path("data").mkdir(exist_ok=True)
with open("data/events.jsonl", "w") as events, open("data/ground_truth.jsonl", "w") as labels:
    for i, (description, expected) in enumerate(cases, 1):
        event_id = f"event-{i:03d}"
        events.write(json.dumps({
            "event_id": event_id,
            "event_type": "commerce_event",
            "description": description
        }) + "\n")
        labels.write(json.dumps({"event_id": event_id, "expected": expected}) + "\n")

print(f"Created {len(cases)} events and separate ground-truth labels")
