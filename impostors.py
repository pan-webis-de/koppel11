'''-- Jakob Koehler & Tolga Buz
Reproduction of Koppel14
'''
#--- Parameters:
#n-gram size
n = 4 
#length of feature list
featureLength = 20000
#Score threshold (needed for open set)
threshold = 0
#number of k repetitions 
repetitions = 100
#minimum size of document 
# (increases precision, but deteriorates recall, 
# if there are many small documents)
minlen = 0
# candidates with less than this amount of words in trainingdata are not attributed to
mintrainlen = 500

#--- Imports:
from math import sqrt
import jsonhandler, random, argparse

#--- Methods:
'''- create Vector:
gets a string (e.g. Book), splits it into and returns a vector 
with all possible n-grams/features'''
def createVector(s):
	vector = {}
	words = s.split()
	for word in words:
		if len(word) <= n:
			add(vector, word)
		else:
			for i in range(len(word)-n+1):
				add(vector, word[i:i+n])
	return vector

'''- add:
adds n-grams to our featurelist-vector, if is not included yet
 (containing all possible n-grams/features)'''
def add(vector, ngram):
	if ngram in vector:
		vector[ngram] += 1
	else:
		vector[ngram] = 1

'''- selectFeatures: 
selects the x most frequent n-grams/features (x=featureLength)
to avoid a (possibly) too big featurelist'''
def selectFeatures(vector):
	if len(vector) < featureLength:
		raise NameError("Vektor zu kurz")
	print(len(vector))
	return sorted(vector, key=vector.get, reverse=True)[:featureLength]

'''- createFeatureMap:
creates Feature Map that only saves 
the features that actually appear more frequently than 0.
Thus, the featurelist needs less memory and can work faster'''
def createFeatureMap(s, features):
	fmap = {}
	vec = createVector(s)
	for ngram in features:
		if ngram in vec:
			fmap[ngram] = vec[ngram]
	return fmap

'''- cosSim:
calculates cosine similarity of two vectors v1 and v2.
-> cosine(X, Y) = (X * Y)/(|X|*|Y|)
'''
def cosSim(v1, v2):
	sp = float(0)
	len1 = 0
	len2 = 0
	for ngram in v1:
		len1 += v1[ngram]**2
	for ngram in v2:
		len2 += v2[ngram]**2
	len1 = sqrt(len1)
	len2 = sqrt(len2)
	for ngram in v1:
		if ngram in v2:
			sp += v1[ngram]*v2[ngram]
	return sp/(len1*len2)

'''- minmax:
calculates minmax similarity of two vectors v1 and v2.
-> minmax(X, Y) = sum(min(Xi, Yi))/sum(max(Xi, Yi))

This baseline method will be used for further evaluation.
'''
def minmax(v1, v2):
	minsum = 0
	maxsum = 0 
	for ngram in v1:
		if ngram in v2: 
			#ngram is in both vectors
			minsum += min(v1[ngram], v2[ngram])
			maxsum += max(v1[ngram], v2[ngram])
		else:
			#ngram only in v1
			maxsum += v1[ngram]
	for ngram in v2:
		if ngram not in v1:
			#ngram only in v2
			maxsum += v2[ngram]
	if maxsum == 0:
		return 0
	return float(minsum)/maxsum

'''- training: 
Turns a given string into a n-gram vector
and returns its feature list.
'''
def training(s):
	print("training...")
	vec = createVector(s)
	print("selecting features...")
	fl = selectFeatures(vec)
	print("done")
	return fl

'''- testSim: 
args: two vectors, a featurelist 
and func(to decide whether to use cosine or minmax similarity).

uses createFeatureMap and cosSim or minmax 
and returns the similarity value of the two vectors
'''
def testSim(x, y, fl, func):
	fx = createFeatureMap(x, fl)
	fy = createFeatureMap(y, fl)
	if func == 0:
		return cosSim(fx, fy)
	else:
		return minmax(fx, fy)
		
'''- getRandomString: 
Returns a random part of a string s 
that has a given length
'''
def getRandomString(s, length):
	words = s.split()
	r = random.randint(0, len(words)-length)
	return "".join(words[r:r+length])

#--- main:
def main():
	#
	parser = argparse.ArgumentParser(description="Tira submission for PPM approach (teahan03)")
	parser.add_argument("-i", action="store", help="path to corpus directory")
	parser.add_argument("-o", action="store", help="path to output directory")
	args = vars(parser.parse_args())

	corpusdir = args["i"]
	outputdir = args["o"]
	if corpusdir == None or outputdir == None:
		parser.print_help()
		return
	
	candidates = jsonhandler.candidates
	unknowns = jsonhandler.unknowns
	jsonhandler.loadJson(corpusdir)
	jsonhandler.loadTraining()

	texts = {}
	#texts = frozenset() would this work??
	corpus = ""
	print("loading texts for training")
	deletes = []
	for cand in candidates:
		texts[cand] = ""
		for file in jsonhandler.trainings[cand]:
			texts[cand] += jsonhandler.getTrainingText(cand, file)
			#if frozenset() is used:
			#texts.add(jsonhandler.getTrainingText(cand, file))
			print("text "+file+" read")
		if len(texts[cand].split()) < mintrainlen:
			del texts[cand]
			deletes.append(cand)
		else:
			corpus += texts[cand]

	newcands = []
	for cand in candidates:
		if cand not in deletes:
			newcands.append(cand)
	candidates = newcands
	words = [len(texts[cand].split()) for cand in texts]
	minwords = min(words)
	print(minwords)

	fl = training(corpus)
	authors = []
	scores = []


	for file in unknowns:
		print("testing "+file)
		utext = jsonhandler.getUnknownText(file)
		ulen = len(utext.split())
		if ulen < minlen:
			authors.append("None")
			scores.append(0)
		else:
			wins = [0]*len(candidates)
			textlen = min(ulen, minwords)
			print(textlen)
			ustring = "".join(utext.split()[:textlen])
			for i in range(repetitions):
				rfl = random.sample(fl, len(fl)//2)
				sims = []
				for cand in candidates:
					candstring = getRandomString(texts[cand], textlen)
					sims.append(testSim(candstring, ustring, rfl, 1))
				wins[sims.index(max(sims))] += 1
			score = max(wins)/float(repetitions)
			if score >= threshold:
				authors.append(candidates[wins.index(max(wins))])
				scores.append(score)
			else: 
				authors.append("None")
				scores.append(score)

	print("storing answers")
	jsonhandler.storeJson(outputdir, unknowns, authors, scores)

main()
