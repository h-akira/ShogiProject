from hads.shourtcuts import render
from hads.shourtcuts import login_required, redirect

def index(master):
  context = {
    'hoge': "index"
  }
  return render(master, 'index.html', context)

@login_required
def sample(master, parameter):
  context = {
      'parameter': parameter
  }
  return render(master, 'sample.html', context)

def logout(master):
  master.settings.COGNITO.sign_out(master)
  return redirect(master, 'home')

