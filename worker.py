import torch
import os, sys, json
from scripts.gradio.i2v_test_application import Image2Video
from diffusers.utils import load_image
import gradio as gr
import numpy as np

sys.path.insert(1, os.path.join(sys.path[0], 'lvdm'))
image2video = Image2Video('/tmp/', resolution='320_512')

@torch.inference_mode()
def generate(command):
    values = json.loads(command)
    
    i2v_input_text = values['i2v_input_text']
    i2v_steps = values['i2v_steps']
    i2v_cfg_scale = values['i2v_cfg_scale']
    i2v_eta = values['i2v_eta']
    i2v_motion = values['i2v_motion']
    i2v_seed = values['i2v_seed']

    i2v_input_image1 = values['i2v_input_image1']
    i2v_input_image1 = np.array(load_image(i2v_input_image1))
    i2v_input_image2 = values['i2v_input_image2']
    i2v_input_image2 = np.array(load_image(i2v_input_image2))

    i2v_output_video = image2video.get_image(i2v_input_image1, i2v_input_text, i2v_steps, i2v_cfg_scale, i2v_eta, i2v_motion, i2v_seed, i2v_input_image2)
    return i2v_output_video

with gr.Blocks(css=".gradio-container {max-width: 544px !important}", analytics_enabled=False) as demo:
    with gr.Row():
      with gr.Column():
          textbox = gr.Textbox(show_label=False, 
          value="""
                {
                    "i2v_input_image1":"https://huggingface.co/camenduru/assets/resolve/main/034133.jpg", 
                    "i2v_input_text":"an anime scene", 
                    "i2v_steps":50, 
                    "i2v_cfg_scale":7.5, 
                    "i2v_eta":1, 
                    "i2v_motion":10, 
                    "i2v_seed":789, 
                    "i2v_input_image2":"https://huggingface.co/camenduru/assets/resolve/main/034147.jpg"
                }
          """)
          button = gr.Button()
    with gr.Row(variant="default"):
        output_video = gr.Video(
            show_label=False,
            interactive=False,
            height=320,
            width=512,
            elem_id="output_video",
        )

    button.click(fn=generate, inputs=[textbox], outputs=[output_video])

import os
PORT = int(os.getenv('server_port'))
demo.queue().launch(inline=False, share=False, debug=True, server_name='0.0.0.0', server_port=PORT)
