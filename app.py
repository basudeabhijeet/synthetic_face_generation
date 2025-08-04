import os
import json
import logging
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for
from inversion_utils import load_hyperstyle_model, load_stylegan2_generator, process_image, download_ganspace_components

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def load_products():
    """Loads the product catalog from the JSON file."""
    with open('products.json', 'r') as f:
        return json.load(f)
    
def load_scenes():
    """Loads the filmmaking scenes from the JSON file."""
    with open('scenes.json', 'r') as f:
        return json.load(f)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['OUTPUT_FOLDER'], 'products'), exist_ok=True)


logger.info("Clearing previous session files to ensure a fresh start...")
folders_to_clear = [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]
for folder in folders_to_clear:
    if os.path.exists(folder):
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}. Reason: {e}")


# --- Load Models ---
logger.info("Initializing GANSpace components...")
download_ganspace_components('models/ganspace')

logger.info("Loading AI models...")
encoder = load_hyperstyle_model('models/hyperstyle/hyperstyle_ffhq.pt')
generator = load_stylegan2_generator('models/stylegan2-ada-pytorch/ffhq.pkl')
logger.info("AI models loaded successfully.")


@app.route('/', methods=['GET', 'POST'])
def index():
    upload_filename = 'uploaded_image.png'
    output_filename = 'synthetic_image.png'
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            logger.info("New image uploaded. Clearing all previous session files...")
            for folder in folders_to_clear:
                if os.path.exists(folder):
                    for dirpath, dirnames, filenames in os.walk(folder):
                        for filename in filenames:
                            file_path = os.path.join(dirpath, filename)
                            if os.path.isfile(file_path):
                                try:
                                    os.remove(file_path)
                                except OSError as e:
                                    logger.error(f"Error removing file {file_path}: {e}")
            
            file = request.files['file']
            file.save(upload_path)
            logger.info(f"Saved uploaded file to {upload_path}")
            
            try:
                process_image(
                    upload_path, encoder, generator, output_path,
                    truncation=0.5,
                    noise_strength=1.0
                )
                logger.info("Image processed successfully.")
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                return render_template('index.html', error=f"Error processing image: {str(e)}")

    original_image, synthetic_image = None, None
    if os.path.exists(upload_path) and os.path.exists(output_path):
        original_image = f"/{app.config['UPLOAD_FOLDER']}/{upload_filename}?t={os.path.getmtime(upload_path)}"
        synthetic_image = f"/{app.config['OUTPUT_FOLDER']}/{output_filename}?t={os.path.getmtime(output_path)}"

    return render_template('index.html', 
                         original_image=original_image,
                         synthetic_image=synthetic_image)


@app.route('/customize', methods=['GET', 'POST'])
def customize():
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.png')
    custom_output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'customized_image.png')
    attributes_path = os.path.join(app.config['OUTPUT_FOLDER'], 'last_attributes.json')

    if request.method == 'GET':
        if not os.path.exists(upload_path):
            return render_template('customize.html', synthetic_image=None, original_image=None)

        original_image = f"/{app.config['UPLOAD_FOLDER']}/uploaded_image.png"

        if os.path.exists(custom_output_path):
            synthetic_image = f"/{app.config['OUTPUT_FOLDER']}/customized_image.png?t={os.path.getmtime(custom_output_path)}"
        else:
            synthetic_image = f"/{app.config['OUTPUT_FOLDER']}/synthetic_image.png"
        
        if os.path.exists(attributes_path):
            with open(attributes_path, 'r') as f:
                attributes = json.load(f)
        else:
            attributes = {
                'gender': 0.0, 'smile': 0.0, 'pose': 0.0, 'age': 0.0,
                'lighting': 0.0, 'hair_color': 0.0, 'hair_length': 0.0,
                'expression': 0.0, 'truncation': 0.5, 'noise_strength': 1.0,
                'eye_color': 0.0, 'eye_state': 0.0, 'serious_mood': 0.0,
                'maturity': 0.0
            }

        return render_template('customize.html', 
                             synthetic_image=synthetic_image, 
                             original_image=original_image, 
                             attributes=attributes)

    if request.method == 'POST':
        data = request.json
        try:
            process_image(
                upload_path, encoder, generator, custom_output_path, 
                truncation=float(data.get('truncation', 0.5)), noise_strength=float(data.get('noise_strength', 1.0)),
                gender=float(data.get('gender', 0)), smile=float(data.get('smile', 0)), pose=float(data.get('pose', 0)),
                age=float(data.get('age', 0)), lighting=float(data.get('lighting', 0)), hair_color=float(data.get('hair_color', 0)),
                hair_length=float(data.get('hair_length', 0)), expression=float(data.get('expression', 0)),
                eye_color=float(data.get('eye_color', 0)), eye_state=float(data.get('eye_state', 0)),
                serious_mood=max(0.0, float(data.get('serious_mood', 0))), maturity=float(data.get('maturity', 0))
            )
            with open(attributes_path, 'w') as f:
                json.dump(data, f)
            return jsonify({'synthetic_image': f"/{app.config['OUTPUT_FOLDER']}/customized_image.png?t={os.path.getmtime(custom_output_path)}"})
        except Exception as e:
            return jsonify({'error': f'Error applying customizations: {str(e)}'}), 500



