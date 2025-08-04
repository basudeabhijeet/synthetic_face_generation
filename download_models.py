import urllib.request
import os

# Download StyleGAN2-ADA model
stylegan2_url = 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl'
stylegan2_output = 'models/stylegan2-ada-pytorch/ffhq.pkl'

# Download e4e encoder model
e4e_url = 'https://huggingface.co/AIRI-Institute/HairFastGAN/blob/main/pretrained_models/encoder4editing/e4e_ffhq_encode.pt'
e4e_output = 'models/e4e_encoder/e4e_ffhq_encode.pt'

# Ensure directories exist
os.makedirs(os.path.dirname(stylegan2_output), exist_ok=True)
os.makedirs(os.path.dirname(e4e_output), exist_ok=True)

# Download files
urllib.request.urlretrieve(stylegan2_url, stylegan2_output)
urllib.request.urlretrieve(e4e_url, e4e_output)

print("✅ Models downloaded successfully to the 'models/' directory.")
