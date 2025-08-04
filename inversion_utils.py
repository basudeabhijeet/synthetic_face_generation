import os
import torch
import torchvision.transforms as transforms
from torchvision.utils import save_image
from PIL import Image, ImageEnhance
from argparse import Namespace
import logging
import numpy as np
import pickle
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import sys
for repo_path in ['hyperstyle', 'stylegan2-ada-pytorch']:
    if not os.path.exists(repo_path):
        logger.warning(f"Repository {repo_path} not found. Attempting to clone...")
        if repo_path == 'hyperstyle':
            os.system("git clone https://github.com/yuval-alaluf/hyperstyle.git")
        elif repo_path == 'stylegan2-ada-pytorch':
            os.system("git clone https://github.com/NVlabs/stylegan2-ada-pytorch.git")
    sys.path.append(os.path.abspath(repo_path))

try:
    from hyperstyle.models.hyperstyle import HyperStyle
    import dnnlib
    import legacy
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"Using device: {device}")

_mean_latent_cache = None
_ganspace_components = None

def load_hyperstyle_model(model_path):
    logger.info(f"Loading HyperStyle model from {model_path}")
    ckpt = torch.load(model_path, map_location=device)
    opts = ckpt['opts']
    opts = Namespace(**opts)
    opts.checkpoint_path = model_path
    opts.device = device
    
    if not hasattr(opts, 'output_size'):
        opts.output_size = 1024
        
    encoder = HyperStyle(opts)
    encoder.eval()
    encoder.to(device)
    logger.info("HyperStyle model loaded successfully")
    return encoder

def load_stylegan2_generator(model_path):
    logger.info(f"Loading generator from {model_path}")
    with dnnlib.util.open_url(model_path) as f:
        G = legacy.load_network_pkl(f)['G_ema'].to(device)
    logger.info("Generator loaded successfully")
    return G

def get_mean_latent(generator, samples=10000):
    global _mean_latent_cache
    if _mean_latent_cache is None:
        logger.info("Computing mean latent vector...")
        z = torch.randn(samples, generator.z_dim, device=device)
        with torch.no_grad():
            w = generator.mapping(z, None)
            _mean_latent_cache = w.mean(0, keepdim=True)
        logger.info("Mean latent computed")
    return _mean_latent_cache

def download_ganspace_components(components_path='models/ganspace'):
    """Download GANSpace principal components for FFHQ StyleGAN2"""
    logger.info(f"Setting up GANSpace components at {components_path}")
    
    os.makedirs(components_path, exist_ok=True)
    
    components_file = os.path.join(components_path, 'ffhq_pca_components.pkl')
    
    if not os.path.exists(components_file):
        logger.info("Downloading GANSpace components...")
        components_url = "https://github.com/harskish/ganspace/releases/download/v1.0/ffhq_pca_components.pkl"
        
        try:
            os.system(f"wget {components_url} -O {components_file}")
            
            if os.path.exists(components_file) and os.path.getsize(components_file) > 1000:
                logger.info("Downloaded GANSpace components successfully")
            else:
                logger.warning("Download failed or file is too small. Creating synthetic components...")
                create_synthetic_components(components_file)
        except Exception as e:
            logger.error(f"Failed to download GANSpace components: {e}")
            logger.info("Creating synthetic components...")
            create_synthetic_components(components_file)
    else:
        logger.info(f"GANSpace components already exist at {components_file}")

def create_synthetic_components(components_file):
    """Create synthetic PCA components if download fails"""
    logger.info("Creating synthetic GANSpace components...")
    
    
    np.random.seed(42)  
    
    n_layers = 18
    latent_dim = 512
    n_components = 80   
    
    components = np.random.randn(n_components, n_layers * latent_dim)
    
    Q, R = np.linalg.qr(components.T)
    components = Q.T[:n_components]
    
    for i in range(n_components):
        components[i] = components[i] / np.linalg.norm(components[i])
    
    component_data = {
        'components': components,
        'mean': np.zeros(n_layers * latent_dim),
        'stdev': np.ones(n_components),
        'comp_indices': list(range(n_components))
    }
    
    with open(components_file, 'wb') as f:
        pickle.dump(component_data, f)
    
    logger.info(f"Created synthetic GANSpace components with {n_components} components")

