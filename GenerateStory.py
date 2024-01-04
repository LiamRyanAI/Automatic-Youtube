import random #we use this for getting a random Story variable
import threading #we use this for Queing
from openai import OpenAI #we use this to interact with the OpenAI API

#Story Variables
friends = [
    "Olivia the Observant Owl", "Gaia the Graceful Gazelle", "Fria the Fearless Fox", "Pellé the Playful Penguin", "Malté the Mighty Moose",
    "Tobias the Thoughtful Turtle", "Liam the Loyal Lion", "Sille the Swift Squirrel", "Beastamor the Brave Bear", "Thomas the Thoughtful Tiger",
    "Patricia the Prancing Peacock", "Granddad the Gentle Gorilla", "Lisbeth the Lively Lemur", "Ole the Observant Owl", "Rob the Resourceful Raccoon", 
    "Albert the Amazing Armadillo", "Victor the Vivacious Vulture.", "Marie the Magnificent Macaw.", "Anne the Agile Anteater", "Mum the Loving Mother"
]
environments = [
    "jungle", "mountain", "river", "forest", "desert",
    "ocean", "volcano", "canyon", "savannah", "arctic",
    "city", "valley", "swamp", "meadow", "cave"
]
themes = [
    "honesty","friendship","love","courage","kindness","empathy","patience","loyalty","humility","gratitude",
    "generosity","respect","integrity","perseverance","compassion","wisdom","responsibility",
    "fairness","forgiveness","optimism"
]
weathers = [
    "sunny", "Rainy", "Cloudy", "Snowy", "Windy",
    "Stormy", "Foggy", "Enchanted", "Misty", "Dusty", "Icy", "magical"
]
incitements = [
    "discovers a mysterious, glowing stone in the forest",
    "finds an ancient map hidden behind a loose brick in an old wall",
    "witnesses a meteor crash-landing in the backyard",
    "uncovers a secret passage behind a bookshelf in their home",
    "receives a mysterious message in a bottle washed up on the shore",
    "stumbles upon a hidden cave filled with ancient artifacts",
    "spots a rare, mythical creature in the wilderness",
    "finds a magical amulet in an old attic",
    "receives an unexpected invitation to a hidden school of magic",
    "discovers an old diary revealing a family secret",
    "wakes up to find the town mysteriously deserted",
    "sees a strange light hovering over the town at night",
    "finds a peculiar device with unknown powers in a thrift shop",
    "witnesses a total solar eclipse that triggers strange events",
    "discovers a plant that grows overnight into a giant beanstalk",
    "finds a talking animal that seeks help",
    "uncovers a conspiracy in a seemingly perfect community",
    "stumbles upon a treasure map in an old library book",
    "discovers they can travel through mirrors into different worlds",
    "witnesses a historical figure appearing in modern times"
]

#the main function for story generation
def request_elephant_story(api_key, story_queue):
    def _threaded_story_generation():
        client = OpenAI(api_key=api_key)

        # Randomly select one element from each category
        theme = random.choice(themes)
        friend1 = random.choice(friends)
        friend2 = random.choice(friends)
        while friend2 == friend1:
            friend2 = random.choice(friends)
        environment = random.choice(environments)
        weather = random.choice(weathers)
        incitement = random.choice(incitements)
        

        # Construct the prompt max 4079 tokens
        prompt = (f"Write a three-chapter children's story about Elliot the Elegant Elephant. "
                f"Chapter format = Chapter #: Characters, {incitement}, in the {weather} {environment}. "
                f"Theme: {theme}. Main characters: Elliot, {friend1} and {friend2}. "
                f"Setting: A {weather} {environment}. They {incitement}. "
                f"End with: The End.")

        params = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 4000 #max 4079 tokens
        } 
        
        print(prompt) #To see in terminal what our prompt looks like.
        completion = client.completions.create(**params) #The call to Openai API
    
        if completion:
            story_text = completion.choices[0].text #Is not accesed directly, but it is used via the result
            result = {
                "story_text": completion.choices[0].text,
                "friend1": friend1,
                "friend2" : friend2,
                "environment": environment,
                "weather": weather,
                "incitement": incitement,
                "number_of_chapters": 3
            }
        else:
            result = {"story_text": "An error occurred.", "friend": "", "environment": ""}

        story_queue.put(result)  # Call the callback function with the result

    # Start the story generation in a separate thread
    thread = threading.Thread(target=_threaded_story_generation)
    thread.start()
    
    #function for adding SSML which is a way to tell the text-to-speech to add a pause instead of saying "period" and so on.
    #feel free to add other replacements you find important.
def add_ssml_breaks(text, break_time1='500ms', break_time2='250ms'):

    # Replace punctuation with breaks
    text = text.replace("...", f'.<break time="{break_time1}"/>')
    punctuations = {'.': f'.<break time="{break_time1}"/>',
                    ';': f';<break time="{break_time2}"/>',
                    ':': f':<break time="{break_time1}"/>'}

    for punctuation, replacement in punctuations.items():
        text = text.replace(punctuation, replacement)

    # Replace line breaks with breaks
    text = text.replace('\n', f'<break time="{break_time2}"/>')
    
    # Wrap the text in <speak> tags
    ssml_text = f"<speak>{text}</speak>"

    return ssml_text

