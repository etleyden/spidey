import urllib.request

test_url = "https://www.lathropschools.com/"

text = urllib.request.urlopen(test_url).read()

file = open("index2.html", "w")
file.write(str(text))
file.close()
