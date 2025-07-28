## Please Use the package manager like venv, anaconda/miniconda, etc
Recommend: packageManager: miniconda,PythonVersion: 3.11;pytorch version: 2.7
### Package Preparing
1. conda install conda-forge::pytorch
2. pip install torch_geometric
3. pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.7.0+cu128.html
4. pip install -r requirements.txt