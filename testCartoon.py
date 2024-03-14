import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
from diffusers.utils import load_image
import os
from utils.util import Util
import shutil
from utils.logger_settings import api_logger
import argparse
import moviepy.editor as mp

import time

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'
api_logger.info("准备开始")


api_logger.info("---------加载模型")
model_id = "instruction-tuning-sd/cartoonizer"
pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, use_auth_token=True
).to("cuda")
# 优化速度
# torch.backends.cudnn.benchmark = True
# pipeline.enable_xformers_memory_efficient_attention()
# pipeline.enable_model_cpu_offload()
image_path = "/data/work/translate/BiB9YykxoZw/frames/17.png"
image = load_image(image_path)
num_inference_steps = 100
image_guidance_scale = 1.5
guidance_scale = 7.5 
image = pipeline("Cartoonize the following image", 
                    image=image,
                    num_inference_steps=num_inference_steps,
                    image_guidance_scale=image_guidance_scale,
                    guidance_scale=guidance_scale
                    ).images[0]
cartoonImagePath = "/data/work/translate/BiB9YykxoZw/cartoon/17.png"
image.save(cartoonImagePath)


# num_inference_steps 默认100
# image_guidance_scale 默认 1.5 , 接近原图的参数，越高越接近，最少1
# guidance_scale 默认 7.5, 更高的引导标度值鼓励模型生成与文本紧密链接的图像
# 以上3个参数会影响推理速度，

# images = pipe(prompt, image=image, num_inference_steps=10, image_guidance_scale=1).images
# edit = pipe(prompt, image=image, num_inference_steps=20, image_guidance_scale=1.5, guidance_scale=7).images[0]

# /data/work/aishowos/whisper_subtitle/venv/bin/python utilCartoon.py -v '/data/work/translate/BiB9YykxoZw/BiB9YykxoZw-cn-subtitle.mp4' -i 'BiB9YykxoZw'