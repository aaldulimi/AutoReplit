from autoreplit import Repl, browser_login

# only need to do this once, then you can comment it out
browser_login()

# the installing packages step will take a while, test it with one package first to get a feel
# sometimes it might stall at that step, just try again
repl = Repl(mount='agent/', packages=['requests'])
output = repl.run('python main.py')
print(output)

repl.delete()
