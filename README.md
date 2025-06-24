# MLOPS-with-MLflow
# End-to-end-Machine-Learning-Project-with-MLflow


## Workflows

## inside config folder
1. Update config.yaml
## schema is a file which will have all columns in our data with data type
2. Update schema.yaml
## We will be writing all of the parameters using in our project
3. Update params.yaml
## entity provides useid as key to join features
4. Update the entity
5. Update the configuration manager in src config
## components has data injection and data validation, datatransaformation
6. Update the components
## all components will be integrated with pipeline; where training and prediction pipeline separate
7. Update the pipeline 
8. Update the main.py
9. Update the app.py

## we will integrate main.py with app.py user will run app.py and access the code

# How to run?
### STEPS:

Clone the repository

```bash
https://github.com/entbappy/End-to-end-Machine-Learning-Project-with-MLflow
```
### STEP 01- Create a conda environment after opening the repository

```bash
conda create -n mlproj python=3.8 -y
```

```bash
conda activate mlproj
```


### STEP 02- install the requirements
```bash
pip install -r requirements.txt
```


```bash
# Finally run the following command
python app.py
```

Now,
```bash
open up you local host and port
```

## 📦 Python Packages & Dependencies

### Overview
This project uses a comprehensive set of Python packages for MLOps, data science, and web development. Below is the complete analysis of all dependencies used.

### Main Dependencies (requirements.txt)

#### 🔬 Core ML & Data Science Packages
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **scikit-learn** - Machine learning library
- **matplotlib** - Data visualization

#### 🚀 MLOps & Experiment Tracking
- **mlflow==2.2.2** - ML experiment tracking and model management
- **notebook** - Jupyter notebook support

#### ⚙️ Utility & Configuration Packages
- **python-box==6.0.2** - Advanced Python dictionaries with attribute-style access
- **pyYAML** - YAML parser for configuration files
- **tqdm** - Progress bars for loops
- **ensure==1.0.2** - Function argument validation
- **joblib** - Lightweight pipelining for Python
- **types-PyYAML** - Type stubs for PyYAML

#### 🌐 Web Application
- **Flask** - Web framework for creating APIs
- **Flask-Cors** - Cross-Origin Resource Sharing support for Flask

#### 📦 Development
- **-e .** - Local package installation (editable install)

### MLflow Model Dependencies
Additional packages automatically tracked by MLflow in model artifacts:

- **mlflow<3,>=2.2** - MLflow compatibility range
- **cloudpickle==2.2.1** - Serialization for machine learning models
- **numpy==1.26.4** - Specific version for model compatibility
- **pandas==2.2.3** - Specific version for model compatibility
- **psutil==7.0.0** - System and process utilities
- **scikit-learn==1.6.1** - Specific version for model compatibility
- **scipy==1.15.3** - Scientific computing library

### Machine Learning Components Used

#### Scikit-learn Algorithms & Tools
- **ElasticNet Regression** - Main ML algorithm for training
- **train_test_split** - Data splitting functionality
- **Performance Metrics** - MSE, MAE, R² score evaluation

#### MLflow Integration
- **mlflow.sklearn** - Scikit-learn model logging and tracking
- **Experiment tracking** - Automated parameter and metric logging
- **Model registry** - Model versioning and artifact storage

### Project Architecture Dependencies

