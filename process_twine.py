from bs4 import BeautifulSoup
import re

#helper functions which process the twine story literal into a schematic representation

link_re = "\[\[([^\[]+)\]\]"

def process_passage(passage):
	attrs = passage.attrs
	#create the sugarcube id format 
	attrs['passage_id'] = "passage-"+attrs["name"].lower().replace(" ", "-")
	attrs['title'] = attrs["name"]
	#get links from text
	link_raws = re.findall(link_re, passage.text)
	links = []
	#account for some syntax sugar going on
	for raw in link_raws:
		if "->" in raw:
			links.append(raw.split("->")[1])
		elif "|" in raw:
			links.append(raw.split("|")[1])
		else:
			links.append(raw)

	attrs["link_titles"] = links
	return attrs

def process(location_format, twine_loc):
	with open(location_format.format(twine_loc)) as tw:
		twine = tw.read()

	soup = BeautifulSoup(twine, "html.parser")
	story_title = soup.find("title").text
	passages_raw = soup.findAll("tw-passagedata")
	passages = [process_passage(p) for p in passages_raw]
	
	#We need the sugarcube id for each link for anything on the browser to work. 
	title_id_map = {p["title"]:p["passage_id"] for p in passages}
	for passage in passages:
		passage["link_ids"] = [title_id_map[link_title] for link_title in passage["link_titles"]]
	return {"story_id":twine_loc, "title":story_title, "passages":passages}