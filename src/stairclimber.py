def climbingStaircase(n, k):

	def recurse(remaining, paths, path):
		print(remaining)
		if remaining == 0:
			paths.append(path)
		else:
			for i in range(1, k+1):
				r2 = remaining - i 
				p2 = path + [i]
				if r2 >= 0:
					recurse(r2, paths, p2)
	pts = []
	recurse(n, pts, [])
	return pts
     
# test1
print(climbingStaircase(4, 2)) 
