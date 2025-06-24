# Python Packages Used in MLOPS Project

## Overview
This document provides a comprehensive analysis of all Python packages used in your MLOPS project deployed through the GitHub repository.

## Main Dependencies (requirements.txt)

### Core ML & Data Science Packages
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **scikit-learn** - Machine learning library
- **matplotlib** - Data visualization

### MLOps & Experiment Tracking
- **mlflow==2.2.2** - ML experiment tracking and model management
- **notebook** - Jupyter notebook support

### Utility & Configuration Packages
- **python-box==6.0.2** - Advanced Python dictionaries with attribute-style access
- **pyYAML** - YAML parser for configuration files
- **tqdm** - Progress bars for loops
- **ensure==1.0.2** - Function argument validation
- **joblib** - Lightweight pipelining for Python
- **types-PyYAML** - Type stubs for PyYAML

### Web Application
- **Flask** - Web framework for creating APIs
- **Flask-Cors** - Cross-Origin Resource Sharing support for Flask

### Development
- **-e .** - Local package installation (editable install)

## MLflow Model Dependencies
Additional packages automatically tracked by MLflow in model artifacts:

- **mlflow<3,>=2.2** - MLflow compatibility range
- **cloudpickle==2.2.1** - Serialization for machine learning models
- **numpy==1.26.4** - Specific version for model compatibility
- **pandas==2.2.3** - Specific version for model compatibility
- **psutil==7.0.0** - System and process utilities
- **scikit-learn==1.6.1** - Specific version for model compatibility
- **scipy==1.15.3** - Scientific computing library

## Standard Library & Built-in Modules Used
The following Python standard library modules are extensively used:

### Core Python Modules
- **os** - Operating system interface
- **sys** - System-specific parameters and functions
- **logging** - Logging facility
- **json** - JSON encoder and decoder
- **typing** - Type hints support

### File & Path Operations
- **pathlib** - Object-oriented filesystem paths
- **urllib.request** - URL request handling
- **urllib.parse** - URL parsing utilities
- **zipfile** - ZIP archive handling

### Data Structures & Utilities
- **dataclasses** - Data class decorator
- **functools** - Higher-order functions and operations

## Machine Learning Specific Imports

### Scikit-learn Components
- **sklearn.linear_model.ElasticNet** - Elastic Net regression
- **sklearn.metrics** - Performance metrics (MSE, MAE, R²)
- **sklearn.model_selection.train_test_split** - Data splitting

### MLflow Components
- **mlflow.sklearn** - Scikit-learn integration with MLflow

## Project Structure Dependencies

### Custom Package Structure
- **mlProject** - Main project package (local)
  - **components/** - ML pipeline components
  - **config/** - Configuration management
  - **constants/** - Project constants
  - **entity/** - Data entity definitions
  - **pipeline/** - ML training pipelines
  - **utils/** - Utility functions

## Package Categories Summary

### 🔬 **Data Science & ML (7 packages)**
pandas, numpy, scikit-learn, matplotlib, scipy, cloudpickle, psutil

### 🚀 **MLOps & Tracking (2 packages)**
mlflow, notebook

### 🌐 **Web Development (2 packages)**
Flask, Flask-Cors

### ⚙️ **Configuration & Utilities (5 packages)**
python-box, pyYAML, types-PyYAML, ensure, tqdm

### 🔧 **Development & Build (1 package)**
joblib

### 📦 **Local Development (1 package)**
mlProject (local editable package)

## Total Package Count
- **Direct dependencies**: 15 packages
- **MLflow tracked versions**: 7 packages  
- **Standard library modules**: 10+ modules
- **Total unique external packages**: ~18 packages

## Version Management
The project uses a mix of:
- **Pinned versions** (mlflow==2.2.2, python-box==6.0.2, ensure==1.0.2)
- **Flexible versions** (pandas, numpy, scikit-learn)
- **MLflow auto-tracked versions** for model artifacts

## Notes
- The project follows MLOps best practices with experiment tracking via MLflow
- All ML pipeline stages are modularized with proper configuration management
- The setup supports both training pipelines and web API deployment
- Version compatibility is ensured through MLflow's automatic dependency tracking