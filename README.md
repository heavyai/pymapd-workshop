# pymapd-workshop
Sample code used for explaining Pymapd API usage.

Here are the steps to create an Anaconda Python environment, and install Pymapd with the basic Machine Learning packages.
This setup information applies to Linux Centos 7.
```bash
sudo yum install bzip2
curl -O https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
bash Anaconda3-5.3.1-Linux-x86_64.sh
```
##### Confirm changes to ~/.bashrc and source it.
```bash
source .bashrc
```
##### Install Pymapd, Nvidia CUDA/RAPIDS along with the ML packages like scikit-learn and xgboost.
```bash
conda install -c nvidia/label/cuda10.0 -c rapidsai/label/cuda10.0 -c numba -c conda-forge -c defaults cudf=0.6 pymapd python=3.6
conda install scikit-learn
conda install -c conda-forge xgboost
conda install cudatoolkit
conda install -c anaconda statsmodels
```
##### Generate the Jupyter Notebook configuration file under ~/.jupyter/jupyter_notebook_config.py.
##### The config parameters c.NotebookApp.port and c.NotebookApp.ip control the port and IP from where you can connect. The default is port 8888.
```bash
jupyter notebook --generate-config 
```



