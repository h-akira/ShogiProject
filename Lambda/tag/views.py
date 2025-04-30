from hads.shourtcuts import render

def index(master, username):
  context = {
    'username': username
  }
  return render(master, 'tag/index.html', context)
