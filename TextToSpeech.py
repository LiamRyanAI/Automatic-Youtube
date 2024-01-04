from google.cloud import texttospeech #we use this to call the google cloud text to speech api
import threading #used for the que
import os #used for saving the audiofile so it can be acces in merge.py where we merge images and audio to make a mp4



def text_to_speech_google(ssmltext, service_account_file, save_directory, tts_queue):
    def _threaded_tts():
        # Instantiates a client
        client = texttospeech.TextToSpeechClient.from_service_account_json(service_account_file)

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(ssml=ssmltext)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Studio-M",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        # Select the type of audio file you want
        audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,  # WAV format
        speaking_rate=0.9
        )

        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Save the audio to a file
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Save the audio to a file in the provided directory
        audio_file = os.path.join(save_directory, "output.mp3")
        with open(audio_file, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to file "{audio_file}"')

            
        tts_queue.put(audio_file)
        return audio_file
        
    # Start the TTS process in a separate thread
    thread = threading.Thread(target=_threaded_tts)
    thread.start()



