from hads.shortcuts import render

def index(master):
  context = {}
  return render(master, 'example/index.html', context)
