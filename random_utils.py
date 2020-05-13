import random
#in a separate file since these lists are kind of unweildy

adjective_list = ["shy", "anxious", "fiery", "nervous", "nice", "pessimistic", "optimistic", "calm", "generous", "clever",
			"ambient", "jaunty", "morose", "toxic", "sleepy", "sinful", "raunchy", "tall", "short"]
noun_list = ["developer", "street", "lightbulb", "apple", "pear", "cherry", "electron", "proton", "phenomenon", "candle",
			 "ameoba", "sunrise","thought", "daemon", "ghost", "ghoti", "fish", "tune", "leaf", "tree"]

def get_random_username():
	return "{} {}".format(random.choice(adjective_list), random.choice(noun_list))

def get_invite_code():
	chars = "ABCDEFGHIJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
	return "".join([random.choice(chars) for i in range(10)])
