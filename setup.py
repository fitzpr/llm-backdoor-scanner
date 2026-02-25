"""Setup configuration for the LLM Backdoor Scanner package"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="llm-backdoor-scanner",
    version="1.0.0",
    author="LLM Security Research Team",
    author_email="security@example.com",
    description="Research-validated backdoor detection system implementing Microsoft Research methodology with 87.8% detection rate",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fitzpr/llm-backdoor-scanner",
    project_urls={
        "Bug Reports": "https://github.com/fitzpr/llm-backdoor-scanner/issues",
        "Source": "https://github.com/fitzpr/llm-backdoor-scanner",
        "Documentation": "https://github.com/fitzpr/llm-backdoor-scanner#readme",
    },
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    python_requires=">=3.8",
    install_requires=requirements,
    
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "pre-commit>=2.15",
        ],
        "visualization": [
            "matplotlib>=3.5",
            "seaborn>=0.11",
            "plotly>=5.0",
        ],
        "experimental": [
            "tensorboard>=2.7",
            "wandb>=0.12",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "llm-backdoor-scanner=llm_backdoor_scanner.cli:main",
            "backdoor-scan=llm_backdoor_scanner.cli:main",
        ],
    },
    
    include_package_data=True,
    package_data={
        "llm_backdoor_scanner": [
            "config/*.json",
            "data/*.json",
        ],
    },
    
    zip_safe=False,
    
    # Additional metadata
    keywords="llm, backdoor, security, transformer, detection, ai, ml, nlp",
    
    # Ensure compatibility
    platforms=["any"],
)