import regex

text = "பதிவாகியுள்ளன.இதுகுறித்து"
pattern = r"(\p{Tamil}{3,})\.(\p{Tamil})"
matches = list(regex.finditer(pattern, text))
print(f"Text: {text}")
print(f"Matches found: {len(matches)}")
for m in matches:
    print(f"  Match: {m.group(0)}")
