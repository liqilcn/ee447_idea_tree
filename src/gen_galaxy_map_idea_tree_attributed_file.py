import networkx as nx
import random
from readgml import readgml
import csv
from networkx.utils import is_string_like
import os
import time
import json
from tqdm import tqdm_notebook as tqdm
from multiprocessing.pool import Pool



SOURCE_GML_FILE_PATH = '../temp_files/source_gml/'
DETAIL_GML_FILE_PATH = '../temp_files/rencent_galaxy_map_to_layout/'


# In[14]:


def get_edge_color_by_mixe_node_color(source_color, target_color):
    # 用于将节点颜色进行混合，进而得到边的颜色
    r = str(hex(int((int(source_color[1:3], 16) + int(target_color[1:3], 16)) / 2)))
    g = str(hex(int((int(source_color[3:5], 16) + int(target_color[3:5], 16)) / 2)))
    b = str(hex(int((int(source_color[5:7], 16) + int(target_color[5:7], 16)) / 2)))
    if len(r.split('x')[1]) == 1:
        r = '0' + r.split('x')[1]
    else:
        r = r.split('x')[1]
    if len(g.split('x')[1]) == 1:
        g = '0' + g.split('x')[1]
    else:
        g = g.split('x')[1]
    if len(b.split('x')[1]) == 1:
        b = '0' + b.split('x')[1]
    else:
        b = b.split('x')[1]
    return '#' + r + g + b


# In[4]:


def generate_gml(G):
    # gml图生成器直接将networkx源代码进行修改
    # recursively make dicts into gml brackets
    def listify(d,indent,indentlevel):
        result='[ \n'
        for k,v in d.items():
            if type(v)==dict:
                v=listify(v,indent,indentlevel+1)
            result += (indentlevel+1)*indent + string_item(k,v,indentlevel*indent)+'\n'
        return result+indentlevel*indent+"]"

    def string_item(k,v,indent):
        # try to make a string of the data
        if type(v)==dict: 
            v=listify(v,indent,2)
        elif is_string_like(v):
            v='"%s"'%v
        elif type(v)==bool:
            v=int(v)
        return "%s %s"%(k,v)

    # check for attributes or assign empty dict
    if hasattr(G,'graph_attr'):
        graph_attr=G.graph_attr
    else:
        graph_attr={}
    if hasattr(G,'node_attr'):
        node_attr=G.node_attr
    else:
        node_attr={}

    indent=2*' '
    count=iter(range(len(G)))
    node_id={}

    yield "graph ["
    if G.is_directed():
        yield indent+"directed 1"
    # write graph attributes 
    for k,v in G.graph.items():
        if k == 'directed':
            continue
        yield indent+string_item(k,v,indent)
    # write nodes
    for n in G:
        yield indent+"node ["
        # get id or assign number
        #nid=G.node[n].get('id',next(count))
        #node_id[n]=nid
        nid = n
        node_id[n]=n
        # 上两行对原代码进行修改，以原始输入的id作为输出图文件的id
        yield 2*indent+"id %s"%nid
        label=G.node[n]['L']
        if is_string_like(label):
            label='"%s"'%label
        yield 2*indent+'label %s'%label
        if n in G:
          for k,v in G.node[n].items():
              if k=='id' or k == 'label' or k == 'L': continue
              yield 2*indent+string_item(k,v,indent)
        yield indent+"]"
    # write edges
    for u,v,edgedata in G.edges(data=True):
        source_color = G.node[u]['graphics']['fill']
        target_color = G.node[v]['graphics']['fill']
        yield indent+"edge ["
        yield 2*indent+"source %s"%u
        yield 2*indent+"target %s"%v
        yield 2*indent+"value 1.0"
        yield 2*indent+"color "+ get_edge_color_by_mixe_node_color(source_color, target_color)
        yield indent+"]"
    yield "]"


# In[18]:


