import random

adjective_list = ["shy", "anxious", "fiery", "nervous", "nice", "pessimistic", "optimistic", "calm", "generous", "clever","ambient"]
noun_list = ["street", "lightbulb", "apple", "pear", "cherry", "electron", "proton", "phenomenon", "candle", "ameoba", "sunrise","thought", "daemon"]

def get_random_username():
	return "{} {}".format(random.choice(adjective_list), random.choice(noun_list))