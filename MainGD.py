import threading #we use this for the ques
from queue import Queue #we use this for the ques
import datetime #used for makeing semi-uniqe save directorys
import os #used for accesing our local machine
import logging #used for logging runs
import sys #used for logging our python exectuable used by Task scheduler
from dotenv import load_dotenv #used for reading our .env file which contains our api keys and service clients

#import functions from our other .py fiels
from GenerateStory import request_elephant_story, add_ssml_breaks 
from TextToSpeech import text_to_speech_google
from ImageGen2 import StoryImageGenerator
from Merge import process_video_creation

#start logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f"Python executable: {sys.executable}") #log python executable
print(sys.executable)
load_dotenv()  # This loads the environment variables from .env

#load information for .env
api_key = os.getenv('OPENAI_API_KEY')
service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')

#create semi-uniqe directorys
today = datetime.date.today()
save_directory = f"Elliot-{today.strftime('%Y%m%d')}"
save_directory_videos = f"ElliotEpisodes"

#threads = []
# Create queues for synchronization
story_queue = Queue()
image_queue = Queue()
tts_queue = Queue()
video_queue = Queue() 

# Start story generation in a separate thread
threading.Thread(target=lambda: request_elephant_story(api_key, story_queue)).start()
story_details = story_queue.get()
#threads.append(story_thread)

# Retrieve story details from the queue and start image generation
logging.info("story_details recieved")
image_generator = StoryImageGenerator(api_key)
threading.Thread(target=lambda: image_generator.generate_images_for_story(story_details, image_queue)).start()
#threads.append(image_thread)

# Retrieve images from the queue and start TTS
images = image_queue.get() 
logging.info("images recieved")
ssmlstory = add_ssml_breaks(story_details['story_text'])
threading.Thread(target=lambda: text_to_speech_google(ssmlstory, service_account_file, save_directory, tts_queue)).start()

# Retrieve audio file path from the queue
audio_file = tts_queue.get()
logging.info("audio_file saved")

# Pass the necessary variables to the video creation function
story_text = story_details.get("story_text", "")
story_title = "Elliot, " + story_details['incitement'] +" "+ "in the " + story_details['weather'] + " " + story_details['environment']
print(story_title)
number_of_chapters = story_details['number_of_chapters']
image_paths = [os.path.join(save_directory, f"chapter_{chapter}_image_0.png") 
               for chapter in range(number_of_chapters)] # Adjust the range if the number of images per chapter changes

#Logging the actual data again to be sure the correct data is passed to the video creation
logging.info(image_paths)
logging.info(story_title)
logging.info(audio_file)
threading.Thread(target=lambda: process_video_creation(image_paths, audio_file, story_title, save_directory_videos)).start()

# Retrieve video output path from the queue
output_video_path = video_queue.get()

#print(f"Video created at {output_video_path}")

logging.info("All code ran, mp4 file should be in designated directoy")

