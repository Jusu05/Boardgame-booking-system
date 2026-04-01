# Boardgame booking system

This is a project for Helsinki University Computer Science course TKT20019. 
The project is not an example project. The project uses Python, Flask, and SQLite3.

## Functionally
☑ User can create account and login \
☑ Users can view all board games added to the app \
☑ Users can search board game listings by keyword \

When user is logged in user can \
&emsp;&emsp;☑ create, edit, and delete board game \
&emsp;&emsp;☐ add images of board game to board game \
&emsp;&emsp;☐ add a avatar \
&emsp;&emsp;☐ review board game \
&emsp;&emsp;☐ reserve available board games and manage their reservations (confirmation, cancellation). \
&emsp;&emsp;☐ assign one or more classifications to a listing

## Running
### Setup
```bash
sqlite3 data.db < schema.sql
sqlite3 data.db < init.sql
cp .env.example .env
python3 -m venv .venv
.venv/bin/activate #on linux/macos windows .venv\scripts\activate
pip install -r requirements.txt
```
### Launch
```bash
python3 app.py
```
