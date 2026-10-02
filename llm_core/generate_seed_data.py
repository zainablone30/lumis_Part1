"""
Helper to scale up the seed dataset using template-based augmentation
(topic x emotion x stance combinations). Use this to bulk up your dataset
to a few thousand rows before LoRA fine-tuning.
"""
import json
import random

TOPICS = [
    "work stress", "loneliness", "family conflict", "exam anxiety",
    "body image", "friendship breakup", "financial stress", "self-doubt",
    "social anxiety", "grief", "burnout", "relationship conflict",
]

NEGATIVE_BELIEFS = [
    "I'm worthless", "I always fail", "nobody actually likes me",
    "I'll never get better at this", "I'm a burden to everyone",
    "I can't do anything right",
]

EMOTIONS = ["Sadness", "Fear", "Anger", "Happiness", "Neutral", "Surprise", "Disgust"]

TEMPLATE_DISAGREE = (
    "I hear that {belief_lower} feels true to you right now, especially with "
    "everything going on with {topic}. But I don't think that's the full picture — "
    "{counter}. What's something small that contradicts that belief, even a little?"
)

COUNTERS = [
    "one hard moment doesn't define your whole worth",
    "you've gotten through difficult things before, which says something about your capability",
    "that sounds like the feeling talking more than the facts",
    "a single setback is data, not a verdict",
]


def generate_rows(n=200, seed=42):
    random.seed(seed)
    rows = []
    for _ in range(n):
        topic = random.choice(TOPICS)
        belief = random.choice(NEGATIVE_BELIEFS)
        counter = random.choice(COUNTERS)
        emotion = random.choice(EMOTIONS)
        instruction = f"I've been dealing with {topic} and honestly {belief.lower()}."
        response = TEMPLATE_DISAGREE.format(
            belief_lower=belief.lower(), topic=topic, counter=counter
        )
        rows.append({"instruction": instruction, "emotion": emotion, "response": response})
    return rows


if __name__ == "__main__":
    rows = generate_rows(300)
    with open("data/seed_dialogues_augmented.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"Generated {len(rows)} augmented rows.")
