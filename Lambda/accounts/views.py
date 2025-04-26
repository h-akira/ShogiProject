from hads.shourtcuts import render
from hads.shourtcuts import login_required, redirect

@login_required
def logout(master):
  master.settings.COGNITO.sign_out(master)
  return redirect(master, 'kifu:home')
