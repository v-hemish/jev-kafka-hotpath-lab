import json

cases = [
    ("The carrier API timed out, but the order was already delivered yesterday.", "NORMAL"),
    ("A customer asks for a refund after delivery; the refund amount matches the original charge and policy eligibility is unclear.", "HUMAN_REVIEW"),
    ("The payment gateway returned HTTP 503 before confirming whether an authorization succeeded.", "RETRY"),
    ("A refund was recorded before any payment existed, although the refund service returned HTTP 200.", "QUARANTINE"),
    ("The warehouse API timed out while reserving inventory; the order has not shipped.", "RETRY"),
    ("A shipment is marked delivered before the order was created; the carrier API is healthy.", "QUARANTINE"),
    ("A high-value order passed payment authorization, but identity checks disagree and require investigation.", "HUMAN_REVIEW"),
    ("An order was cancelled before shipment, and the payment authorization was voided.", "NORMAL"),
    ("The retry count is high because the carrier API is temporarily unavailable; no shipment status was changed.", "RETRY"),
    ("The retry count is high, but this event says the item quantity on a completed sale is negative.", "QUARANTINE"),
    ("A customer reports a duplicate charge, but the two payment records may represent separate purchases.", "HUMAN_REVIEW"),
    ("A refund was issued after a documented return and matches the amount originally captured.", "NORMAL"),
    ("The analytics event has a valid schema and also contains a full payment card number in its description.", "QUARANTINE"),
    ("The database connection reset before the order write committed; whether it persisted is unknown.", "RETRY"),
    ("The delivery proof and customer claim conflict; the order and payment records are otherwise valid.", "HUMAN_REVIEW"),
    ("The shipping provider briefly returned HTTP 429 after a tracking number had already been stored successfully.", "NORMAL"),
]

with open("data/hard_events.jsonl", "w") as events, \
     open("data/hard_ground_truth.jsonl", "w") as labels:
    for i, (description, expected) in enumerate(cases, 33):
        event_id = f"event-{i:03d}"
        events.write(json.dumps({
            "event_id": event_id,
            "event_type": "commerce_event",
            "description": description
        }) + "\n")
        labels.write(json.dumps({
            "event_id": event_id,
            "expected": expected
        }) + "\n")

print(f"Created {len(cases)} harder events")
