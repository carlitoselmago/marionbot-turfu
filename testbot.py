import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from transfchatbot.talk import *
import time

if __name__ == '__main__':
    while True:

        prompt = input("you: ")

        print("bot:"+predict(prompt))
