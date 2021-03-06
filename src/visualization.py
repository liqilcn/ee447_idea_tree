#!/usr/bin/env python
# coding: utf-8

import os
import re
import csv
import json
import math
import random
import queue
import datetime
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt
from graphviz import Digraph
from tqdm import tqdm_notebook as tqdm
from PIL import Image
from matplotlib import cm
import numpy as np
import seaborn as sns
import networkx as nx
import treelib as tl
from matplotlib.ticker import MaxNLocator

from entropy_tree_layout2gml import gen_entropy_tree_visual_gml, gen_citation_entropy_tree_visual_gml # 传递参数较多，集成的模块从函数内部进行配置传参
from gen_tree_analysis_data import get_max_bias_subtree_entropy, get_max_bias_node_entropy
from simply_skeleton_tree import simply_skeleton_tree
from gml2jpg import gml2png # 传递的参数较少，集成模块时直接从函数调用时传参
from get_sub_field_entropy import get_sub_field_entropy


def get_top_entropy_pids2colorlist(pid):
    # 在2019年的点熵中找到点熵排名前10的节点的id，返回pid与颜色对应的字典
    # 特别研究的论文所用的颜色列表
    color_list = [
            '#25753f',
            '#c14510',
            '#8a1752',
            '#619cb9',
            '#f8f014',
            '#9b56b1',
            '#e88d24'
        ]
    node_entropy = json.load(open(f'../temp_files/node_entropy_by_year/{pid}/{datetime.datetime.now().year}', 'r'))   
    pid_entropy_tuple = sorted(node_entropy.items(), key = lambda item:item[1], reverse=True)
    pids_list = []
    pid2color_list = {}
    ii = 0
    for i in range(8):
        if pid_entropy_tuple[i][0] == str(pid):
            continue
        pids_list.append(pid_entropy_tuple[i][0])
        pid2color_list[str(pid_entropy_tuple[i][0])] = color_list[ii]
        ii += 1
    return pid2color_list


# 对每个领域生成逐年可视深度的演进图
def gen_visible_depth_marked_skeleton_tree_png(seminal_pid):
    # 在简化的脉络树中标注出最大可视深度下的点熵超过10的节点，用深红色
    pid2simply_ratio = {
    }
    
    COMPLETED_SKELETON_TREE_JSON = '../temp_files/skeleton_tree_by_year/'
    GML_FILE_PATH = '../temp_files/simplied_tree_gml/'
    SIMPLIED_TREE_PNG_PATH = '../temp_files/simplied_skeleton_tree_png/'
    VISIBLE_DEPTH_GML_FILE_PATH = '../temp_files/visible_depth_gml/'
    VISIBLE_DEPTH_SIMPLIED_TREE_PNG_PATH = '../output/visible_depth_marked_skeleton_tree_by_year/'
    if not os.path.exists(SIMPLIED_TREE_PNG_PATH+str(seminal_pid)):
        os.makedirs(SIMPLIED_TREE_PNG_PATH+str(seminal_pid))
    if not os.path.exists(VISIBLE_DEPTH_GML_FILE_PATH+str(seminal_pid)):
        os.makedirs(VISIBLE_DEPTH_GML_FILE_PATH+str(seminal_pid))
    
    years = [file.split('.')[0] for file in os.listdir(COMPLETED_SKELETON_TREE_JSON+str(seminal_pid))]
    simply_ratio = pid2simply_ratio.get(seminal_pid, 0.4)
    year2visible_depth = {}  # 年份与可视深度的对应，用于挑选结构发生改变年份的脉络树
    for year in years:
        pid2color_list = get_top_entropy_pids2colorlist(seminal_pid)
        pid2node_entropy = json.load(open('../temp_files/node_entropy_by_year/'+str(seminal_pid)+'/{}'.format(year), 'r'))
        tree_node_deep = json.load(open('../temp_files/tree_deep_by_year/'+str(seminal_pid)+'/{}'.format(year), 'r'))
        visible_depths = []
        for deep in tree_node_deep:
            for p_id in tree_node_deep[deep]:
                if float(pid2node_entropy[str(p_id)]) > 10:
                    visible_depths.append(int(deep))
                    break
        max_visible_depth = 0 if len(visible_depths) == 0 else max(visible_depths)  # 找到当前年份的最大可视深度
        year2visible_depth[year] = max_visible_depth
        for p_id in tree_node_deep[str(max_visible_depth)]: # 在最大可视深度中检索所有点熵超过10的节点
            if float(pid2node_entropy[str(p_id)]) > 10:
                pid2color_list[str(p_id)] = '#ff0000'
        simply_skeleton_tree(seminal_pid, year, simply_ratio) # 通过第上一个函数写文件，下一个函数读文件进行传递数据也是可行的
        gen_entropy_tree_visual_gml(seminal_pid, year, pid2color_list)
        if not os.path.exists(VISIBLE_DEPTH_SIMPLIED_TREE_PNG_PATH+seminal_pid):
            os.makedirs(VISIBLE_DEPTH_SIMPLIED_TREE_PNG_PATH+seminal_pid)
        print(VISIBLE_DEPTH_GML_FILE_PATH+str(seminal_pid)+'/'+str(year)+'.gml')
        gml2png(VISIBLE_DEPTH_GML_FILE_PATH+str(seminal_pid)+'/'+str(year)+'.gml', VISIBLE_DEPTH_SIMPLIED_TREE_PNG_PATH+str(seminal_pid)+'/'+str(year)+'.png', label_flag=False)
    if not os.path.exists(f'../temp_files/year2visible_depth/'):
        os.makedirs(f'../temp_files/year2visible_depth/')
    json.dump(year2visible_depth, open(f'../temp_files/year2visible_depth/{seminal_pid}.json', 'w'))

if __name__=="__main__":
    gen_visible_depth_marked_skeleton_tree_png('102857695')