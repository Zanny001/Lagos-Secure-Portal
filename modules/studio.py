import os
import base64
from flask import Blueprint, request, jsonify, render_template
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from config import google_credentials

# ===================================================================
# MODULE C: ZANNIE AI DESIGN STUDIO (VERTEX AI INTEGRATION)
# ===================================================================

# Initialize Vertex AI using the new Lagos-verifier project ID
vertexai.init(project="western-verve-443214-s5", location="us-central1", credentials=google_credentials)

studio_bp = Blueprint('studio', __name__)

@studio_bp.route('/design-studio', methods=['GET'])
def studio_interface():
    """Serves the frontend for the Zannie AI image generation portal."""
    return render_template('zannie_studio.html')

@studio_bp.route('/api/generate-design', methods=['POST'])
def generate_design():
    """Receives prompt payloads and interfaces with the Google Vertex AI image pipeline."""
    data = request.get_json() or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"status": "error", "message": "Prompt cannot be empty."}), 400

    try:
        # Load the high-fidelity Imagen model
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        # Enforce high-end fashion photography constraints silently
        enhanced_prompt = f"Professional fashion photography, high-end editorial, luxury bespoke tailoring. {prompt}"
        
        # Generate the asset
        images = model.generate_images(
            prompt=enhanced_prompt,
            number_of_images=1,
            aspect_ratio="3:4", # Optimal aspect ratio for fashion portraits
            guidance_scale=7.5
        )
        
        # Extract the raw bytes and encode to base64 for instant frontend rendering
        img_bytes = images[0]._image_bytes
        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        image_data_url = f"data:image/png;base64,{encoded_img}"
        
        return jsonify({
            "status": "success",
            "image_url": image_data_url,
            "prompt_used": prompt
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Vertex AI Engine Fault: {str(e)}"}), 500
