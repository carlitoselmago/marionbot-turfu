# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:37:12 2020

@author: zuzan
"""

import sys
import pandas as pd
import pathlib

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import pickle
from train import textPreprocess
from train import transformer
from train import CustomSchedule
from train import accuracy, loss_function
from config import *
import numpy as np

from colorama import init
from colorama import Fore, Back
init()

strategy = tf.distribute.get_strategy()

# For tf.data.Dataset
BATCH_SIZE = int(64 * strategy.num_replicas_in_sync)


try:
    with open(str(pathlib.Path(__file__).parent.absolute())+'/saved/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
except:
    print("Error::::::: no tokenizer found, run the training on train.py")
    sys.exit()

# Define start and end token to indicate the start and end of a sentence
START_TOKEN, END_TOKEN = [tokenizer.vocab_size], [tokenizer.vocab_size + 1]

# Vocabulary size plus start and end token
VOCAB_SIZE = tokenizer.vocab_size + 2


def evaluate(sentence, model,temperature=0.7):
  sentence = textPreprocess(sentence)
  sentence = tf.expand_dims(
      START_TOKEN + tokenizer.encode(sentence) + END_TOKEN, axis=0)
  output = tf.expand_dims(START_TOKEN, 0)

  for i in range(MAX_LENGTH):
    predictions = model(inputs=[sentence, output], training=False)
    # select the last word from the seq_len dimension
    predictions = predictions[:, -1:, :]
    #print(predictions)
    #new part :::::::::::::::::::::
    #preds = np.asarray(preds).astype('float64')
    preds = np.log(predictions) / temperature
    exp_preds = np.exp(predictions)
    predictions = exp_preds / np.sum(exp_preds)
    #print(predictions)
    #print("predictions shape",predictions.shape)
    #print("vamo a ver",predictions[0][0].shape)
    probas = np.random.multinomial(1, predictions[0][0], 1)
    #print("probas shape",probas.shape)
    #return np.argmax(probas)
    # end new part :::::::::::::::::::::

    #predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32) #original
    predicted_id = tf.cast(tf.argmax([probas], axis=-1), tf.int32)
    # return the result if the predicted_id is equal to the end token
    if tf.equal(predicted_id, END_TOKEN[0]):
      break
    # concatenated the predicted_id to the output which is given to the decoder
    # as its input.
    output = tf.concat([output, predicted_id], axis=-1)

  return tf.squeeze(output, axis=0)



def predict(sentence,temperature=0.7):
  prediction = evaluate(sentence.lower(),model,temperature)
  predicted_sentence = tokenizer.decode(
      [i for i in prediction if i < tokenizer.vocab_size])
  return predicted_sentence.lstrip().capitalize()


learning_rate = CustomSchedule(D_MODEL)

optimizer = tf.keras.optimizers.Adam(
    learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9)

model = transformer(
      vocab_size=VOCAB_SIZE,
      num_layers=NUM_LAYERS,
      units=UNITS,
      d_model=D_MODEL,
      num_heads=NUM_HEADS,
      dropout=DROPOUT)

model.compile(optimizer=optimizer, loss=loss_function, metrics=[accuracy])

try:
    model.load_weights(str(pathlib.Path(__file__).parent.absolute())+'/saved/saved_weights.h5')
except:
    print("Error::::::: no trained model found, run the training on train.py")
    sys.exit()

"""
if __name__ == '__main__':
    while True:

        prompt = input("you: ")

        print("bot:"+predict(prompt))
"""
#give two sentences as input
if __name__ == '__main__':
    lastPrompt=""
    while True:

        prompt = input("you: ")
        predicted=predict(lastPrompt+". "+prompt)
        print("bot:"+predicted)
        lastPrompt=predicted
