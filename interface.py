import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
"""
try:
    from main import *
except:
    from app.botAIapi.marionbotapi.transfchatbot.talk import *
import time
"""
from transfchatbot.talk import *

def answer(input,oldmessages):
    return predict(input)

"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
try:
    from main import *
except:
    from app.botAIapi.marionbotapi.main import *
import time

try:
    load_weights = tl.files.load_npz(name='saved/model_16-06-2020_2.npz')
except:
    load_weights = tl.files.load_npz(name='app/botAIapi/marionbotapi/saved/model_16-06-2020_2.npz')
tl.files.assign_weights(load_weights, model_)

def answer(input):
    sentence = inference(input, 3)
    response=' '.join(sentence)
    return response
"""
