import os
from tqdm import tqdm
from multiprocessing.pool import Pool

from gen_intermediate_files import gen_intermediate_files
from vis_idea_tree_by_dot import gen_dot_vis_idea_tree_png
from gen_KE_and_VD_evolution_pics import visible_depth_evoluation


def main(pids):

	print('generating intermediate files...')
	for pid in tqdm(pids):
		gen_intermediate_files(pid)
	finished_pids = []
	for pp_id in os.listdir('../temp_files/attributed_idea_tree_by_year/'):
		if os.path.isfile(f'../temp_files/attributed_idea_tree_by_year/{pp_id}/{str(datetime.datetime.now().year)}.gml'):
			finished_pids.append(pp_id)

	#################################################使用DOT可视化idea tree##############################################################
	print('geting idea trees...')
	process_num = len(pids) if len(pids) <= 40 else 40
	with Pool(process_num) as pool:
		pool.map(visible_depth_evoluation, pids)
	process_num = len(pids) if len(pids) <= 40 else 40
	with Pool(process_num) as pool:
		pool.map(gen_dot_vis_idea_tree_png, pids)
	print("Idea tree dot vis finish!")
	

if __name__ == "__main__":
	pids = ['15851315', '12445429']  # 列表中存放需要提取idea tree的GML文件的ID（GML文件的命名方式是ID.gml）
	main(pids)