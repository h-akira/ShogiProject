import random

def gen_code(length):
  allow="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  return ''.join(random.choice(allow) for i in range(length))

