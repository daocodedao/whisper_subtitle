# 安装
## 项目
git clone https://github.com/daocodedao/whisper_subtitle.git

> *This project is only available to Linux/MacOS users.*

## About This Project 
This project
  
- uses [openai/Whisper](https://github.com/openai/whisper) from OpenAI to generate video subtitles automatically.

- adapted some codes from [m1guelpf/auto-subtitle](https://github.com/m1guelpf/auto-subtitle).
- uses the [base model](https://github.com/openai/whisper#available-models-and-languages) from [openai/Whisper](https://github.com/openai/whisper). Which is multi-lingual and fairly fast. If you want to use a smaller model, you can change the model in `main.py` to `tiny`. However, the accuracy will be lower.
- has been tested on a youtube video of 8 min duration. It took around 2 min to generate the subtitles on my mac (CPU, Quad-Core Intel Core i5).
## Potential Application
- Generate time-stamped subtitles for your video. Would be helpful in video editing.
- Add subtitles to lesson recordings to learn 3x faster by reading subtitles instead of listening. You might also navigate lectures via keywords.
- and more...
## Installation

```
# Dependency
python3.10 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# download https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt
# to models/

# ubuntu install font
sudo apt install -y ttf-mscorefonts-installer
# check font
sudo fc-cache -f

```

It might take a while to install `whisper`. Please be patient.
## Usage
```
python generate-subtitle.py -v "path_to_your_video.mp4" -o "path_to_save_subtitles.srt" -l "zh"
```




