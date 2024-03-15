import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
from diffusers.utils import load_image
import os
from utils.util import Util
import shutil
from utils.logger_settings import api_logger
import argparse
import moviepy.editor as mp
from pathlib import Path
import subprocess
from utils.Tos import TosService
from utils.notify import NotifyUtil

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'
api_logger.info("准备开始")

globalPipeline = None
# 10K
k10K = 10 * 1024
kMinFileSizeK = k10K

KInferenceStep = 10

def generateImage(framePaths):
    global globalPipeline,kMinFileSizeK
    result_frames = []
    error_frames = []
    for idx, image_path in enumerate(framePaths) :
        image = load_image(image_path)
        refImageName = Path(image_path).stem

        # kMaxTryCount = 3
        # for tryIdx in range(kMaxTryCount):
        num_inference_steps = KInferenceStep
        image_guidance_scale = 1.5
        guidance_scale = 7.5 
        api_logger.info(f"卡通化 {image_path}")
        # api_logger.info(f"生成 inference_steps={num_inference_steps} image_guidance_scale={image_guidance_scale} guidance_scale={guidance_scale}")

        image = globalPipeline("Cartoonize the following image", 
                        image=image,
                        num_inference_steps=num_inference_steps,
                        image_guidance_scale=image_guidance_scale,
                        guidance_scale=guidance_scale
                        ).images[0]
        cartoonImagePath = os.path.join(cartoonOutDir, f"{refImageName}.jpg")
        image.save(cartoonImagePath)
        api_logger.info(f"卡通帧保存到 {cartoonImagePath}")

        fileSize = os.path.getsize(cartoonImagePath) 
        if fileSize < kMinFileSizeK:
            api_logger.error(f"文件 {fileSize} < {kMinFileSizeK} 生成错误")
            error_frames.append(image_path)
            # if os.path.exists(cartoonImagePath):
            #     os.remove(cartoonImagePath)

            preCartoonImagePath = os.path.join(cartoonOutDir, f"{int(refImageName)-1}.jpg")
            shutil.copyfile(preCartoonImagePath, cartoonImagePath)
            api_logger.info(f"复制上一帧 {preCartoonImagePath} 到 {cartoonImagePath}")

        elif kMinFileSizeK == k10K:
            # 有的图片黑色的，几十K，比正常图片小太多了
            kMinFileSizeK = fileSize/2


        if os.path.exists(cartoonImagePath):
            result_frames.append(cartoonImagePath)
    return result_frames, error_frames


program = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))
program.add_argument('-v', '--videoPath', help='videoPath',
                     dest='videoPath', type=str, default='')
program.add_argument('-i', '--processId', help='process Id',
                     dest='processId', type=str, default='')
program.add_argument('-a', '--addVoice', help='is need add voice, value: add,noadd',
                     dest='addVoice', type=str, default='add')
program.add_argument('-u', '--upload', help='is need upload to cloud, value: upload,noupload',
                     dest='upload', type=str, default='upload')

args = program.parse_args()

print(args)

kFixedFps = 24
kMaxWidthOrHeight = 720

videoSrcPath = args.videoPath
processId = args.processId
addVoice = args.addVoice
needUploadTos = args.upload

api_logger.info(f"videoSrcPath: {videoSrcPath} processId={processId}  addVoice={addVoice} needUploadTos={needUploadTos}")

outVideoDir = os.path.dirname(videoSrcPath)
outVideoMutePath = os.path.join(outVideoDir, f"{processId}-cartoon-mute.mp4")
outVideoPath = os.path.join(outVideoDir, f"{processId}-cartoon.mp4")
outAudioPath= os.path.join(outVideoDir, f"{processId}.wav")
videoFpsFixPath = os.path.join(outVideoDir, f"{processId}-fps-{kFixedFps}.mp4")
videoSizeFixPath = os.path.join(outVideoDir, f"{processId}-{kMaxWidthOrHeight}.mp4")


