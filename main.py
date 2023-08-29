from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import requests
from fastapi import BackgroundTasks, Depends
import time

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEONARDO_URL = "https://cloud.leonardo.ai/api/rest/v1/generations"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "PUT YOUR API CODE HERE"
}

LEONARDO_STATUS_URL = "https://cloud.leonardo.ai/api/rest/v1/generations/"

@app.get("/check_status/{generation_id}")
async def check_image_status(generation_id: str):
    # Fetch the status or result of the image generation from the Leonardo API
    response = requests.get(LEONARDO_STATUS_URL + generation_id, headers=HEADERS)

    if response.status_code == 200:
        data_response = response.json()
        
        # Extract the image URL
        image_urls = [img.get('url') for img in data_response.get('generations_by_pk', {}).get('generated_images', []) if img.get('url')]
        if image_urls:
            return {"image_urls": image_urls}
        else:
            return {"error": "Image URL not found in Leonardo API response."}
    else:
        return {"error": f"Failed to fetch status from Leonardo API with status code: {response.status_code}"}



@app.post("/generate_image/")
async def generate_image(request: Request):
    data = await request.json()
    
    prompt = data.get("prompt", "An oil painting of a cat")
    modelId = data.get("modelId", "b63f7119-31dc-4540-969b-2a9df997e173")
    width = data.get("width", 768)
    height = data.get("height", 768)    
    sd_version = data.get("sd_version", "v2") 
    highContrast = data.get("highContrast", False)
    scheduler = data.get("scheduler", "LEONARDO") 
    guidance_scale = data.get("guidance_scale", 7) 
    promptMagic = data.get("promptMagic", False) 
    promptMagicVersion = data.get("promptMagicVersion", "v2")    
    init_strength = data.get("init_strength", 0.4)
    num_images = data.get("num_images", 1) 
    public = data.get("public", True)
    presetStyle = data.get("presetStyle", "LEONARDO") 
    alchemy = data.get("alchemy", False)
    contrastRatio = data.get("contrastRatio", 0.5)
    expandedDomain = data.get("expandedDomain", False)
    highResolution = data.get("highResolution", False)                                                               

    payload = {
        "prompt": prompt,
        "modelId": modelId,
        "width": width,
        "height": height,
        "sd_version": sd_version,
        "num_images": num_images,
        "init_strength": init_strength,
        "highContrast": highContrast, 
        "presetStyle": presetStyle,
        "num_inference_steps": 30,
        "guidance_scale": guidance_scale,
        "tiling": False,
        "scheduler": scheduler,
        "public": public,
        "controlNet": False,
        "controlNetType": "POSE",        
        "promptMagic": promptMagic,
        "promptMagicVersion": promptMagicVersion,        
        "alchemy": alchemy,
        "contrastRatio": contrastRatio,
        "expandedDomain": expandedDomain,
        "highResolution": highResolution, 
        "negative_prompt": "closeup, close up, nude, naked, naughty, kissing, NFSW, disfigured, bad art, deformed,extra limbs,extra fins,extra tails,extra wheels,close up, duplicate, poorly drawn face, bad anatomy, disfigured, missing arms, missing legs, fused fingers, too many fingers, cross-eye, body out of frame, blurry, lacking facial details, missing paws, distorted paws, disfigured fruit",                                              

    }

    print(f"Sending payload to Leonardo: {payload}")  # Log the payload

    response = requests.post(LEONARDO_URL, json=payload, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error from Leonardo: {response.text}")  # Log error from Leonardo
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

