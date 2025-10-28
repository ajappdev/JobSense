# General Imports
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

# App imports
import common as common
import ai as ai

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:8080"])

@app.route('/get-jobs', methods=['POST'])
def get_jobs():
    try:
        # Validate JSON body
        data = request.get_json()
        if not data or "link" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'link' in request payload"
            }), 400

        link = data["link"]
        domain = common.get_domain_from_link(link)


        url = "https://crawlic.ialae.com/describe-page"
        payload = {
            "link": link
        }

        headers = {
            "Authorization": f"Bearer {common.CRAWLIC_API_KEY}",
            "Content-Type": "application/json"
        }

        # Call web scraping service at POST /describe-page
        response = requests.post(url, json=payload, headers=headers)

        data = response.json()

        if data["success"]:
            description = data['data']
        else:
            return jsonify(
                {
                    "success": False,
                    "error": "Error fetching web scraping service"
                }
            ), 500

        # Analyze content using AI module

        if description['type'] != "Job Board":
            return jsonify(
                {
                    "success": False,
                    "error": "The provided page is not a job board page"
                }
            ), 400
        
        jobs = ai.get_listed_jobs_from_content(description['content']).model_dump()["jobs"]

        for j in jobs:
            j["job_link"] = common.fix_link_with_domain(j["job_link"], domain)

        # Return structured response
        return jsonify({
            "success": True,
            "jobs": jobs,
        }), 200
    
    except Exception as e:
        # In production, log the error instead of exposing str(e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5001, debug=True)