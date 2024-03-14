import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
from diffusers.utils import load_image
import os
from utils.util import Util
import shutil
from utils.logger_settings import api_logger

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'

processId = "simple5"
videoSrcPath = "./sample/simple5.mp4"
outVideoDir = f"./out/{processId}/"

videoFpsFixPath = os.path.join(outVideoDir, f"{processId}-fps-fix.mp4")

frameOutPath = os.path.join(outVideoDir, "frames")
shutil.rmtree(frameOutPath, ignore_errors=True)
os.makedirs(frameOutPath, exist_ok=True)

cartoonOutDir = os.path.join(outVideoDir, "cartoon")
shutil.rmtree(cartoonOutDir, ignore_errors=True)
os.makedirs(cartoonOutDir, exist_ok=True)

kFixedFps = 24
api_logger.info("---------调整POSEFPS")
src_fps = Util.get_fps(videoSrcPath)
api_logger.info(f"videoSrcPath={videoSrcPath} src_fps={int(src_fps)}")
if int(src_fps) > kFixedFps:
    if not os.path.exists(videoFpsFixPath): 
        api_logger.info(f"原视频FPS需要调整为{kFixedFps}")
        Util.changeVideoFps(videoSrcPath, kFixedFps, videoFpsFixPath)
        api_logger.info(f"fps调整完成")
    
    videoSrcPath = videoFpsFixPath

api_logger.info(f"现在的videoSrcPath={videoSrcPath}")


api_logger.info(f"解压视频帧 {videoSrcPath}")
framePaths = Util.extract_video_to_frames(videoSrcPath, frameOutPath)
api_logger.info(f"共有 {len(framePaths)} 帧")
api_logger.info("加载模型")
model_id = "instruction-tuning-sd/cartoonizer"
pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, use_auth_token=True
).to("cuda")

# image_path = "./sample/WX20240314-161847.png"
for idx, image_path in enumerate(framePaths) :
    image = load_image(image_path)
    api_logger.info(f"卡通化 {image_path}")
    image = pipeline("Cartoonize the following image", image=image).images[0]
    cartoonImagePath = os.path.join(cartoonOutDir, f"cartoon{idx}.png")
    image.save(cartoonImagePath)
    api_logger.info(f"卡通帧保存到 {cartoonImagePath}")

