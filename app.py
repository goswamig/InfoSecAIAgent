from flask import Flask, render_template, request, jsonify
import requests
import git
import os
import shutil
import threading
from datetime import datetime, timedelta
from queue import Queue

app = Flask(__name__)

class VulnerabilityScannerAgent:
    def __init__(self):
        self.cve_database = {}
        self.system_inventory = {}
        self.last_update = None
        self.update_interval = timedelta(hours=24)
        self.status_queue = Queue()

    def update_status(self, status):
        self.status_queue.put(status)

    def update_cve_database(self):
        self.update_status("Updating CVE database...")
        url = "https://cve.mitre.org/data/downloads/allitems.csv"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.cve_database = self.parse_cve_data(response.text)
                self.last_update = datetime.now()
                self.update_status(f"CVE database updated at {self.last_update}")
            else:
                self.update_status(f"Failed to fetch CVE data. Status code: {response.status_code}")
        except Exception as e:
            self.update_status(f"Error updating CVE database: {str(e)}")

    def parse_cve_data(self, csv_data):
        cve_dict = {}
        for line in csv_data.split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 3:
                cve_id = parts[0]
                description = parts[2]
                cve_dict[cve_id] = description
        return cve_dict

    def update_system_inventory(self, repo_path):
        self.update_status("Updating system inventory...")
        self.system_inventory = {}
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.php')):
                    self.update_status(f"Analyzing file: {file}")
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        if 'import' in content:
                            self.system_inventory[file] = "1.0.0"  # Dummy version

    def check_vulnerabilities(self):
        self.update_status("Checking for vulnerabilities...")
        vulnerabilities = []
        for file, version in self.system_inventory.items():
            for cve_id, description in self.cve_database.items():
                if file.lower() in description.lower():
                    vulnerabilities.append(f"{cve_id}: {description} (Found in {file})")
        return vulnerabilities

    def scan_repository(self, repo_url):
        self.update_status(f"Starting scan for {repo_url}")
        if not self.last_update or datetime.now() - self.last_update > self.update_interval:
            self.update_cve_database()
        
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = f"temp_repos/{repo_name}"
        
        try:
            self.update_status(f"Cloning repository: {repo_url}")
            git.Repo.clone_from(repo_url, repo_path)
            self.update_system_inventory(repo_path)
            vulnerabilities = self.check_vulnerabilities()
        finally:
            if os.path.exists(repo_path):
                self.update_status("Cleaning up temporary files...")
                shutil.rmtree(repo_path)
        
        if vulnerabilities:
            result = f"Vulnerabilities found in {repo_url}:\n" + "\n".join(vulnerabilities)
        else:
            result = f"No known vulnerabilities found in {repo_url}"
        
        self.update_status("Scan completed")
        return result

scanner = VulnerabilityScannerAgent()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        threading.Thread(target=scanner.scan_repository, args=(repo_url,)).start()
        return render_template('result.html', repo_url=repo_url)
    return render_template('index.html')

@app.route('/status')
def status():
    if not scanner.status_queue.empty():
        return jsonify({'status': scanner.status_queue.get()})
    return jsonify({'status': None})

@app.route('/result')
def result():
    if scanner.status_queue.empty():
        return jsonify({'result': scanner.scan_repository(request.args.get('repo_url'))})
    return jsonify({'result': None})

if __name__ == '__main__':
    app.run(debug=True)