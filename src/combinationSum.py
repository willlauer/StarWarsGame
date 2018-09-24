def combinationSum(a, s):
    
	revA = sorted(a, key = lambda x: -x)
	print(revA)
	def recurse(remaining, combinations, combination, x):
		print(remaining, combination)
		if remaining == 0:
			combinations.append(combination)
		if remaining < 0:
			return # This one didn't work out
		for i in range(x, len(revA)):
			# Move to this option
			# We have the option to add revA[i] or not
			recurse(remaining - revA[i], combinations, combination + [revA[i]], i)
	all_combinations = []
	recurse(s, all_combinations, [], 0)
	all_combinations.reverse()
	result = ''
	for c in all_combinations:
		c = sorted(c)
		s = ' '.join([str(x) for x in c])
		result = result + '(' + s + ')'

	return result

print(combinationSum([2, 3, 5, 9], 9))

