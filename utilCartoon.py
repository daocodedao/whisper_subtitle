import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
from diffusers.utils import load_image
import os
from utils.util import Util
import shutil
from utils.logger_settings import api_logger

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'


videoPosePath = "./sample/simple5.mp4"
frameOutPath = "./out/simple5/frames/"
shutil.rmtree(frameOutPath, ignore_errors=True)
os.makedirs(frameOutPath, exist_ok=True)

cartoonOutDir = "./out/simple5/cartoon5/"
shutil.rmtree(frameOutPath, ignore_errors=True)
os.makedirs(frameOutPath, exist_ok=True)

api_logger.info(f"解压视频帧 {videoPosePath}")
framePaths = Util.extract_video_to_frames(videoPosePath, frameOutPath)
api_logger.info(f"共有 {len(framePaths)} 帧")
api_logger.info("加载模型")
model_id = "instruction-tuning-sd/cartoonizer"
pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16, use_auth_token=True
).to("cuda")

# image_path = "./sample/WX20240314-161847.png"
for idx, image_path in enumerate(framePaths) :
    image = load_image(image_path)
    api_logger.info(f"卡通化 {image_path}")
    image = pipeline("Cartoonize the following image", image=image).images[0]
    cartoonImagePath = os.path.join(cartoonOutDir, f"cartoon{idx}.png")
    image.save(cartoonImagePath)
    api_logger.info(f"卡通帧保存到 {cartoonImagePath}")

