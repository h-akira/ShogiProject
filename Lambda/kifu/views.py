from hads.shourtcuts import render
from hads.shourtcuts import login_required, redirect
from .forms import KifuForm
import random


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

@login_required
def create(master, username):
  if master.request.method == 'POST':
    context = {
      'username': username
    }
    master.logger.info(master.request.body)
    return redirect(master, 'kifu:create', username=username)
  elif master.request.method == 'GET':
    allow="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    length=32
    share_code = ''.join(random.choice(allow) for i in range(length))
    initial = {
      'share_code': share_code
    }
    form = KifuForm(data=initial)
    context = {
      "type": "create",
      "form": form,
      "error_message": None
    }
    return render(master, 'kifu/create.html', context)
  else:
    raise Exception('Invalid request method')
