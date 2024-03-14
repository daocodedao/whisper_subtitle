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
videoSrcPath = "./sample/simple5-cut3.mp4"
outVideoDir = f"./out/{processId}/"

outVideoPath = os.path.join(outVideoDir, f"{processId}-cartoon.mp4")
videoFpsFixPath = os.path.join(outVideoDir, f"{processId}-fps-fix.mp4")

frameOutDir = os.path.join(outVideoDir, "frames")
shutil.rmtree(frameOutDir, ignore_errors=True)
os.makedirs(frameOutDir, exist_ok=True)

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

framePaths = Util.get_image_paths_from_folder(frameOutDir)
if len(framePaths) > 0:
    api_logger.info(f"无需解压视频帧 {frameOutDir}")
else:
    api_logger.info(f"解压视频帧 {videoSrcPath}")
    framePaths = Util.extract_video_to_frames(videoSrcPath, frameOutDir)
api_logger.info(f"共有 {len(framePaths)} 帧")

api_logger.info("加载模型")
model_id = "instruction-tuning-sd/cartoonizer"
pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, use_auth_token=True
).to("cuda")
# 优化速度
torch.backends.cudnn.benchmark = True
pipeline.enable_xformers_memory_efficient_attention()

# image_path = "./sample/WX20240314-161847.png"
result_frames = []
for idx, image_path in enumerate(framePaths) :
    image = load_image(image_path)
    api_logger.info(f"卡通化 {image_path}")
    image = pipeline("Cartoonize the following image", image=image, num_inference_steps=5).images[0]
    cartoonImagePath = os.path.join(cartoonOutDir, f"cartoon{idx}.png")
    image.save(cartoonImagePath)
    api_logger.info(f"卡通帧保存到 {cartoonImagePath}")
    result_frames.append(cartoonImagePath)

final_vid = Util.create_video(result_frames, kFixedFps, outVideoPath)
api_logger.info(f"视频保存到 {outVideoPath}")
# num_inference_steps 默认100
# image_guidance_scale 默认 1.5 , 接近原图的参数，越高越接近，最少1
# guidance_scale 默认 7.5, 更高的引导标度值鼓励模型生成与文本紧密链接的图像
# 以上3个参数会影响推理速度，

# images = pipe(prompt, image=image, num_inference_steps=10, image_guidance_scale=1).images
# edit = pipe(prompt, image=image, num_inference_steps=20, image_guidance_scale=1.5, guidance_scale=7).images[0]
