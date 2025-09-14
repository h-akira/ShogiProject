from wambda.shortcuts import render

def home(master):
  context = {}
  return render(master, 'home.html', context)
