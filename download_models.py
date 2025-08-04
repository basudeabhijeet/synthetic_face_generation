import os
import urllib.request
import gdown

# Ensure target directories exist
def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

# Download using urllib
def download_with_urllib(url, output_path):
    try:
        ensure_dir(output_path)
        print(f"⬇️ Downloading with urllib: {url}")
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ Saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

# Download using gdown (Google Drive)
def download_with_gdown(drive_url, output_path):
    try:
        ensure_dir(output_path)
        print(f"⬇️ Downloading with gdown: {drive_url}")
        gdown.download(drive_url, output_path, quiet=False, fuzzy=True)
        print(f"✅ Saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to download {drive_url}: {e}")

# List of files to download
downloads = {
    "models/ganspace/age_pca_direction.npy": "https://drive.google.com/file/d/1b-PhSFrHPtDcTiZ7Fzozuba520vRE1wg/view?usp=sharing",
    "models/ganspace/eyeglasses_pca_direction.npy": "https://drive.google.com/file/d/1a_spmAc_CIjCFTzPyz-3tlL0Hpg5fu7a/view?usp=sharing",
    "models/ganspace/ffhq_pca_components.pkl": "https://drive.google.com/file/d/1nSxghZb8ZuVBeIEwOFxQg8NMV5_6aqdY/view?usp=sharing",
    "models/ganspace/ffhq-pca-components.pth": "https://drive.google.com/file/d/1b1xY83mlR6XwUK9bDSsEuTyW2rKaoSJp/view?usp=sharing",
    "models/ganspace/ganspace_pca_80_200000.pkl.gz": "https://drive.google.com/file/d/1fL_CY2U7G2lIdHq-zT-hxmfhP9oK31YO/view?usp=sharing",
    "models/ganspace/gender_pca_direction.npy": "https://drive.google.com/file/d/133wovA02T4XQxIMM7ghg5tqqvmxzl1S_/view?usp=sharing",
    "models/ganspace/pose_pca_direction.npy": "https://drive.google.com/file/d/1tvmuOXPz0wCTDJrmUDU-T6Ve6sYnMoj0/view?usp=sharing",
    "models/ganspace/smile_pca_direction.npy": "https://drive.google.com/file/d/1mjurY286umcwfw-7RNjcVWBV9EJg6_gO/view?usp=sharing",
    "models/hyperstyle/hyperstyle_ffhq.pt": "https://drive.google.com/file/d/1KkBHGd0Dk4a1Y4PgB06p1XsRBns4wU5L/view?usp=sharing",
    "models/stylegan2-ada-pytorch/ffhq.pkl": "https://drive.google.com/file/d/1EDOsYNpSiDeDlTq9LA_h1iwyD2-V1Eyk/view?usp=sharing",
    "models/pretrained_models/faces_w_encoder.pt": "https://drive.google.com/file/d/1qsh6DpsSqAxrr6oWRaMd_Me2QFFypPHW/view?usp=sharing"
}

# Download all files
for output_path, link in downloads.items():
    # Use gdown for Google Drive links, else urllib
    if "drive.google.com" in link:
        download_with_gdown(link, output_path)
    else:
        download_with_urllib(link, output_path)

print("\n🎉 All model files downloaded.")