#### Custom Package Structure (mlProject)
- **components/** - ML pipeline components (data ingestion, validation, transformation, training, evaluation)
- **config/** - Configuration management and YAML parsing
- **constants/** - Project constants and file paths
- **entity/** - Data entity definitions and type hints
- **pipeline/** - Modular training and prediction pipelines
- **utils/** - Common utility functions and helpers

### Standard Library Modules Extensively Used
- **os, sys** - System operations
- **pathlib** - Modern path handling
- **logging** - Comprehensive logging throughout pipelines
- **json** - Configuration and data serialization
- **urllib** - URL and web request handling
- **zipfile** - Data archive processing
- **dataclasses** - Clean data structure definitions

### Package Summary by Category

| Category | Count | Examples |
|----------|--------|----------|
| 🔬 Data Science & ML | 7 | pandas, numpy, scikit-learn, scipy |
| 🚀 MLOps & Tracking | 2 | mlflow, notebook |
| 🌐 Web Development | 2 | Flask, Flask-Cors |
| ⚙️ Configuration & Utils | 5 | python-box, pyYAML, tqdm, ensure |
| 🔧 Development & Build | 1 | joblib |
| 📦 Local Development | 1 | mlProject (custom) |

### Total Package Count
- **Direct dependencies**: 15 packages
- **MLflow tracked versions**: 7 packages  
- **Standard library modules**: 10+ modules
- **Total unique external packages**: ~18 packages

### Version Management Strategy
- **Pinned versions** for critical packages (mlflow==2.2.2, python-box==6.0.2)
- **Flexible versions** for common packages (pandas, numpy, scikit-learn)
- **MLflow auto-tracking** ensures model artifact compatibility
- **Environment reproducibility** through requirements.txt and MLflow logging

### Installation Notes
All dependencies are managed through:
1. **requirements.txt** - Main project dependencies
2. **setup.py** - Local package installation with editable mode
3. **MLflow artifacts** - Automatic model environment capture
4. **Conda environment** - Isolated Python 3.8 environment recommended


## MLflow

[Documentation](https://mlflow.org/docs/latest/index.html)


##### cmd
- mlflow ui

### dagshub
[dagshub](https://dagshub.com/)

MLFLOW_TRACKING_URI=https://dagshub.com/entbappy/End-to-end-Machine-Learning-Project-with-MLflow.mlflow \
MLFLOW_TRACKING_USERNAME=entbappy \
MLFLOW_TRACKING_PASSWORD=6824692c47a369aa6f9eac5b10041d5c8edbcef0 \
python script.py

Run this to export as env variables:

```bash

export MLFLOW_TRACKING_URI=https://dagshub.com/entbappy/End-to-end-Machine-Learning-Project-with-MLflow.mlflow

export MLFLOW_TRACKING_USERNAME=entbappy 

export MLFLOW_TRACKING_PASSWORD=6824692c47a369aa6f9eac5b10041d5c8edbcef0

```



# AWS-CICD-Deployment-with-Github-Actions

## 1. Login to AWS console.

## 2. Create IAM user for deployment

	#with specific access

	1. EC2 access : It is virtual machine

	2. ECR: Elastic Container registry to save your docker image in aws


	#Description: About the deployment

	1. Build docker image of the source code

	2. Push your docker image to ECR

	3. Launch Your EC2 

	4. Pull Your image from ECR in EC2

	5. Lauch your docker image in EC2

	#Policy:

	1. AmazonEC2ContainerRegistryFullAccess

	2. AmazonEC2FullAccess

	
## 3. Create ECR repo to store/save docker image
    - Save the URI: 566373416292.dkr.ecr.ap-south-1.amazonaws.com/mlproj

	
## 4. Create EC2 machine (Ubuntu) 

## 5. Open EC2 and Install docker in EC2 Machine:
	
	
	#optinal

	sudo apt-get update -y

	sudo apt-get upgrade
	
	#required

	curl -fsSL https://get.docker.com -o get-docker.sh

	sudo sh get-docker.sh

	sudo usermod -aG docker ubuntu

	newgrp docker
	
# 6. Configure EC2 as self-hosted runner:
    setting>actions>runner>new self hosted runner> choose os> then run command one by one


# 7. Setup github secrets:

    AWS_ACCESS_KEY_ID=

    AWS_SECRET_ACCESS_KEY=

    AWS_REGION = us-east-1

    AWS_ECR_LOGIN_URI = demo>>  566373416292.dkr.ecr.ap-south-1.amazonaws.com

    ECR_REPOSITORY_NAME = simple-app




## About MLflow 
MLflow

 - Its Production Grade
 - Trace all of your expriements
 - Logging & tagging your model


