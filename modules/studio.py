import os
import base64
import sqlite3
from flask import Blueprint, request, jsonify, render_template
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, Image as VertexImage
from config import google_credentials, ZANNIE_DB             

# ===================================================================
# NETWORK SHIELD: BYPASS LOCAL PROOT/VNC PROXY ROUTING
# ===================================================================
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
for proxy_var in ['http_proxy', 'https_proxy', 'grpc_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'GRPC_PROXY']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]

# ===================================================================
# MODULE C: ZANNIE AI DESIGN STUDIO (INPAINTING + NEGATIVE PROMPTS)                                                       
# ===================================================================

vertexai.init(project="western-verve-443214-s5", location="us-central1", credentials=google_credentials)

studio_bp = Blueprint('studio', __name__)

def get_zannie_db():
    if str(ZANNIE_DB).startswith("postgres"):
        import psycopg2                                              
        return psycopg2.connect(ZANNIE_DB), True
    else:
        db_path = os.path.join('/tmp', os.path.basename(ZANNIE_DB)) if os.environ.get('VERCEL') else ZANNIE_DB                    
        return sqlite3.connect(db_path), False

def init_gallery_table():                                        
    conn, is_postgres = get_zannie_db()
    cursor = conn.cursor()
    if is_postgres:                                                  
        cursor.execute('''CREATE TABLE IF NOT EXISTS ai_gallery (
                            id SERIAL PRIMARY KEY,
                            prompt TEXT NOT NULL,                                        
                            image_data TEXT NOT NULL,
                            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)''')
    else:
        cursor.execute('''CREATE TABLE IF NOT EXISTS ai_gallery (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            prompt TEXT NOT NULL,
                            image_data TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cursor.close()
    conn.close()

@studio_bp.route('/design-studio', methods=['GET'])
def studio_interface():
    return render_template('zannie_studio.html')

@studio_bp.route('/api/generate-design', methods=['POST'])
def generate_design():
    data = request.get_json() or {}
    prompt = data.get('prompt', '')                              
    reference_image_b64 = data.get('image', None)
    mask_image_b64 = data.get('mask', None)

    if not prompt:
        return jsonify({"status": "error", "message": "Prompt cannot be empty."}), 400

    try:                                                             
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
                                                                     
        enhanced_prompt = f"Professional fashion photography, high-end editorial, luxury bespoke tailoring, highly detailed, flowing garment shapes, loose drape, cinematic lighting, {prompt}"                                                             
        harsh_negative_prompt = "tight clothing, form-fitting shirts, modern business suits, blazers, western jackets, dark t-shirts, crew necks, split geometric blocks, crop tops, distorted anatomy, poor textiles"                              
        
        if reference_image_b64:
            raw_base_b64 = reference_image_b64.split(',')[1] if ',' in reference_image_b64 else reference_image_b64
            base_bytes = base64.b64decode(raw_base_b64)
            v_base_image = VertexImage(image_bytes=base_bytes)

            if mask_image_b64:                                               
                raw_mask_b64 = mask_image_b64.split(',')[1] if ',' in mask_image_b64 else mask_image_b64
                mask_bytes = base64.b64decode(raw_mask_b64)
                v_mask_image = VertexImage(image_bytes=mask_bytes)
                                                                             
                # Execution Path A: Masked Inpainting (Syntax Corrected)
                images = model.edit_image(
                    base_image=v_base_image,
                    mask=v_mask_image,             # Correct SDK argument
                    edit_mode="inpainting-insert", # Explicit mode enforcement
                    prompt=enhanced_prompt,                                      
                    negative_prompt=harsh_negative_prompt,
                    guidance_scale=8.5,
                    number_of_images=1
                )
            else:                                                            
                # Execution Path B: Global Image-to-Image
                images = model.edit_image(
                    base_image=v_base_image,                                     
                    prompt=enhanced_prompt,
                    negative_prompt=harsh_negative_prompt,                       
                    guidance_scale=8.0,
                    number_of_images=1
                )
        else:                                                            
            # Execution Path C: Standard Text-to-Image
            images = model.generate_images(
                prompt=enhanced_prompt,
                negative_prompt=harsh_negative_prompt,
                number_of_images=1,
                aspect_ratio="3:4",
                guidance_scale=7.5
            )

        img_bytes = images[0]._image_bytes
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        image_data_url = f"data:image/png;base64,{encoded_img}"

        return jsonify({"status": "success", "image_url": image_data_url, "prompt_used": prompt}), 200                    
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Vertex AI Engine Fault: {str(e)}"}), 500                          

@studio_bp.route('/api/save-design', methods=['POST'])       
def save_design():                                               
    data = request.get_json()
    prompt = data.get('prompt')
    image_data = data.get('image_url')                       
    
    if not prompt or not image_data:
        return jsonify({"status": "error", "message": "Missing payload data."}), 400                                      
    
    try:
        init_gallery_table()
        conn, is_postgres = get_zannie_db()
        cursor = conn.cursor()

        param = "%s" if is_postgres else "?"
        cursor.execute(f"INSERT INTO ai_gallery (prompt, image_data) VALUES ({param}, {param})", (prompt, image_data))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Asset secured in Zannie Gallery."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database Fault: {str(e)}"}), 500
