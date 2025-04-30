from hads.shourtcuts import render

def index(master, username):
  context = {
    'username': username
  }
  return render(master, 'kifu/index.html', context)

def explorer(master, username):
  context = {
    'username': username
  }
  return render(master, 'kifu/explorer.html', context)