def load_ganspace_components(components_path='models/ganspace'):
    """Load GANSpace principal components"""
    logger.info(f"Loading GANSpace components from {components_path}")
    
    download_ganspace_components(components_path)
    
    components_file = os.path.join(components_path, 'ffhq_pca_components.pkl')
    
    try:
        with open(components_file, 'rb') as f:
            data = pickle.load(f)
        
        if isinstance(data, dict):
            components = data['components']
            semantic_mappings = data.get('semantic_mappings', {})
        else:
            components = data
            semantic_mappings = {}
        
        logger.info(f"Loaded GANSpace components with shape: {components.shape}")
        return torch.from_numpy(components).float().to(device), semantic_mappings
        
    except Exception as e:
        logger.error(f"Error loading GANSpace components: {e}")
        create_synthetic_components(components_file)
        with open(components_file, 'rb') as f:
            data = pickle.load(f)
        components = data['components']
        semantic_mappings = data['semantic_mappings']
        return torch.from_numpy(components).float().to(device), semantic_mappings

def get_ganspace_components():
    """Get cached GANSpace components"""
    global _ganspace_components
    if _ganspace_components is None:
        components, semantic_mappings = load_ganspace_components()
        _ganspace_components = {
            'components': components,
            'semantic_mappings': semantic_mappings
        }
    return _ganspace_components

def edit_latent_with_ganspace(latent_codes, attributes):
    """Edit latent codes using GANSpace principal components"""
    if not attributes or all(abs(v) < 0.001 for v in attributes.values()):
        return latent_codes
    
    ganspace_data = get_ganspace_components()
    components = ganspace_data['components']
    
    with open('config.json', 'r') as f:
        semantic_mappings = json.load(f)
    
    batch_size = latent_codes.shape[0]
    num_layers = latent_codes.shape[1]
    
    flattened_latents = latent_codes.view(batch_size, -1)
    edited_latents = flattened_latents.clone()
    
    logger.info(f"Editing with GANSpace - attributes: {attributes}")
    
    for attr_name, strength in attributes.items():
        if attr_name in semantic_mappings and abs(strength) > 0.001:
            
            if attr_name == 'serious_mood' and strength < 0:
                logger.warning(f"Ignoring negative value for {attr_name}: {strength}")
                continue
            
            if attr_name == 'eye_color' and strength > 0:
                logger.warning(f"Ignoring positive value for {attr_name}: {strength}")
                continue
        
            mapping = semantic_mappings[attr_name]
            component_idx = mapping['component']
            direction = mapping['direction']
            base_strength = mapping['strength']
            
            if component_idx < components.shape[0]:
                component = components[component_idx]
                
                effective_strength = strength * direction * base_strength * 0.8  
                
                importance_weight = 1.0 / (1.0 + 0.05 * component_idx)  
                effective_strength *= importance_weight
                
                if abs(strength) > 5.0:
                    boost_factor = 1.0 + (abs(strength) - 5.0) * 0.3
                    effective_strength *= boost_factor
                
                logger.info(f"Applying GANSpace edit for {attr_name}: "
                            f"component {component_idx}, strength {effective_strength:.3f}")
                
                for i in range(batch_size):
                    edited_latents[i] = edited_latents[i] + component * effective_strength
            else:
                logger.warning(f"Component index {component_idx} out of range for {attr_name}")
    
    edited_latent_codes = edited_latents.view(batch_size, num_layers, -1)
    
    return edited_latent_codes

