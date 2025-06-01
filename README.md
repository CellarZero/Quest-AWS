# Rearc Quest AWS Data Pipeline

This project is an **AWS CDK-based data pipeline** that:
- Syncs open BLS data to S3
- Fetches US population data via API and uploads it to S3
- Processes analytics on this data via Lambda
- Triggers analytics on SQS messages

It includes:
- Lambda functions with supporting layers
- CDK stacks for infrastructure
- CI/CD pipeline with unit testing in both Dev and Prod stages

---

## 🚀 Project Structure

rearc-quest-aws/
│
├── quest_aws/
│ ├── lambda_functions/
│ │ ├── sync_bls_api.py
│ │ └── analysis.py
│ ├── lambda_layers/
│ │ └── dependencies/ # dependencies layer (boto3, pandas, etc.)
│ └── stacks/
│ └── quest_first_stack.py # Main CDK stack
│
├── tests/
│ └── unit/
│ ├── test_sync_bls_api.py
│ ├── test_analysis.py
│ └── test_cdk_stack.py
│
├── app.py # CDK entrypoint
├── requirements.txt
└── README.md # This file!


---

## 🛠️ Prerequisites

- **Python 3.9+**  
- **Node.js 16+** (for AWS CDK)  
- **AWS CLI** configured with appropriate credentials  
- **GitHub Token** (stored in AWS Secrets Manager under `github-token`)

---

## 🧩 Setup

1️⃣ **Clone the repository:**
```bash
git clone https://github.com/CellarZero/Quest-AWS.git
cd Quest-AWS

2️⃣ **Create a virtual environment and activate it:**
```bash
python3 -m venv rearcenv
source rearcenv/bin/activate

3️⃣ **Install dependencies:**
```bash
pip install -r requirements.txt

4️⃣ **Install AWS CDK:**
```bash
npm install -g aws-cdk

---

## 📦 Build & Deploy

1️⃣ **Bootstrap your AWS environment:**
```bash
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>

2️⃣ **Deploy your stack:**
```bash
cdk deploy

---

## 🧪 Run Unit Tests

The unit tests cover:
* Lambda functions (sync_bls_api and analysis)
* CDK stack resources
* Run them using pytest:
```bash
pytest tests/unit

--- 

## 🔄 CI/CD Pipeline
This project uses AWS CDK Pipelines:
* Pulls code from GitHub (CellarZero/Quest-AWS).
* Runs unit tests before deploying to Dev and Prod stages.
* Requires a GitHub token stored in AWS Secrets Manager (github-token).

---

## 🔐 Secrets Management
Store your GitHub token using AWS CLI:
```bash
aws secretsmanager create-secret \
  --name github-token \
  --secret-string "<your-github-token>"

---

## 🗑️ Clean Up
To remove all resources:
```bash
cdk destroy

---

## 🔎 Additional Notes
Lambda Layers:
Add external dependencies like boto3, pandas, beautifulsoup4, etc. to quest_aws/lambda_layers/dependencies/ and build a ZIP package if needed.

CDK Stages:
The pipeline includes both Dev and Prod stages with a Manual Approval step before production deployment.

Environment Variables:

BUCKET_NAME is passed automatically in each environment.