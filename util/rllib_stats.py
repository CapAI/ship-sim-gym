''' Read out a series '''
import json
import glob
import os

RAY_RESULTS_DIR = os.path.expanduser("~/ray_results/pbt_ship_sim")

def main():

	# Find all the params json

	js = glob.glob(os.path.join(RAY_RESULTS_DIR, "**/params.json"))
	
	print(f"{len(js)} param files found")
	for j in js:
		with open(j, "r") as f:
			d = json.load(f)

			print(d['lr'])
			# break


if __name__ == '__main__':
	main()