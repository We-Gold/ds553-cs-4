from dotenv import load_dotenv
from pydub import AudioSegment
from transformers import pipeline

# Load the HF token from .env
load_dotenv()

import gradio as gr
from huggingface_hub import InferenceClient
from prometheus_client import start_http_server, Counter, Summary

from typing import Optional

USE_LOCAL_TOKEN = True

LOCAL_AUDIO_FILE = "./input.wav"

# Prometheus metrics
REQUEST_COUNTER = Counter('app_requests_total', 'Total number of requests')
SUCCESSFUL_REQUESTS = Counter('app_successful_requests_total', 'Total number of successful requests')
FAILED_REQUESTS = Counter('app_failed_requests_total', 'Total number of failed requests')
HAIKU_REQUESTS = Counter('app_haiku_requests_total', 'Total number of haiku requests')
RAP_REQUESTS = Counter('app_rap_requests_total', 'Total number of rap requests')
ROAST_REQUESTS = Counter('app_roast_requests_total', 'Total number of roast requests')
BRAINROT_REQUESTS = Counter('app_brainrot_requests_total', 'Total number of brainrot requests')
REQUEST_DURATION = Summary('app_request_duration_seconds', 'Time spent processing request')
SPEECH_TO_TEXT_DURATION = Summary('app_speech_to_text_duration_seconds', 'Time spent in speech to text conversion')
TEXT_GENERATION_DURATION = Summary('app_text_generation_duration_seconds', 'Time spent in text generation')


def load_whisper_model():
    return pipeline(
        "automatic-speech-recognition", model="openai/whisper-tiny", 
    )

pipe = load_whisper_model()

def load_audio_file(file):
    try: 
        return AudioSegment.from_file(file)
    except:
        raise gr.Error("Make sure a valid file is already uploaded.")
    
def build_message_prompt(text, mode):
    if mode == "Haiku":
        HAIKU_REQUESTS.inc()
        system_message = f"""Generate a haiku based on the given text.
        A haiku is a short, Japanese poem typically with three lines. 
        It follows a structure of 5 syllables in the first line, 7 in the second, and 5 in the third, 
        totaling 17 syllables. 
        Please respond with only the haiku and no additional text. 
        """
    elif mode == "Rap":
        RAP_REQUESTS.inc()
        system_message = f"""Generate a short rap based on the given text.
        A rap is a rhythmic and rhyming speech that often tells a story or conveys a message.
        Please respond with only the rap and no additional text.
        """
    elif mode == "Roast":
        ROAST_REQUESTS.inc()
        system_message = f"""Generate a roast based on the given text.
        A roast is a humorous and often exaggerated insult or critique, typically delivered in a light-hearted manner.
        Please respond with only the roast and no additional text.
        """
    elif mode == "Brainrot":
        BRAINROT_REQUESTS.inc()
        system_message = f"""Generate a brainrot based on the given text.
        Brainrot consists of poor-quality, humorous and absurd writing that often involves nonsensical use of content about
        2023-2025 Internet slang terms such as 6-7, negative aura, crashout, mogging, gyatt, sigma, skibidi, and rizz.
        Please respond with only the brainrot and no additional text.
        """

    messages = [{"role": "system", "content": system_message}]
    messages.append({"role": "user", "content": text})

    return messages

def respond(file, mode, hf_token: Optional[gr.OAuthToken] = None):
    REQUEST_COUNTER.inc()  
    with REQUEST_DURATION.time():
        try: 
            global pipe

            input_sound = load_audio_file(file)

            # Save audio file in wav format (which is compatible with whisper)
            input_sound.export(LOCAL_AUDIO_FILE, format="wav")

            if pipe is None:
                pipe = load_whisper_model()

            # Convert the audio to text with the whisper tiny model
            with SPEECH_TO_TEXT_DURATION.time():
                response = pipe(LOCAL_AUDIO_FILE)

            text_result = response["text"]

            messages = build_message_prompt(text_result, mode)

            if USE_LOCAL_TOKEN:
                import os
                hf_token = {}
                token = os.getenv("HF_TOKEN")
            elif hf_token is None or not getattr(hf_token, "token", None):
                yield "⚠️ Please log in with your Hugging Face account first."
                return
            else:
                token = hf_token.token
            
            client = InferenceClient(token=token, model="openai/gpt-oss-20b")

            response = ""

            # Generate text with streaming
            with TEXT_GENERATION_DURATION.time():
                for chunk in client.chat_completion(
                    messages,
                    stream=True
                ):
                    choices = chunk.choices
                    token = ""
                    if len(choices) and choices[0].delta.content:
                        token = choices[0].delta.content
                    response += token

                    yield response

            SUCCESSFUL_REQUESTS.inc()
        except Exception as e:
            FAILED_REQUESTS.inc()
            yield f"⚠️ An error occurred: {str(e)}"
            return
    
# Fancy styling
CSS = """
#main-container {
    background-color: #f0f0f0;
    font-family: 'Arial', sans-serif;
    width: 700px;
}
.gradio-container {
    width: 700px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-radius: 10px;
}
.gr-button {
    background: #8e44ad;
    color: white;
    border-radius: 50px;
    padding: 12px 24px;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
}
.gr-button:hover {
    background: #732d91;
    transform: translateY(-2px);
}
.gr-slider input {
    color: #4CAF50;
}
.gr-chat {
    font-size: 16px;
}
#title {
    text-align: center;
    font-size: 2em;
    margin-bottom: 20px;
    color: #333;
}
"""

with gr.Blocks(css=CSS) as demo:
    with gr.Row():
        gr.Markdown("<h1 style='text-align: center; color: black'> Well-Versed AI </h1>")
        if not USE_LOCAL_TOKEN:
            gr.LoginButton()
    with gr.Row():
        mic = gr.Audio(label="🎙️ Microphone or Upload (< 30 seconds)", type="filepath")
    with gr.Row():
        submit = gr.Button("Submit")
    with gr.Row():
        style_select = gr.Radio(["Haiku", "Rap", "Roast", "Brainrot"], label="Select output style", value="Haiku")
    with gr.Row():
        output = gr.Textbox(label="Output", lines=5, interactive=False)

    submit.click(fn=respond, inputs=[mic,style_select], outputs=output)
  

if __name__ == "__main__":
    start_http_server(8000)  # Expose metrics on port 8000
    demo.launch()