def process_image(img_path, encoder, generator, output_path, truncation=0.7, noise_strength=0.05, 
                  gender=0.0, smile=0.0, pose=0.0, age=0.0, lighting=0.0, hair_color=0.0, 
                  hair_length=0.0, expression=0.0, eye_color=0.0, eye_state=0.0, 
                  serious_mood=0.0, maturity=0.0):
    logger.info(f"Processing image with HyperStyle + GANSpace - truncation={truncation}, noise_strength={noise_strength}")
    logger.info(f"Attribute editing: gender={gender}, smile={smile}, pose={pose}, age={age}")
    logger.info(f"Additional attributes: lighting={lighting}, hair_color={hair_color}, hair_length={hair_length}, expression={expression}, eye_color={eye_color}, eye_state={eye_state}, serious_mood={serious_mood}, maturity={maturity}")
    
    img = Image.open(img_path).convert('RGB')
    
    # Face detection and cropping 
    try:
        import face_alignment
        fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, device=device)
        detected_faces = fa.get_landmarks_from_image(np.array(img))
        
        if detected_faces and len(detected_faces) > 0:
            landmarks = detected_faces[0]
            left = np.min(landmarks[:, 0])
            top = np.min(landmarks[:, 1])
            right = np.max(landmarks[:, 0])
            bottom = np.max(landmarks[:, 1])
            
            width, height = right - left, bottom - top
            center_x, center_y = (left + right) // 2, (top + bottom) // 2
            size = int(max(width, height) * 1.5)
            left = max(0, center_x - size // 2)
            top = max(0, center_y - size // 2)
            right = min(img.width, center_x + size // 2)
            bottom = min(img.height, center_y + size // 2)
            
            img = img.crop((left, top, right, bottom))
            logger.info("Face detected and cropped successfully")
        else:
            width, height = img.size
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            img = img.crop((left, top, left + size, top + size))
            logger.info("No face detected, using center crop")
    except ImportError:
        width, height = img.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        img = img.crop((left, top, left + size, top + size))
        logger.info("Face alignment module not available, using center crop")
    
    # Ensure square image
    width, height = img.size
    if width != height:
        max_dim = max(width, height)
        new_img = Image.new('RGB', (max_dim, max_dim), (0, 0, 0))
        new_img.paste(img, ((max_dim - width) // 2, (max_dim - height) // 2))
        img = new_img

    # HyperStyle expects 256x256 input images
    img = img.resize((256, 256), Image.LANCZOS)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        logger.info("Running HyperStyle encoder...")
        hyperstyle_reconstruction_img, result_latent = encoder(img_tensor, return_latents=True)
        
        latent_codes = result_latent
        
        if len(latent_codes.shape) == 2:
            logger.info("Expanding W space latent to W+ space")
            num_layers = 18
            latent_codes = latent_codes.unsqueeze(1).repeat(1, num_layers, 1)
        
        if truncation < 1.0:
            mean_latent = get_mean_latent(generator)
            latent_codes = mean_latent + truncation * (latent_codes - mean_latent)
            logger.info(f"Applied truncation with strength {truncation}")
        
        attribute_values = {
            'gender': gender, 'smile': smile, 'pose': pose, 'age': age,
            'lighting': lighting, 'hair_color': hair_color, 'hair_length': hair_length,
            'expression': expression, 'eye_color': eye_color, 'eye_state': eye_state,
            'serious_mood': serious_mood, 'maturity': maturity
        }
        
        final_latent_codes_for_synthesis = latent_codes
        
        if any(abs(v) > 0.001 for v in attribute_values.values()):
            edited_latent_codes = edit_latent_with_ganspace(latent_codes, attribute_values)
            logger.info("Applied GANSpace attribute editing")
            final_latent_codes_for_synthesis = edited_latent_codes
        else:
            logger.info("No attribute editing applied.")
        
        noise_mode = 'const' if noise_strength <= 0 else 'random'

        
        for module in generator.synthesis.modules():
            if 'Conv2dLayer' in str(type(module)) and hasattr(module, 'noise_strength'):
                module.noise_strength = noise_strength
        
        
        logger.info("Generating synthetic face with StyleGAN generator...")
        synthetic_img = generator.synthesis(final_latent_codes_for_synthesis,
                                            noise_mode=noise_mode,
                                            force_fp32=True)
        
        synthetic_img = (synthetic_img + 1) * 0.5
        synthetic_img = torch.clamp(synthetic_img, 0, 1)
    
    synthetic_pil = transforms.ToPILImage()(synthetic_img.squeeze(0).cpu())
    
    enhancer = ImageEnhance.Sharpness(synthetic_pil)
    synthetic_pil = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Contrast(synthetic_pil)
    synthetic_pil = enhancer.enhance(1.1)
    
    synthetic_pil.save(output_path)
    logger.info(f"Saved HyperStyle + GANSpace edited synthetic image to {output_path}")
    
    return attribute_values