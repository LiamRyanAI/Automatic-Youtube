from moviepy.editor import concatenate_videoclips, ImageClip, AudioFileClip #make sure to install moviepy with pip install movepie
import os #used again for accesting our local machin 
import re #used for accesing the story title and removing "harmful" characters
import logging #used for logging to ensure the code is running as planned - especially usefull when the full automation is running and you want to see what has been going on

# Constants
CHAPTER_DURATION = 50  # Duration of each chapter in seconds 
IMAGES_PER_CHAPTER = 1  # Number of images per chapter #this code is not super smart so it doenst account for you increasing image prompts - this could be coded or just remember to change number here

#gives each image a duration
def create_chapter_clips(image_paths):
    clips = []
    if len(image_paths) == 0:
        print("No images provided to create video clips.")
        return clips

    # Assuming each image corresponds to one chapter
    for img_path in image_paths:
        clip = ImageClip(img_path).set_duration(CHAPTER_DURATION)
        clips.append(clip)

    return clips

#the function that makes and safes the video
def make_video(chapters_clips, audio_path, story_title, save_directory):
    # Replace or remove characters not allowed in filenames
    safe_title = re.sub(r'[\\/*?"<>|:.]', ' ', story_title)

    # Ensure that the formatted title has the .mp4 extension
    formatted_title = safe_title + ".mp4"
    output_path = os.path.join(save_directory, formatted_title)  # Save in the provided directory

    final_clip = concatenate_videoclips(chapters_clips, method="compose")
    audio = AudioFileClip(audio_path)
    final_video = final_clip.set_audio(audio)

    final_video.write_videofile(output_path, codec='libx264', fps=1)

    return output_path

#function called from our main.py
def process_video_creation(image_paths, audio_path, story_title, save_directory):
    logging.info("Starting video creation process")
    chapters_clips = create_chapter_clips(image_paths)
    output_video_path = make_video(chapters_clips, audio_path, story_title, save_directory)

    # Add metadata to the video
    # add_metadata_to_video(output_video_path, metadata)
    return output_video_path
   

