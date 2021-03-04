from stats_per_server import main as runServer
from stats_per_site import main as runSite
from stats_per_as import main as runAS
import sys

def runIT():
    print("start running stats per Server")
    runServer()
    print("done")

    print("start running stats per site")
    runSite()
    print('done')

    print("start running stats per AS")
    runAS()
    print("DONE. Anteater will exit now.")

if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  anteater.py")


    else:


        run = runIT()
