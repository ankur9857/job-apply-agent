from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import json, os
from datetime import datetime

app = Flask(__name__, static_folder='static')

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel('gemini-1.5-flash')

applications = []

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/search', methods=['POST'])
def search_jobs():
    data = request.json
    role = data.get('role', 'Developer')
    location = data.get('location', 'Remote')
    prompt = f"""Generate 6 realistic job listings for "{role}" in "{location}" Indian market.
Return ONLY JSON array:
[{{"id":1,"title":"title","company":"company","location":"loc","salary":"X-Y LPA","skills":["s1","s2"],"match":85,"description":"desc"}}]"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'): text = text[4:]
        jobs = json.loads(text.strip())
    except:
        jobs = [{"id":1,"title":role,"company":"TechCorp","location":location,"salary":"8-12 LPA","skills":["Python"],"match":85,"description":"Great role"}]
    return jsonify({"success": True, "jobs": jobs})

@app.route('/api/auto-apply', methods=['POST'])
def auto_apply():
    data = request.json
    role = data.get('role', 'Developer')
    location = data.get('location', 'Remote')
    limit = int(data.get('limit', 5))
    profile = data.get('profile', {})
    results = []
    prompt = f"""Generate {limit} job listings for "{role}" in "{location}".
Return ONLY JSON array:
[{{"id":1,"title":"title","company":"company","location":"loc","salary":"X-Y LPA","skills":["s1"],"match":85,"description":"desc"}}]"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'): text = text[4:]
        jobs = json.loads(text.strip())
    except:
        jobs = [{"id":1,"title":role,"company":"TechCorp","location":location,"salary":"8-12 LPA","skills":["Python"],"match":85,"description":"Great role"}]
    for job in jobs[:limit]:
        cl_prompt = f"Write 2-sentence cover letter for {job['title']} at {job['company']} for {profile.get('name','candidate')} with {profile.get('skills','good skills')}."
        cl = model.generate_content(cl_prompt).text
        app_entry = {
            "id": len(applications)+1,
            "job_title": job['title'],
            "company": job['company'],
            "location": job['location'],
            "salary": job.get('salary','Negotiable'),
            "status": "Applied",
            "applied_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "cover_letter": cl
        }
        applications.append(app_entry)
        results.append(app_entry)
    return jsonify({"success":True,"message":f"Applied to {len(results)} jobs!","applications":results})

@app.route('/api/applications', methods=['GET'])
def get_applications():
    return jsonify({"success": True, "applications": applications})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
