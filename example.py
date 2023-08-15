from autoreplit import Repl, browser_login

# only need to do this once, then you can comment it out
browser_login()

# the installing packages step will take a while
# sometimes it might stall at the mounting files step, re run again if that happens
repl = Repl(mount='agent/', packages=['requests'])
output = repl.run('python main.py')
print(output)

repl.delete()
