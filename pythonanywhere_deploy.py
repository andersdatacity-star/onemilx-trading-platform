#!/usr/bin/env python3
"""
OneMilX Trading Platform - PythonAnywhere Auto Deploy
"""

import requests
import json
import time

def deploy_to_pythonanywhere():
    """Deploy OneMilX Trading Platform to PythonAnywhere"""
    
    print("🚀 Deploying OneMilX Trading Platform to PythonAnywhere...")
    
    # PythonAnywhere API endpoint
    api_url = "https://www.pythonanywhere.com/api/v0/user/andersdatacity/consoles/"
    
    # Headers for API request
    headers = {
        "Authorization": "Token YOUR_PYTHONANYWHERE_TOKEN",
        "Content-Type": "application/json"
    }
    
    # Deploy script
    deploy_script = """
    # Clone repository
    git clone https://github.com/andersdatacity-star/onemilx-trading-platform.git
    
    # Navigate to project
    cd onemilx-trading-platform
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Set environment variables
    export JWT_SECRET_KEY="onemilx-super-secret-jwt-key-2024"
    export FLASK_SECRET_KEY="onemilx-super-secret-flask-key-2024"
    
    # Start the app
    python simple_app.py
    """
    
    try:
        # Create console session
        response = requests.post(api_url, headers=headers, json={
            "executable": "/usr/bin/python3",
            "arguments": deploy_script
        })
        
        if response.status_code == 201:
            print("✅ Successfully deployed to PythonAnywhere!")
            print("🌐 Your app URL: https://andersdatacity.pythonanywhere.com")
            print("🔑 Admin login: admin / admin123")
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    deploy_to_pythonanywhere() 