def gen_galaxy_map_idea_tree_attributed_file(seminal_paper_id):
    
    seminal_paper_id = seminal_paper_id
    nodes, edges = readgml.read_gml(SOURCE_GML_FILE_PATH + str(seminal_paper_id) + '.gml')
    
    G = nx.DiGraph()
    id2title = {} # id到title的映射
    id2citated_paper = {}
    index2id = {} # igraph自动将节点id进行了索引
    # 读取原始数据
    i = len(nodes)

    for node in nodes:
        G.add_node(str(node['id']),graphics = {'w':0,'h':0,'d':0,'fill':''}, L = '')
        id2title[str(node['id'])] = node['label']
    for edge in edges:
        G.add_edge(str(edge['source']), str(edge['target']))
        if str(edge['target']) not in id2citated_paper:
            id2citated_paper[str(edge['target'])] = []
            id2citated_paper[str(edge['target'])].append(str(edge['source']))
        else:
            id2citated_paper[str(edge['target'])].append(str(edge['source']))
    # 写入size
    id2in_degree = {}
    max_in_degree = 0
    for node in G.node:
        id2in_degree[node] = G.in_degree(node)
        if G.in_degree(node) > max_in_degree:
            max_in_degree = G.in_degree(node)
    max_node_sixe = 130 + int((i - 1000)/100)*2.5
    for node in G.node:
        try:
            G.node[node]['graphics']['w'] = G.in_degree(node) / max_in_degree * max_node_sixe + 10
            G.node[node]['graphics']['h'] = G.in_degree(node) / max_in_degree * max_node_sixe + 10
            G.node[node]['graphics']['d'] = G.in_degree(node) / max_in_degree * max_node_sixe + 10
        except:
            print(node)
            print(G.node[node])
    
    # 写入label
    citation_list = sorted(id2in_degree.items(), key = lambda item:item[1], reverse=True)
    title_list = [(i - 1000)/100]
    title_num = 15 + int((i - 1000)/1000*8)
#     title_num = 25 + int((i - 1000)/1000*8)
    for i in range(title_num):
          G.node[citation_list[i][0]]['L'] = id2title[citation_list[i][0]]
    # 写入节点颜色
    # 找到7个引用量较大的子领域，找到一个集合后，从总体节点中删掉这一集合，然后在剩下的所有节点中再找到一个集合，如此反复
    semial_paper_color = '#fc0706'
    base_paper_color = '#2e5bff'
    color_list = [
        '#38f510', # 绿
        '#f8f014', # 黄
        '#ff33cc', # 紫红
        '#9933ff', # 紫
        '#ff9933', # 橙
        '#cccc00', # 青
        '#993366', # 浅紫
        '#9858ae'
    ]
    G.node[seminal_paper_id]['graphics']['fill'] = semial_paper_color # 将开山作设置为红色
    id2in_degree.pop(seminal_paper_id) # 去除上色完成的节点
    for i in range(7):
        if not id2in_degree:
            break
        citation_list = sorted(id2in_degree.items(), key = lambda item:item[1], reverse=True)
        G.node[citation_list[0][0]]['graphics']['fill'] = color_list[i]
        id2in_degree.pop(citation_list[0][0])
        try:
            for node in list(set(id2citated_paper[citation_list[0][0]]).intersection(set(id2in_degree.keys()))):
                G.node[node]['graphics']['fill'] = color_list[i]
                try:
                    id2in_degree.pop(node)
                except:
                    pass
        except:
            pass
    if id2in_degree:
        for key in id2in_degree:
            G.node[key]['graphics']['fill'] = base_paper_color
    if not os.path.exists(DETAIL_GML_FILE_PATH):
        os.makedirs(DETAIL_GML_FILE_PATH)
    with open(DETAIL_GML_FILE_PATH+str(seminal_paper_id)+'.gml', 'w') as fp:
        for line in generate_gml(G):
            line+='\n'
            fp.write(line)
    # print(f"{seminal_paper_id} attributed")