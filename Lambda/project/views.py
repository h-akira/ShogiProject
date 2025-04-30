from hads.shourtcuts import render

def home(master):
  context = {}
  return render(master, 'home.html', context)
