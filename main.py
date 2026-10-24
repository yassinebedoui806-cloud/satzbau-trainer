import json
import os
import random
import re 
# (English, German, category)
SENTENCES = [
    ("I'm waiting for the bus.", "Ich warte auf den Bus.", "verb+praeposition"),
    ("She is waiting for her friend.", "Sie wartet auf ihre Freundin.", "verb+praeposition"),
    ("I can't solve this problem.", "Ich kann dieses Problem nicht lösen.", "modalverb"),
    ("He can't solve the task.", "Er kann die Aufgabe nicht lösen.", "modalverb"),
    ("Could you help me, please? (formal)", "Könnten Sie mir bitte helfen?", "konjunktiv2"),
    ("Could you open the window? (informal)", "Könntest du das Fenster öffnen?", "konjunktiv2"),
    ("The man whose car is red lives here.", "Der Mann, dessen Auto rot ist, wohnt hier.", "relativsatz"),
    ("The woman whose son studies in Berlin is my neighbour.", "Die Frau, deren Sohn in Berlin studiert, ist meine Nachbarin.", "relativsatz"),
    ("I'm giving my brother a book as a present.", "Ich schenke meinem Bruder ein Buch.", "kasus"),
    ("She gives her mother flowers as a present.", "Sie schenkt ihrer Mutter Blumen.", "kasus"),
    ("I forgot to call him.", "Ich habe vergessen, ihn anzurufen.", "infinitiv+zu"),
    ("Don't forget to close the door.", "Vergiss nicht, die Tür zuzumachen.", "infinitiv+zu"),
    ("The project is supported by the city.", "Das Projekt wird von der Stadt befürwortet.", "passiv"),
    ("That can be determined easily.", "Das lässt sich leicht feststellen.", "passiv"),
    ("The problem can be solved.", "Das Problem lässt sich lösen.", "passiv"),
    ("The book I'm interested in is expensive.", "Das Buch, für das ich mich interessiere, ist teuer.", "relativsatz"),
    ("The topic I'm talking about is important.", "Das Thema, über das ich spreche, ist wichtig.", "relativsatz"),
    ("My studies are going well.", "Mein Studium läuft gut.", "wortschatz"),
]

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


def pick_questions(progress, how_many=10):
    """Sentences in a low box (weak) are picked more often."""
    pool = list(SENTENCES)
    chosen = []
    while pool and len(chosen) < how_many:
        weights = [6 - progress["boxes"].get(s[1], 1) for s in pool]
        pick = random.choices(pool, weights=weights, k=1)[0]
        chosen.append(pick)
        pool.remove(pick)
    return chosen


def main():
    progress = load_progress()
    print("=== Satzbau Trainer ===")
    print("Translate into German. You can type ae/oe/ue instead of ä/ö/ü.\n")

    questions = pick_questions(progress)
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