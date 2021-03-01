import json

from botzone import *

class Human(Agent):
    
    def reset(self):
        pass
    
    def step(self, request):
        print('Request:', request)
        return json.loads(input('Input response:'))