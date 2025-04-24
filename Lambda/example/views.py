from hads.shourtcuts import render

def index(master):
  context = {}
  return render(master, 'example/index.html', context)
