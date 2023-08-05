<p align="center">
  <a href="" rel="noopener">
</p>

<h3 align="center">Telegram Crawler</h3>

<div align="center">

</div>

---

<p align="center"> Telegram Crawler - parser for connections between Channels in Telegram. It can detect connections between Channels, such as: 
Forwards, Mentions and direct links to other Channels.  
    <br> 

</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)

## 🧐 About <a name = "about"></a>

Telegram Crawler is the scanner for connections between Channels in Telegram. It is written in Python and mostly based on [telethon](https://github.com/LonamiWebs/Telethon). This project requires [separate back-end](https://github.com/Antcating/TelegramCrawlerAPI). Back-end based on PostgresQL and FastAPI, so that it allows 
multiple scanners running in parallel to increase scanning speed. 

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

This project written in Python, so you have to make sure you have [Python](https://www.python.org/downloads/) installed on your machine. 

Make sure, Python is operative and you can proceed to installation.

### Installing

Clone this repo: 
```
git clone https://github.com/Antcating/TelegramCrawler.git
```
Go to the project folder
```
cd TelegramCrawler
```

The appropriate thing to do is to create virtual environment for this project. *Newer Linux distros are forcing users to create virtual environments and not install Python packages system-wide*

Create virtual environment for this project in the working directory 
```
python -m venv .
```

Install all the dependencies
```
pip install -r requirements.txt
```

You are done with installation. Now we proceed to running the scanner

## 🎈 Usage <a name="usage"></a>

Before running the project make sure, that **backend is running on `127.0.0.1`**. After you [confirmed](https://github.com/Antcating/TelegramCrawlerAPI#usage), that backend is running, you can proceed to running this project.

```
python src/main.py
```

If the installation was successful, you would be presented with question about starting point of the scanner. After that, the scanner should be running without problems.

## ⛏️ Built Using <a name = "built_using"></a>

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram Backend

## ✍️ Authors <a name = "authors"></a>

- [@Antcating](https://github.com/Antcating) - Author