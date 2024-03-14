import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
from diffusers.utils import load_image

model_id = "instruction-tuning-sd/cartoonizer"
pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16, use_auth_token=True
).to("cuda")

image_path = "./sample/WX20240314-161847.png"
image = load_image(image_path)

image = pipeline("Cartoonize the following image", image=image).images[0]
image.save("out/image.png")