if addVoice == "add":
    api_logger.info("需要原视频声音")
    if not os.path.exists:
        api_logger.info(f"从视频剥离音频文件 {outAudioPath}")
        command = f"ffmpeg -y -i {videoSrcPath} -vn -acodec pcm_f32le -ar 44100 -ac 2 {outAudioPath}"
        api_logger.info(command)
        if os.path.exists(outAudioPath):
            api_logger.info(f"从视频剥离音频文件成功 {outAudioPath}")
    else:
        api_logger.info(f"无需剥离音频，已经存在 {outAudioPath}")

                        

frameOutDir = os.path.join(outVideoDir, "frames")
shutil.rmtree(frameOutDir, ignore_errors=True)
os.makedirs(frameOutDir, exist_ok=True)

cartoonOutDir = os.path.join(outVideoDir, "cartoon")
shutil.rmtree(cartoonOutDir, ignore_errors=True)
os.makedirs(cartoonOutDir, exist_ok=True)


api_logger.info("---------调整视频帧率FPS")
src_fps = Util.get_fps(videoSrcPath)
api_logger.info(f"videoSrcPath={videoSrcPath} src_fps={int(src_fps)}")
if int(src_fps) > kFixedFps:
    if not os.path.exists(videoFpsFixPath): 
        api_logger.info(f"原视频FPS需要调整为{kFixedFps}")
        Util.changeVideoFps(videoSrcPath, kFixedFps, videoFpsFixPath)
        api_logger.info(f"fps调整完成")
    
    videoSrcPath = videoFpsFixPath

api_logger.info(f"现在的videoSrcPath={videoSrcPath}")

clip = mp.VideoFileClip(videoSrcPath)
width = clip.w
height = clip.h
api_logger.info(f"---------判断视频是否要改尺寸 宽={width} 高={height}")

if os.path.exists(videoSizeFixPath):
    videoSrcPath = videoSizeFixPath
else:
    if width > height:
        if width > kMaxWidthOrHeight:
            clip_resized = clip.resize(width=kMaxWidthOrHeight)
            clip_resized.write_videofile(videoSizeFixPath)
            videoSrcPath = videoSizeFixPath
            api_logger.info(f"横屏视频，视频宽度超过{kMaxWidthOrHeight}，已压缩 {videoSizeFixPath}")
    else:
        if height > kMaxWidthOrHeight:
            clip_resized = clip.resize(height=kMaxWidthOrHeight)
            clip_resized.write_videofile(videoSizeFixPath)
            videoSrcPath = videoSizeFixPath
            api_logger.info(f"竖屏视频，视频高度超过{kMaxWidthOrHeight}，已压缩 {videoSizeFixPath}")


api_logger.info("---------解压视频帧")
framePaths = Util.get_image_paths_from_folder(frameOutDir)
if len(framePaths) > 0:
    api_logger.info(f"无需解压视频帧 {frameOutDir}")
else:
    api_logger.info(f"解压视频帧 {videoSrcPath}")
    framePaths = Util.extract_video_to_frames(videoSrcPath, frameOutDir)
api_logger.info(f"共有 {len(framePaths)} 帧")

api_logger.info("---------加载模型")
model_id = "instruction-tuning-sd/cartoonizer"
# model_id = "timbrooks/instruct-pix2pix"
globalPipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, use_auth_token=True
).to("cuda")
# 优化速度
torch.backends.cudnn.benchmark = True
globalPipeline.enable_xformers_memory_efficient_attention()
# globalPipeline.enable_model_cpu_offload()


total_cartoon_frames, error_video_frames = generateImage(framePaths)
api_logger.info(f"生成结束，成功：{len(total_cartoon_frames)}帧， 失败：{len(error_video_frames)}帧")
# if len(error_video_frames) > 0:
#     api_logger.error(f"生成图片失败, 共有 {len(error_video_frames)} 帧")

#     for tryIdx in range(100):
#         api_logger.info(f"第 {tryIdx + 1} 次尝试, 还剩下错误帧={len(error_video_frames)}")
#         temp_cartoon_frames, temp_error_frame = generateImage(error_video_frames)
#         if len(temp_cartoon_frames) > 0:
#             total_cartoon_frames = total_cartoon_frames + temp_cartoon_frames
#         if len(temp_error_frame) == 0:
#             api_logger.info("已经没有错误帧")
#             break
#         error_video_frames = temp_cartoon_frames


