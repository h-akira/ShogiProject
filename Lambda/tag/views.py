from hads.shortcuts import render

MAIN_TABLE_NAME = "table-sgp-main"
TID_LENGTH = 8

def index(master, username):
  context = {
    'username': username
  }
  return render(master, 'tag/index.html', context)
