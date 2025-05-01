from hads.shourtcuts import render
from hads.shourtcuts import login_required, redirect


@login_required
def index(master, username):
  context = {
    'username': username
  }
  return render(master, 'kifu/index.html', context)

@login_required
def explorer(master, username):
  context = {
    'username': username
  }
  return render(master, 'kifu/explorer.html', context)
