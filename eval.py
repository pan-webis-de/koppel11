import json, os
from sys import argv

corpusdir = ""
OUT_FNAME = "out.json"
TRUTH_FNAME = "ground-truth.json"

def eval():
	if len(argv) != 2:
		print("Syntax: python eval.py MAIN_FOLDER")
		return

	global corpusdir
	corpusdir = argv[1]
	
	ofile = open(os.path.join(corpusdir, OUT_FNAME), "r")
	tfile = open(os.path.join(corpusdir, TRUTH_FNAME), "r")
	ojson = json.load(ofile)
	tjson = json.load(tfile)
	ofile.close()
	tfile.close()

	succ = 0
	fail = 0
	sucscore = 0
	failscore = 0
	for i in range(len(tjson["ground-truth"])):
	#for i in range(len(ojson["answers"])):
		if tjson["ground-truth"][i]["true-author"] == ojson["answers"][i]["author"]:
			succ += 1
			sucscore += ojson["answers"][i]["score"]
		else:
			fail += 1
			failscore += ojson["answers"][i]["score"]
			
	print("Fail: "+str(fail))
	print("Success: "+str(succ))
	print("Accuracy: "+str(float(succ)/(succ+fail)))
	print("Fail score mean: "+str(float(failscore)/fail))
	print("Success score mean: "+str(float(sucscore)/succ))

eval()
