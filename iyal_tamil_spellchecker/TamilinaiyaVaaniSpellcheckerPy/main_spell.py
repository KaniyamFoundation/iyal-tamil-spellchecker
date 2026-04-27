import sys
import argparse
import re
try:
    from .db_loader import TamilinaiyaVaaniData
    from .spellchecker import TamilinaiyaVaaniSpellchecker
except ImportError:
    from db_loader import TamilinaiyaVaaniData
    from spellchecker import TamilinaiyaVaaniSpellchecker

def main():
    parser = argparse.ArgumentParser(description="Vaani Tamil Spellchecker")
    parser.add_argument("text", nargs="?", help="Text to spellcheck")
    parser.add_argument("--db", default="data/DB.json", help="Path to DB.json")
    parser.add_argument("--file", help="Path to a text file to spellcheck")
    args = parser.parse_args()

    data = TamilinaiyaVaaniData(args.db)
    if not data.load():
        sys.exit(1)
        
    checker = TamilinaiyaVaaniSpellchecker(data)
    
    content = ""
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.text:
        content = args.text

    if content:
        # Regex to split by whitespace and keep punctuation separate if needed, 
        # or just strip punctuation for spellchecking.
        # Here we strip common punctuation.
        raw_words = re.findall(r"[\u0B80-\u0BFF]+", content)
        results = checker.validate_words(raw_words)
        for word, res in zip(raw_words, results):
            if res[1] != "correct":
                print(f"[{word}]: Wrong. Suggestions: {res[1]}")
        print("\nSpellcheck complete.")
    else:
        # Interactive mode
        print("Vaani Tamil Spellchecker (Python). Type 'exit' to quit.")
        while True:
            try:
                line = input("> ")
                if line.lower() == 'exit': break
                words = line.split()
                results = checker.validate_words(words)
                for word, res in zip(words, results):
                    if res[1] == "correct":
                        print(f"  {word}: Correct")
                    else:
                        print(f"  {word}: Wrong. Suggestions: {res[1]}")
            except EOFError:
                break

if __name__ == "__main__":
    main()
