import re #used to find the chapters and their names
import openai #interacti with openaI
import requests #used to work the image url we get back from openai 
import os #used for saving files on our local machine
import threading #used for queues
import datetime #used for getting the time of day to create semi-uniqe folders for storage 
from PIL import Image #used to read the image from the url with the help from #requests #BytesIO
from io import BytesIO #used to read the image from the url with the help from #requests #Image


dall_e_model = "dall-e-3" #Dall-E model
style_description = "Gen ID: nLvEWe9FvRW5U4MI" #Gen ID for the image style we want - Watch this video to see how to get you Gen ID:



class StoryImageGenerator: #Class to contain image generation functions
    
    #Character descriptions to keep the essene of each character intact between images and stories
    character_descriptions = {
    "Elliot": "Elliot the Elegant Elephant, a cheerful and kind elephant with large, friendly blue eyes, a big smile, and a stylish bow tie,",
    "Oliva": "Olivia the Observant Owl, with piercing intelligent eyes, soft, speckled feathers,",
    "Gaia": "Gaia the Graceful Gazelle, an elegant gazelle with long, slender legs, a sleek coat, and a gentle demeanor,",
    "Fria": "Fria the Fearless Fox, an adventurous fox with bright, curious eyes, a vibrant red fur coat, and a bushy tail,",
    "Pelle": "Pelle the Playful Penguin, a friendly penguin with a shiny, black and white coat, a charming waddle, and an infectious laugh,",
    "Malthe": "Malthe the Mighty Moose, a strong and majestic moose with impressive antlers, a sturdy build,",
    "Tobias the Thoughtful Turtle": "Tobias the Thoughtful Turtle, a slow-moving turtle with a wise and contemplative expression.",
    "Liam": "Liam the Loyal Lion, a strong and majestic lion with a commanding presence.",
    "Sille": "Sille the Swift Squirrel, a nimble and agile squirrel with a sleek, furry coat.",
    "Beastamor": "Beastamor the Brave Bear, a formidable and courageous bear with a fearless demeanor.",
    "Thomas": "Thomas the Thoughtful Tiger, a pensive and reflective tiger with thoughtful eyes.",
    "Patricia": "Patricia the Prancing Peacock, a dazzling and flamboyant peacock with vibrant feathers.",
    "Granddad": "Granddad the Gentle Gorilla, a kind and wise gorilla with a gentle and caring presence.",
    "Lisbeth": "Lisbeth the Lively Lemur, an energetic and playful lemur with a lively disposition.",
    "Ole": "Ole the Oracle Owl, a perceptive owl with sharp, watchful eyes.",
    "Rob": "Rob the Resourceful Raccoon, a clever raccoon with a resourceful and cunning nature.",
    "Albert": "Albert the Amazing Armadillo, a unique armadillo with a tough exterior and a distinctive appearance.",
    "Victor": "Victor the Vivacious Vulture, a lively vulture with a spirited and adventurous look.",
    "Marie": "Marie the Magnificent Macaw, a vibrant macaw with colorful plumage and a lively personality.",
    "Anne": "Anne the Agile Anteater, a nimble anteater with a long, agile tongue for catching insects.",
    "Mum": "Mum the Loving Mother, a caring and nurturing mother figure with a warm and affectionate demeanor."
    # Add descriptions for other characters here
    }
    
    def __init__(self, api_key):
        # Create an OpenAI client with the provided API key
        self.client = openai.OpenAI(api_key=api_key)

    def extract_chapter_names(self, story_text):
        # Extract chapter names from the story text
        chapters = re.findall(r'Chapter \d+: (.+)', story_text)
        return chapters

    def create_image_prompts(self, friend1, friend2, environment, weather, incitement, style_description):
        elliot_description = self.character_descriptions["Elliot"] #Since Elliot is always in the story we can hardcode his name here.
        friend_description1 = self.character_descriptions.get(friend1, friend1) #Gets the character description for friend1# Default to the friend's name if not found
        friend_description2 = self.character_descriptions.get(friend2, friend2) #Gets the character description for friend1# Default to the friend's name if not found
        #Here you can have multiple prompts or just the one you prefer - i went with just one. 
        prompts = [
            #f"{chapter_name} - {elliot_description}, {friend_description1} and {friend_description2} walking in a {weather} {environment}. style:{style_description}.",
            f"{elliot_description}, {friend_description1} and {friend_description2} {incitement} in a {weather} {environment}. style:{style_description}.",
            #f"{chapter_name} - {elliot_description} and {friend_description} moving on from the adventure a {weather}{environment}. style:{style_description}."
            #f"Add prompts as you see fit" - note openai Dall-e might cut you off if you generate to many images per hour
        ]
        print(prompts) #Print the prompts to terminal so we can follow and see what they are like we want them
        return prompts


    def generate_images(self, prompts):
        #print("generate was called") #used to for testing
        images = [] #Variable to keep all image urls
        for prompt in prompts: # Generate an image using the OpenAI client #this will handle multiple prompts and images if you made more
            response = self.client.images.generate(model=dall_e_model, prompt=prompt, size="1792x1024") #Dall-e model taking from variable at the start, the prompt, and size()
            #print("API response:", response) #used for testing
            
            # Extract URLs from the response
            for img in response.data:  #data contains the list of images
                if img.url:  # Check if URL is available
                    images.append(img.url)
                else:
                    print("No URL in image response")
        return images

    #this is the main function which is called from our main.py
    def generate_images_for_story(self, story_details, image_queue):
        def _threaded_generate_and_save(): #start thread
            #extract important information for our prompt generations
            chapter_names = self.extract_chapter_names(story_details["story_text"])
            friend1 = story_details["friend1"]
            friend2 = story_details["friend2"]
            environment = story_details["environment"]
            weather = story_details["weather"]
            incitement = story_details["incitement"]

            story_images = {} #variable for our images
            for chapter_index, chapter in enumerate(chapter_names):
                prompts = self.create_image_prompts(friend1, friend2, environment, weather, incitement, style_description)
                image_urls = self.generate_images(prompts)
                story_images[chapter] = image_urls

                # Ensure images for each chapter are saved within this loop
                for image_index, image_url in enumerate(image_urls):
                    self.save_image(image_url, chapter_index, image_index)

            image_queue.put(story_images) #return our images to the queue so the code can move on

        thread = threading.Thread(target=_threaded_generate_and_save)
        thread.start()



    #Saving images
    def save_image(self, image_url, chapter_index, image_index):
        if image_url:
            # Fetch the image from the URL
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))

            # Create a directory name based on the current date
            today = datetime.date.today()
            save_directory = f"Elliot-{today.strftime('%Y%m%d')}"

            # Ensure the directory exists
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # Construct a unique image path using chapter and image indices
            img_path = os.path.join(save_directory, f'chapter_{chapter_index}_image_{image_index}.png')
        
            # Save the image
            img.save(img_path)
            print(f"Image saved to {img_path}")
        else:
            print("Image URL is missing")

    def save_images_for_chapter(self, chapter_images):
        #print("save_images_for_chapter method called")
        for index, image_response in enumerate(chapter_images):
            # Assuming each 'image_response' is an 'ImagesResponse' object with a 'data' attribute
            if hasattr(image_response, 'data') and image_response.data:
                # Extract the URL from the first image in the data list
                image_url = image_response.data[0].url if image_response.data[0] else None
                self.save_image(image_url, image_count=index)
            else:
                print("No image data found")

