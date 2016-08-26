
import os
import optparse


p = optparse.OptionParser()
p.add_option('-s', '--size', help="Size of builder farm", default=2)
    
opts, args = p.parse_args()


launch_terminal = "gnome-terminal -x bash -c \"%s && bash\""

# Launch the web query front
os.system(launch_terminal % "python query_services.py")

# Launch redis
os.system(launch_terminal % "redis-server")

# Launch two builder
for n in range(0,opts.size):
   name = "builder%s" % n
   work = "work%s" % n
   os.system( launch_terminal % ("python builder_services.py -n %s -w %s" % (name,work)) )

