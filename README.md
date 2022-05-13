# Idea Tree Extraction Lab for ee447 

## Usage

0. Compile the gml reading tool in your python environment, otherwise the code will not work
``` shell
    cd ./src/readgml
    python setup.py build_ext --inplace
```
1. Choose .gml files you want to extract idea tree in [./temp_files/input/source_gml/](./temp_files/input/source_gml/). The file name is leading articles paper ID in acemap.
2. Modify the pid list in [main.py](./src/main.py)
3. run [main.py](./src/main.py) to get idea trees, then you can get the idea tree in [idea_tree_thumbnail](./idea_tree_thumbnail)

## Attention
You can get the details of the corresponding paper ID via a URL like this: [https://www.acemap.info/paper/280665520](https://www.acemap.info/paper/280665520). The last part of the URL is the paper ID. This may help you to filter the corresponding .gml file.