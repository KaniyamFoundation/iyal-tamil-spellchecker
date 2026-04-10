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
$ localhost:5000/
```

## LanguageTool அமைப்பது எப்படி? (How to setup LanguageTool server)

இயல் பிழைத்திருத்தி LanguageTool வழியாக இலக்கணப் பிழைகளைச் சுட்டிக்காட்ட, LanguageTool சேவையகம் பின்னணியில் இயங்க வேண்டும்.

1. LanguageTool ஐ snap மூலம் நிறுவவும்:
```bash
sudo snap install languagetool
```

2. பயனர் systemd சேவையை உருவாக்கவும் (Create a systemd user service):
```bash
mkdir -p ~/.config/systemd/user
cat << 'EOF' > ~/.config/systemd/user/languagetool.service
[Unit]
Description=LanguageTool Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/java -cp /snap/languagetool/current/usr/bin/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --allow-origin '*'
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF
```

3. சேவையைத் துவக்கி செயல்படுத்துங்கள் (Enable and start the service):
```bash
systemctl --user daemon-reload
systemctl --user enable --now languagetool.service
```

நீங்கள் `systemctl --user status languagetool.service` கட்டளை மூலம் சேவை சரியாக இயங்குகிறதா என பார்க்கலாம். LanguageTool 8081 என்ற போர்ட்டில் இயங்கும்.
