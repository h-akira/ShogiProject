from hads.shortcuts import render
from hads.shortcuts import login_required, redirect

@login_required
def logout(master):
  master.settings.COGNITO.sign_out(master)
  return redirect(master, 'home')
