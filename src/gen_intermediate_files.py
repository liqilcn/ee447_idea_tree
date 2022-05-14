# ### 逐年生成相关科学主题的所需文件，逐年分割gml文件，脉络树文件，点熵树熵文件，树深文件
import networkx as nx
import time
import json
import datetime
import shutil
import random
import os
from readgml import readgml
from tqdm import tqdm_notebook as tqdm
from multiprocessing.pool import Pool

from gen_source_gml_by_year import gen_year_by_year_source_gml
from gen_reduction import gen_reduction
from gen_skeleton_tree import gen_skeleton_tree
from gen_tree_node_deep import gen_tree_node_deep
from gen_node_and_tree_entropy import gen_entropy
from gen_idea_tree_attributed_and_detail_file import gen_visible_depth_marked_skeleton_tree_gml_and_high_KE_node_detail


def gen_intermediate_files(pid):
    # 逐年生成脉络树，树深，各个节点的点熵树熵等
    # print('gen source gml finish!')
    if not os.path.exists('../temp_files/source_gml_by_year/'+str(pid)):
        os.makedirs('../temp_files/source_gml_by_year/'+str(pid))
    shutil.copyfile(f"../temp_files/source_gml/{pid}.gml", f"../temp_files/source_gml_by_year/{pid}/{datetime.datetime.now().year}.gml")
    # 将生成的文件直接复制到source_gml_by_year，并用当前年份命名
    gen_year_by_year_source_gml(pid)
    # print('gen source gml year by year finish!')
    files_list = os.listdir('../temp_files/source_gml_by_year/'+str(pid))
    all_years_list = sorted([int(file.split('.')[0]) for file in files_list])
    
    if not os.path.exists('../temp_files/skeleton_tree_by_year/'+str(pid)):
        os.makedirs('../temp_files/skeleton_tree_by_year/'+str(pid))
    if not os.path.exists('../temp_files/node_entropy_by_year/'+str(pid)):
        os.makedirs('../temp_files/node_entropy_by_year/'+str(pid))
    if not os.path.exists('../temp_files/subtree_entropy_by_year/'+str(pid)):
        os.makedirs('../temp_files/subtree_entropy_by_year/'+str(pid))
    if not os.path.exists('../temp_files/tree_deep_by_year/'+str(pid)):
        os.makedirs('../temp_files/tree_deep_by_year/'+str(pid))
    if not os.path.exists('../temp_files/attributed_idea_tree_by_year/'+str(pid)):
        os.makedirs('../temp_files/attributed_idea_tree_by_year/'+str(pid))

    year = datetime.datetime.now().year
    INPUT_FILE_PATH = '../temp_files/source_gml_by_year/'+str(pid)+'/'+str(year)+'.gml'
    pid2reduction = gen_reduction(pid, INPUT_FILE_PATH)
    skeleton_tree = gen_skeleton_tree(pid, pid2reduction, INPUT_FILE_PATH)
    deep2node = gen_tree_node_deep(pid, skeleton_tree)
    EntropyIndex, EntropyCutIndex = gen_entropy(pid, skeleton_tree, deep2node, INPUT_FILE_PATH)  # EntropyIndex: 树熵，EntropyCutIndex：点熵
    json.dump(skeleton_tree, open('../temp_files/skeleton_tree_by_year/'+str(pid)+'/'+str(year), 'w'))
    json.dump(deep2node, open('../temp_files/tree_deep_by_year/'+str(pid)+'/'+str(year), 'w'))
    json.dump(EntropyIndex, open('../temp_files/subtree_entropy_by_year/'+str(pid)+'/'+str(year), 'w'))
    json.dump(EntropyCutIndex, open('../temp_files/node_entropy_by_year/'+str(pid)+'/'+str(year), 'w'))
    gen_visible_depth_marked_skeleton_tree_gml_and_high_KE_node_detail(pid, year)
    print(f'{pid} gen_intermediate_files finished!')