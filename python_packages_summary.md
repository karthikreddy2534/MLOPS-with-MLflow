# Python Packages Used in MLOPS Project

## Overview
This document lists all Python packages used in the MLOPS project based on analysis of dependency files.

## Main Dependencies (from requirements.txt)

### Core ML & Data Science Libraries
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **scikit-learn** - Machine learning algorithms
- **matplotlib** - Data visualization

### MLOps & Model Management
- **mlflow==2.2.2** - ML lifecycle management and model tracking

### Development & Utilities
- **notebook** - Jupyter notebook support
- **python-box==6.0.2** - Advanced Python dictionaries
- **pyYAML** - YAML file parsing
- **tqdm** - Progress bars
- **ensure==1.0.2** - Validation utilities
- **joblib** - Efficient serialization
- **types-PyYAML** - Type hints for PyYAML

### Web Application
- **Flask** - Web framework
- **Flask-Cors** - Cross-Origin Resource Sharing support

### Local Package
- **-e .** - Local package installation (mlProject)

## MLflow-Generated Dependencies (Exact Versions)
*These are the actual versions captured during model training/logging:*

- **mlflow<3,>=2.2** - ML lifecycle management
- **cloudpickle==2.2.1** - Enhanced pickling for cloud environments
- **numpy==1.26.4** - Numerical computing
- **pandas==2.2.3** - Data manipulation
- **psutil==7.0.0** - System and process utilities
- **scikit-learn==1.6.1** - Machine learning algorithms
- **scipy==1.15.3** - Scientific computing

## Package Categories Summary

### 📊 Data Science & ML
- pandas, numpy, scikit-learn, scipy, matplotlib

### 🔄 MLOps & Tracking
- mlflow, cloudpickle

### 🌐 Web Development
- Flask, Flask-Cors

### 🛠️ Development Tools
- notebook, joblib, tqdm

### ⚙️ Configuration & Utilities
- pyYAML, python-box, ensure, types-PyYAML, psutil

## Installation Commands

To install all dependencies:
```bash
pip install -r requirements.txt
```

To install with exact MLflow-captured versions:
```bash
pip install mlflow>=2.2,<3 cloudpickle==2.2.1 numpy==1.26.4 pandas==2.2.3 psutil==7.0.0 scikit-learn==1.6.1 scipy==1.15.3
```

## Notes
- The project uses MLflow for experiment tracking and model management
- Flask is used for creating web applications/APIs
- The setup includes both development (notebook) and production (Flask) dependencies
- MLflow automatically captures exact package versions during model logging for reproducibility