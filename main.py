import json
import os
import random
import re 
# (English, German, category)
def load_sentences():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saetze.txt")
    sentences = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                english, german, category = [part.strip() for part in line.split("|")]
                sentences.append((english, german, category))
    return sentences


SENTENCES = load_sentences()

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.json")


def normalize(text):
    """Lowercase, turn umlauts into ae/oe/ue/ss, remove punctuation."""
    text = text.lower().strip()
    for old, new in [("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")]:
        text = text.replace(old, new)
    text = re.sub(r"[^a-z ]", "", text)
    return " ".join(text.split())


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"boxes": {}, "mistakes": {}}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def pick_questions(progress, pool, how_many=10):
    pool = list(pool)
    chosen = []
    while pool and len(chosen) < how_many:
        weights = [6 - progress["boxes"].get(s[1], 1) for s in pool]
        pick = random.choices(pool, weights=weights, k=1)[0]
        chosen.append(pick)
        pool.remove(pick)
    return chosen

def choose_pool(progress):
    print("1 = gemischte Runde")
    print("2 = nur meine schwächste Kategorie")
    choice = input("Wahl: ").strip()
    if choice == "2" and progress["mistakes"]:
        weakest = max(progress["mistakes"], key=progress["mistakes"].get)
        print(f"Schwächste Kategorie: {weakest}\n")
        return [s for s in SENTENCES if s[2] == weakest]
    return list(SENTENCES)


def main():
    progress = load_progress()
    print("=== Satzbau Trainer ===")
    print("Translate into German. You can type ae/oe/ue instead of ä/ö/ü.\n")
    questions = pick_questions(progress, choose_pool(progress))
    score = 0

    for number, (english, german, category) in enumerate(questions, start=1):
        print(f"{number}. {english}")
        answer = input("   > ")
        box = progress["boxes"].get(german, 1)

        if normalize(answer) == normalize(german):
            print("   Richtig!\n")
            score += 1
            progress["boxes"][german] = min(box + 1, 5)
        else:
            print(f"   Falsch. Richtig wäre: {german}\n")
            progress["boxes"][german] = 1
            progress["mistakes"][category] = progress["mistakes"].get(category, 0) + 1

    save_progress(progress)

    print(f"Ergebnis: {score}/{len(questions)}")
    if progress["mistakes"]:
        print("\nDeine schwächsten Kategorien (insgesamt):")
        ranking = sorted(progress["mistakes"].items(), key=lambda x: -x[1])
        for category, count in ranking:
            print(f"  - {category}: {count} Fehler")


main()