# api_logger.error(f"最终还有错误帧={len(error_video_frames)}")


total_cartoon_frames.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
final_vid = Util.create_video(total_cartoon_frames, kFixedFps, outVideoMutePath)
curVideoPath = outVideoMutePath
api_logger.info(f"视频保存到 {outVideoMutePath}")


if addVoice == "add" and os.path.exists(outAudioPath):
    api_logger.info("---------添加音频")
    command = f"ffmpeg -y -i {curVideoPath}  -i {outAudioPath} -shortest {outVideoPath}"
    api_logger.info(f"命令：")
    api_logger.info(command)
    result = subprocess.check_output(command, shell=True)
    Util.log_subprocess_output(result)
    api_logger.info(f'完成音频合并任务: {outVideoPath}')
    curVideoPath = outVideoPath


if curVideoPath != outVideoPath:
    shutil.copyfile(curVideoPath, outVideoPath)
    curVideoPath = outVideoPath

api_logger.info(f"最终视频保存到 {outVideoPath}")

if needUploadTos == "upload":
    api_logger.info("---------上传到oss")
    bucketName = "magicphoto-1315251136"
    resultUrlPre = f"cartoon/video/{processId}/"
    videoName=os.path.basename(curVideoPath)
    reusultUrl = f"{resultUrlPre}{videoName}"
    api_logger.info(f"上传视频 {curVideoPath}")
    if os.path.exists(curVideoPath):
        api_logger.info(f"上传视频到OSS，curVideoPath:{curVideoPath}, task.key:{reusultUrl}, task.bucketName:{bucketName}")
        TosService.upload_file(curVideoPath, reusultUrl, bucketName)
        KCDNPlayUrl="http://magicphoto.cdn.yuebanjyapp.com/"
        playUrl = f"{KCDNPlayUrl}{reusultUrl}"
        api_logger.info(f"播放地址= {playUrl}")

        notiMsg = f"任务类型：卡通化视频\n"
        notiMsg = notiMsg + f"文件名： {videoName}\n"
        notiMsg = notiMsg + f"原始文件地址： {videoSrcPath}\n"
        orginVideoUrl = playUrl.replace("http://magicphoto.cdn.yuebanjyapp.com/", "https://magicphoto-1315251136.cos.ap-hongkong.myqcloud.com/")
        notiMsg = notiMsg + f"cdn播放地址: {playUrl}\n"
        notiMsg = notiMsg + f"原始地址: {orginVideoUrl}\n"
        NotifyUtil.notifyFeishu(notiMsg)
        api_logger.info(notiMsg)
        # # 打开文件并写入
        # dataFilePath = f"/data/work/translate/{processId}/output.txt"
        # os.makedirs(os.path.dirname(dataFilePath), exist_ok=True)
        # api_logger.info(f"url 列表写入文件: {dataFilePath}")
        # with open(dataFilePath, "w") as file:
        #     file.write(playUrl + "\n")
    else:
        api_logger.error(f"上传文件失败, {curVideoPath}不存在")
        exit(1)


exit(0)
# num_inference_steps 默认100
# image_guidance_scale 默认 1.5 , 接近原图的参数，越高越接近，最少1
# guidance_scale 默认 7.5, 更高的引导标度值鼓励模型生成与文本紧密链接的图像
# 以上3个参数会影响推理速度，

# images = pipe(prompt, image=image, num_inference_steps=10, image_guidance_scale=1).images
# edit = pipe(prompt, image=image, num_inference_steps=20, image_guidance_scale=1.5, guidance_scale=7).images[0]

# /data/work/aishowos/whisper_subtitle/venv/bin/python utilCartoon.py -v '/data/work/translate/BiB9YykxoZw/BiB9YykxoZw-cn-subtitle.mp4' -i 'BiB9YykxoZw'