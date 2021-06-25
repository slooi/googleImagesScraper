import os;
import traceback;
from bs4 import BeautifulSoup;
import requests;
import threading;

FOLDER_NAME = "images"
DEBUGGING_ON = False

s = requests.Session()

# TO DO IN FUTUER:
# Use thread manager not Thread

user_agent = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0",
	# "Set-Cookie": "w:1"
}

def read_file(file_name):
	# If file exists: return array of urls made from file contents 
	# Else: return 0
	try:
		file = open(file_name)
		url_list = [url for url in file.read().split("\n") if url != ""]

		file.close()
		return url_list
	except Exception as e:
		print("\n### ERROR:")
		print(traceback.format_exc())
		return 0

def ask_file():
	print("\n### Google Images Scraper Summary ###")
	print(" - Only one google page url per line within text file")
	print("###")
	input_file_name = input("Enter in a text file: ")

	# Check user input has a ".txt". If not, append ".txt"
	if (".txt" in input_file_name):
		print("YES")
		if input_file_name[-4:] is ".txt":
			input_file_name += ".txt"
			print(".txt already exists. Good!")
		else:
			print("Added .txt")
	else:
		input_file_name += ".txt"
		print("Added .txt")

	return input_file_name


def get_page_img_urls(page_url):
	html = s.get(page_url,headers=user_agent).content
	soup = BeautifulSoup(html,"html.parser")
	img_urls = [img_ele["data-src"] for img_ele in soup.find_all("img",{"data-deferred": False})]
	return img_urls


def download_all_urls(url_list):
	if DEBUGGING_ON:
		global debug_txt

	all_img_urls = []
	#  send http request to all urls
	for i in range(len(url_list)):
		all_img_urls.extend(get_page_img_urls(url_list[i]))
		
	#	scrap the content to get image urls
	# send http requests to all image urls and down load the images
	
	t_list = []
	for i in range(len(all_img_urls)):
		t = threading.Thread(target=download_img,args=([all_img_urls[i]]))
		t.id = i
		t.start()
		t_list.append(t)

		if DEBUGGING_ON:
			debug_txt.write("{}\n".format(all_img_urls[i]))

	[t.join() for t in t_list]
	print("DONE DOWNLOADING ALL IMAGES")

	
	if DEBUGGING_ON:
		debug_txt.close()


def download_img(img_url):
	print("downloading: "+img_url)
	res = s.get(img_url,headers=user_agent)
	img_bin = res.content
	
	if(res.headers["Content-Type"] != "image/jpeg"):
		print("ERROR: content type is NOT jpeg")
		print('res.headers["Content-Type"] '+res.headers["Content-Type"])
	
	
	img_file = open("{}/{}.{}".format(FOLDER_NAME,threading.current_thread().id,".jpg"),"wb")
	img_file.write(img_bin)
	img_file.close()

def create_dir():
	if not os.path.isdir("./{}".format(FOLDER_NAME)):
		os.mkdir(FOLDER_NAME)

if __name__ == "__main__":
	if DEBUGGING_ON:
		debug_txt = open("debug_txt","a")

	# Keep asking user for .txt file until receive valid file
	url_list = 0
	while url_list == 0:
		# Ask user for file
		input_file_name = ask_file()
		# read inputted file 
		url_list = read_file(input_file_name)

	# Create folder
	create_dir()

	# Download all images contained in the url_list
	print("Urls to download from:")
	print(url_list)
	download_all_urls(url_list)

