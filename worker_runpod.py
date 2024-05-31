import torch
import os, sys, json, subprocess, requests, runpod

from scripts.gradio.i2v_test_application import Image2Video
from diffusers.utils import load_image
import numpy as np

discord_token = os.getenv('com_camenduru_discord_token')
web_uri = os.getenv('com_camenduru_web_uri')
web_token = os.getenv('com_camenduru_web_token')

sys.path.insert(1, os.path.join(sys.path[0], 'lvdm'))
image2video = Image2Video('./tmp/', resolution='320_512')

def generate(input):
    values = input["input"]
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

    result = i2v_output_video

    response = None
    try:
        source_id = values['source_id']
        del values['source_id']
        source_channel = values['source_channel']     
        del values['source_channel']
        job_id = values['job_id']
        del values['job_id']
        files = {f"video.mp4": open(result, "rb").read()}
        payload = {"content": f"{json.dumps(values)} <@{source_id}>"}
        response = requests.post(
            f"https://discord.com/api/v9/channels/{source_channel}/messages",
            data=payload,
            headers={"authorization": f"Bot {discord_token}"},
            files=files
        )
        response.raise_for_status()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if os.path.exists(result):
            os.remove(result)

    if response and response.status_code == 200:
        try:
            payload = {"jobId": job_id, "result": response.json()['attachments'][0]['url']}
            requests.post(f"{web_uri}/api/notify", data=json.dumps(payload), headers={'Content-Type': 'application/json', "authorization": f"{web_token}"})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            return {"result": response.json()['attachments'][0]['url']}
    else:
        return {"result": "ERROR"}

runpod.serverless.start({"handler": generate})