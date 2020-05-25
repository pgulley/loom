from bs4 import BeautifulSoup
import re
from pprint import pprint as pp

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

def process_file(location_format, twine_loc):
	with open(location_format.format(twine_loc)) as tw:
		twine = tw.read()

	soup = BeautifulSoup(twine, "html.parser")
	story_title = soup.find("title").text
	passages_raw = soup.findAll("tw-passagedata")
	passages = [process_passage(p) for p in passages_raw]
	
	#We need the twine engine for each link for anything on the browser to work. 
	title_id_map = {p["title"]:p["passage_id"] for p in passages}
	for passage in passages:
		passage["link_ids"] = [title_id_map[link_title] for link_title in passage["link_titles"] if "http" not in link_title]
	return {"story_id":twine_loc, "title":story_title, "passages":passages}


def process_raw(twine_raw):
	soup = BeautifulSoup(twine_raw, "html.parser")
	story_title = soup.find("title").text
	passages_raw = soup.findAll("tw-passagedata")
	passages = [process_passage(p) for p in passages_raw]
	#We need the twine engine id for each link for anything on the browser to work. 
	title_id_map = {p["title"]:p["passage_id"] for p in passages}

	for passage in passages:
		passage["link_ids"] = [title_id_map[link_title] for link_title in passage["link_titles"] if "http" not in link_title]
	return {"title":story_title, "passages":passages}

#to check new uploaded raw stories
def validate_raw(uploaded_raw):
	soup = BeautifulSoup(uploaded_raw, "html.parser")
	has_loom_js = "{LOOM_JS}" in uploaded_raw
	has_loom_css = "{LOOM_CSS}" in uploaded_raw
	twine_tag = soup.find("tw-storydata")
	if twine_tag is not None:
		is_twine = True
		is_sugarcube = twine_tag["format"] == "SugarCube"
	else:
		is_twine = False
		is_sugarcube = False
	return {"Missing {LOOM_JS} tag":has_loom_js, "Missing {LOOM_CSS} tag":has_loom_css, "Is not a twine story": is_twine, "Is not a sugarcube story":is_sugarcube}