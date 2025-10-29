# தனியக கணினியில் இயல் பிழைதிருத்தியை நிறுவுவது எப்படி?

## நிரல் களஞ்சியம் நகலாக்குக

1. நிரல்கலஞ்சியத்தை `கிட்` மூலம் நகல் எடுக்கவும்
```bash
$ git clone https://github.com/tshrinivasan/iyal-tamil-spellchecker.git
$ cd iyal-spetamil-llchecker/iyal-tamilspellchecker
```

2. `python venv`  உருவாக்கவும் :
```bash
$ virtualenv venv
$ . venv/bin/activate.sh
```

3. சார்பு நிரல் பொதிகளை நிறுவவும்
```bash
$ pip3 install -r requirements.txt
```

4. `flask web server` துவங்கவும்
```bash
$ flask --app app.py run
```

5. இணய உலாவியில் இயல் பிழைதிருத்தியை திறக்கவும்
```bash
$ localhost:8000/
```
