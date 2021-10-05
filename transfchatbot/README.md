based on  https://chatbotslife.com/replicate-your-friend-with-transformer-bc5efe3a1596

* To run your Chatbot, only those 3 lines have to be written in Command Prompt (in repository path).

  * `python conversations_to_csv.py path_to_html_files` You will be asked to enter input and target persons fullname. The first person is probably you and the target person is the one you want to make chatbot based on. Please note, that names you enter should be exactly the same as provided on Facebook.

  * `python train.py` This script is responsible for building and training transformer model, so it will take some time  to complete. If you would like to change some parameters, for example batch size or number of epochs, you can easily do it  within the script.

  * `python talk.py` You will be asked to enter your and chatbot name or nick.  Then you can start your conversation. Enjoy! For closing, press `CTRL + C`

  *


    
