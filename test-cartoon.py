import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
from diffusers.utils import load_image
import os
from utils.util import Util
import shutil
from utils.logger_settings import api_logger
import argparse
import moviepy.editor as mp
import PIL
import time
import random

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'
api_logger.info("准备开始")


api_logger.info("---------加载模型")
model_id = "timbrooks/instruct-pix2pix"
# model_id = "instruction-tuning-sd/cartoonizer"
pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, use_auth_token=True
).to("cuda")
# 优化速度
# torch.backends.cudnn.benchmark = True
# pipeline.enable_xformers_memory_efficient_attention()
# pipeline.enable_model_cpu_offload()
fileIdx = 37
image_path = f"/data/work/translate/BiB9YykxoZw/frames/{fileIdx}.png"
image = load_image(image_path)

num_inference_steps = 20
image_guidance_scale = 1
guidance_scale = 7

negative_prompt="The entire picture is black"
image = pipeline("Cartoonize the following image", 
                    image=image,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    image_guidance_scale=image_guidance_scale,
                    guidance_scale=guidance_scale
                    ).images[0]
cartoonImagePath = f"/data/work/translate/BiB9YykxoZw/cartoon/{fileIdx}.png"
image.save(cartoonImagePath)

k10K = 100 * 1024
kMinFileSizeK = k10K

for tryIdx in range(100):
    fileSize = os.path.getsize(cartoonImagePath) 
    if fileSize < kMinFileSizeK:
        num_inference_steps = random.randint(2, 100)
        image_guidance_scale = 1.5
        guidance_scale = 7 
        api_logger.error(f"文件 {fileSize} < {kMinFileSizeK} 生成错误, 重试{tryIdx}次  num_inference_steps={num_inference_steps}")

        image = pipeline("Cartoonize the following image", 
                    image=image,
                    num_inference_steps=num_inference_steps,
                    image_guidance_scale=image_guidance_scale,
                    guidance_scale=guidance_scale
                    ).images[0]
        cartoonImagePath = f"/data/work/translate/BiB9YykxoZw/cartoon/{fileIdx}.png"
        image.save(cartoonImagePath)
    else:
        break

api_logger.info(f"完成")

# num_inference_steps 默认100
# image_guidance_scale 默认 1.5 , 接近原图的参数，越高越接近，最少1
# guidance_scale 默认 7.5, 更高的引导标度值鼓励模型生成与文本紧密链接的图像
# 以上3个参数会影响推理速度，

# images = pipe(prompt, image=image, num_inference_steps=10, image_guidance_scale=1).images
# edit = pipe(prompt, image=image, num_inference_steps=20, image_guidance_scale=1.5, guidance_scale=7).images[0]

# /data/work/aishowos/whisper_subtitle/venv/bin/python utilCartoon.py -v '/data/work/translate/BiB9YykxoZw/BiB9YykxoZw-cn-subtitle.mp4' -i 'BiB9YykxoZw'