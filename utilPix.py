# https://huggingface.co/spaces/fffiloni/Pix2Pix-Video/blob/main/app.py modified
# 指定图片各种风格化
# https://twitter.com/CitizenPlain
# import gradio as gr
import os, cv2, torch, time, random
import numpy as np
from moviepy.editor import *

from diffusers import DiffusionPipeline, EulerAncestralDiscreteScheduler
from PIL import Image
# from yt_dlp import YoutubeDL

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'


pipe = DiffusionPipeline.from_pretrained("timbrooks/instruct-pix2pix", torch_dtype=torch.float16, safety_checker=None)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.enable_xformers_memory_efficient_attention()
pipe.unet.to(memory_format=torch.channels_last)
pipe = pipe.to("cuda")

# def download_video(url):
#   ydl_opts = {'overwrites':True, 'format':'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 'outtmpl':'/content/video.mp4'}
#   with YoutubeDL(ydl_opts) as ydl:
#     ydl.download(url)
#     return f"/content/video.mp4"

def pix2pix(prompt, text_guidance_scale, image_guidance_scale, image, steps, neg_prompt="", width=512, height=512, seed=0):
    if seed == 0:
        seed = random.randint(0, 2147483647)
    generator = torch.Generator("cuda").manual_seed(seed)
    try:
        image = Image.open(image)
        ratio = min(height / image.height, width / image.width)
        image = image.resize((int(image.width * ratio), int(image.height * ratio)), Image.LANCZOS)
        result = pipe(
            prompt,
            negative_prompt=neg_prompt,
            image=image,
            num_inference_steps=int(steps),
            image_guidance_scale=image_guidance_scale,
            guidance_scale=text_guidance_scale,
            generator=generator,
        )
        return result.images, result.nsfw_content_detected, seed
    except Exception as e:
        return None, None, error_str(e)

def error_str(error, title="Error"):
    return (
        f"""#### {title}
            {error}"""
        if error
        else ""
    )

def get_frames(video_in):
    frames = []
    kMaxFPS = 24
    clip = VideoFileClip(video_in)
    if clip.fps > kMaxFPS:
        print(f"vide rate is over {kMaxFPS}, resetting to {kMaxFPS}")
        clip_resized = clip.resize(height=512)
        clip_resized.write_videofile("video_resized.mp4", fps=kMaxFPS, verbose=False)
    else:
        print("video rate is OK")
        clip_resized = clip.resize(height=512)
        clip_resized.write_videofile("video_resized.mp4", fps=clip.fps, verbose=False)
    print("video resized to 512 height")
    cap= cv2.VideoCapture("video_resized.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("video fps: " + str(fps))
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        cv2.imwrite('in'+str(i)+'.jpg',frame)
        frames.append('in'+str(i)+'.jpg')
        i+=1
    cap.release()
    cv2.destroyAllWindows()
    print("broke the video into frames")
    return frames, fps

def create_video(frames, fps):
    print("building video result")
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile("/content/output.mp4", fps=fps, verbose=False)
    return "/content/output.mp4"

def infer(prompt, video_in, seed_in, trim_value):
    print(prompt)
    break_vid = get_frames(video_in)
    frames_list= break_vid[0]
    fps = break_vid[1]
    n_frame = int(trim_value*fps)
    if n_frame >= len(frames_list):
        print("video is shorter than the cut value")
        n_frame = len(frames_list)
    result_frames = []
    print("set stop frames to: " + str(n_frame))
    for i in frames_list[0:int(n_frame)]:
        pix2pix_img = pix2pix(prompt,5.5,1.5,i,15,"",512,512,seed_in)
        images = pix2pix_img[0]
        rgb_im = images[0].convert("RGB")
        rgb_im.save(f"out-{i}.jpg")
        result_frames.append(f"out-{i}.jpg")
        print("frame " + i + "/" + str(n_frame) + ": done;")
    final_vid = create_video(result_frames, fps)
    print("Done!")
    return final_vid

# with gr.Blocks() as demo:
#     with gr.Column(elem_id="col-container"):
#         with gr.Row():
#             with gr.Column():
#                 input_text = gr.Textbox(show_label=False, value="https://youtu.be/EU3hIXXeiz4")
#                 input_download_button = gr.Button(value="Download from YouTube or Twitch")
#                 prompt = gr.Textbox(label="Prompt", placeholder="enter prompt", show_label=False, elem_id="prompt-in")
#                 video_inp = gr.Video(label="Video source", source="upload", type="filepath", elem_id="input-vid")
#                 input_download_button.click(download_video, inputs=[input_text], outputs=[video_inp])
#             with gr.Column():
#                 video_out = gr.Video(label="Pix2pix video result", type="filepath", elem_id="video-output")
#                 with gr.Row():
#                   seed_inp = gr.Slider(label="Seed", minimum=0, maximum=2147483647, step=1, value=69)
#                   trim_in = gr.Slider(label="Cut video at (s)", minimun=1, maximum=600, step=1, value=1)
#                 submit_btn = gr.Button("Generate Pix2Pix video")
#         inputs = [prompt,video_inp,seed_inp, trim_in]
#         submit_btn.click(infer, inputs=inputs, outputs=[video_out])
# demo.queue().launch(debug=True, share=True, inline=False)

videoSrcPath = "./sample/simple5.mp4"
inputs = ["turn into an anime", videoSrcPath, 69, 5]
infer(inputs)