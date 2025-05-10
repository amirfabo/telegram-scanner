# Telegram Usernames Scanner

<b>Telegram usernames scanner</b> can scan usernames and detect their status. 

💠 Three mode available:

1. Occupied (username is claimable or already taken) ✅
2. Invalid (username is banned or is collectible NFT) 🚫
3. On Fragment (username is for sale or auction proceed) 🌀

# Features

- Easy to Use
- Interactive console statistics
- Unlimited and Reliable

# Requirements

1. Python 3.10+
2. Telethon

# Installation

- git clone https://github.com/amirfabo/telegram-scanner.git
- cd telegram-scanner
- pip install -r requirements.txt

## ⚠️ Note before using

⬇️ You must edit the configuration file keys (<code>settings.ini</code>) like below:

1. First replace Telegram API authentication info ([generate](https://my.telegram.org/))
2. Second save and replace String Session hash of your telethon session. ([See more](http://docs.telethon.dev/en/stable/concepts/sessions.html#string-sessions))
3. Finally, You can run the scanner with <code>python3 scanner.py</code> command.