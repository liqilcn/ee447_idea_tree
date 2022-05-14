# Idea Tree Extraction Lab for ee447 


## Attention
1. We recommend that you use conda to create a new python environment and install all the dependency packages via the requirement file. The code will run fine in a python 3.7 environment.
2. Graphviz may need to be installed on your machine.

## Usage

0. Compile the gml reading tool in your python environment, otherwise the code will not work
``` shell
    cd ./src/readgml
    python setup.py build_ext --inplace
```
1. Choose .gml files you want to extract idea tree in [./temp_files/input/source_gml/](./temp_files/input/source_gml/). The file name is leading articles paper ID in acemap.
2. Modify the pid list in [main.py](./src/main.py)
3. run [main.py](./src/main.py) to get idea trees, then you can get the idea tree in [idea_tree_thumbnail](./idea_tree_thumbnail)

You can get the details of the corresponding paper ID via a URL like this: [https://www.acemap.info/paper/280665520](https://www.acemap.info/paper/280665520). The last part of the URL is the paper ID. This may help you to filter the corresponding .gml file.