@app.route('/marketing')
def marketing():
    """Renders the marketing dashboard, checking for a base image first."""
    if not os.path.exists(os.path.join(app.config['OUTPUT_FOLDER'], 'synthetic_image.png')):
        return render_template('marketing.html', products_available=False)

    featured_ids = ["eye_color_lenses", "beard_grooming"]
    PRODUCTS = load_products()
    all_products = list(PRODUCTS.values())
    
    featured_products = [p for p in all_products if p['id'] in featured_ids]
    other_products = [p for p in all_products if p['id'] not in featured_ids]
    
    return render_template('marketing.html', 
                           products_available=True,
                           featured_products=featured_products, 
                           other_products=other_products)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """
    Renders the detail page by generating an image carousel based on the
    "variations" list in products.json.
    """
    PRODUCTS = load_products()
    product = PRODUCTS.get(product_id)
    if not product:
        return "Product not found", 404

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.png')
    if not os.path.exists(upload_path):
        return redirect(url_for('index'))

    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'products')
    
    image_urls = []
    labels = []
    base_image_url = f"/{app.config['OUTPUT_FOLDER']}/synthetic_image.png"

    if 'variations' in product:
        for i, variation in enumerate(product['variations']):
            if variation['edits'] == 'input':
                labels.append(variation.get('label', 'Input Image'))
                image_urls.append(base_image_url)
            else:
                labels.append(variation['label'])
                variation_filename = f"product_{product_id}_var{i}.png"
                variation_path = os.path.join(output_dir, variation_filename)
                process_image(upload_path, encoder, generator, variation_path, **variation['edits'])
                image_urls.append(f"/{variation_path.replace(os.sep, '/')}")
        
    else:
        labels.append("Input Image")
        image_urls.append(base_image_url)

    return render_template('product_detail.html',
                           product=product,
                           image_urls=image_urls,
                           labels=labels,
                           product_id=product_id)
    
@app.route('/filmmaking')
def filmmaking():
    """Renders the filmmaking 'Director's Panel' page."""
    if not os.path.exists(os.path.join(app.config['OUTPUT_FOLDER'], 'synthetic_image.png')):
        return redirect(url_for('index'))

    scenes = load_scenes()
    synthetic_image = f"/{app.config['OUTPUT_FOLDER']}/synthetic_image.png?t={os.path.getmtime(os.path.join(app.config['OUTPUT_FOLDER'], 'synthetic_image.png'))}"
    
    return render_template('filmmaking.html', 
                           scenes=list(scenes.values()),
                           synthetic_image=synthetic_image)


@app.route('/apply_scene', methods=['POST'])
def apply_scene():
    """API endpoint to apply a pre-defined scene's edits."""
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.png')):
        return jsonify({'error': 'No base image found. Please start over.'}), 400

    data = request.json
    edits = data.get('edits', {})

    scene_output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'scene_image.png')
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.png')

    try:
        process_image(upload_path, encoder, generator, scene_output_path, **edits)
        
        image_url = f"/{scene_output_path.replace(os.sep, '/')}?t={os.path.getmtime(scene_output_path)}"
        return jsonify({'new_image_url': image_url})
        
    except Exception as e:
        logger.error(f"Error applying scene: {e}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)