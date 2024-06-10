from libzim.reader import Archive
import sys
import multiprocessing
import mwparserfromhell
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from unidecode import unidecode
import html

debug=False


# In Parameters
# zim file
# parallelism
# output filename

def convert_to_closest_ascii(input_string):
    pattern = r'\[\[(.*?)\]\]'

    def replace(match):
        matched_text = match.group(1)

        decoded_text = urllib.parse.unquote(matched_text)

        closest_ascii = unidecode(decoded_text)

        # Preserve existing '|' characters and replace others
        #decoded_text = ''.join(c if c == '|' else c if c.isascii() else '' for c in closest_ascii)

        return '[[' + closest_ascii + ']]'

    result = re.sub(pattern, replace, input_string)
    return result



PATH = sys.argv[1]
parallel=int(sys.argv[2])
outfile=sys.argv[3]

zim = Archive(PATH)

print("Total Articles : ",zim.all_entry_count)

workload=zim.all_entry_count // parallel

print("Work per slave : ",workload)

WORK=[]

start = 0 
stream =0


def strip_html_tags(clean_text,main_title):

    #print(clean_text)
    pattern = r"<span class=\"mw-headline\" id=\"title_0\"><span class=\"mw-page-title-main\">"+re.escape(main_title)+r"</span></span>"
    #print("Pre:",pattern)
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    pattern = r"<span class=\"mw-headline\"><i>"+re.escape(main_title)+r"<\/i></span>"
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    pattern = " title=\".*?\"| id=\".*?\"| id=\".*?\" "
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    pattern = " data-mw-group=\".*?\" "
    clean_text = re.sub(pattern, ' ', clean_text,flags=re.DOTALL)

    pattern = r"<style data.*?</style>|<script src=.*?</script>"
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    pattern = r"<a class=\"mw-disambig\" href=\"(.*?)\">(.*?)</a>"
    replacement = r"[[\1|\2]]"
    clean_text = re.sub(pattern, replacement, clean_text,flags=re.DOTALL)

    pattern = r"<a class=\"mw-redirect mw-disambig\" href=\"(.*?)\">(.*?)</a>"
    replacement = r"[[\1|\2]]"
    clean_text = re.sub(pattern, replacement, clean_text,flags=re.DOTALL)

    pattern = r"<a class=\"mw-redirect\" href=\"(.*?)\">(.*?)</a>"
    replacement = r"[[\1|\2]]"
    clean_text = re.sub(pattern, replacement, clean_text,flags=re.DOTALL)

    pattern = r"<a href=\"(.*?)\">(.*?)</a>"
    replacement = r"[[\1|\2]]"
    clean_text = re.sub(pattern, replacement, clean_text,flags=re.DOTALL)

    # [[../../../A/San_Diego_Sports_Arena|San Diego Sports Arena]]
    pattern = r"\[\[\.\.\/\.\.\/\.\.\/A\/"
    clean_text = re.sub(pattern, '[[', clean_text,flags=re.DOTALL)

    # [[../../A/San_Diego_Sports_Arena|San Diego Sports Arena]]
    pattern = r"\[\[\.\.\/\.\.\/A\/"
    clean_text = re.sub(pattern, '[[', clean_text,flags=re.DOTALL)

    clean_text = convert_to_closest_ascii(clean_text)

    pattern = r'<(a class=\"external text external\"|a class=\"external text\"|meta property|divstyle|sup class=|section data-mw|\/section|body class=\"mediawiki|summary class|details data-level|div style|div class|div id|a class=\"extiw external\"|\/div).*?>|<a id=\"top\"><\/a>|<\/body>|<tbody>|<\/tbody>|<meta/>|<a><\/a>|<wbr/>|<caption>|<\/caption>|<\/summary>|<\/details>|<abbr>|<\/abbr>'
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    # Nuke any unclassified ones but limit damage zone to avoid runaways
    pattern = r"<a .{1,100}</a>"
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)


    pattern = r"</a>"
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    pattern = r'^\s*$'
    clean_text = re.sub(pattern, '', clean_text, flags=re.MULTILINE)

    #tables

    pattern = r'<table .*?>'
    clean_text = re.sub(pattern, '\n<b>+__________________________</b>\n', clean_text,flags=re.DOTALL)

    pattern = r'<tr>|<td>|<tr .*?>|<(th |td ).*?>|<th>|</tr>'
    clean_text = re.sub(pattern, '<br>', clean_text,flags=re.DOTALL)

    pattern = r'</td>|</th>'
    clean_text = re.sub(pattern, ' / ', clean_text,flags=re.DOTALL)

    pattern = r'</table>'
    clean_text = re.sub(pattern, '\n<b>_________________________+</b>\n', clean_text,flags=re.DOTALL)

    # spam span
    #pattern = r"\<span\>\<\/span\>|\<span\> \<\/span\>"
    pattern = r'<span> </span>|<span></span>'
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)

    pattern = r'<span> </span>|<span></span>'
    clean_text = re.sub(pattern, '', clean_text,flags=re.DOTALL)
 

    return clean_text

def extract_and_write(stream,start,end,outfile):
     #status
    OUT=open("OUTPUT2/"+outfile,"w")
    for id_value in range(start, end):
        entry = zim._get_entry_by_id(id_value)
        # 'if' is to skip entries with extension like .js, .css, .svg, .png
        #if debug :
        #        print(f"GOT      : {stream} : {entry.title}")

        if re.search(r"favicon|\.(css|png|js|svg|php|txt|pdf)$", entry.title):
            if debug :
                print(f"SKIP     : {stream} : {entry.title}")
            continue

        if entry.is_redirect:
            target = entry.get_redirect_entry()
            target_item = target.get_item()
            target_title = target.title


            OUT.write("<page>\n");

            before = entry.title
            pattern = r'\&amp\;'
            title = re.sub(pattern, '&', entry.title,flags=re.DOTALL)
            pattern = r'\&'
            title = re.sub(pattern, '&amp;', title,flags=re.DOTALL)

            pattern = r'\&amp\;'
            target_title = re.sub(pattern, '&', target_title,flags=re.DOTALL)
            pattern = r'\&'
            target_title = re.sub(pattern, '&amp;', target_title,flags=re.DOTALL)

            #title = html.escape(convert_to_closest_ascii(entry.title))

            pattern = r'\&lt;i\>|\n|\&lt;/i\>'
            title=re.sub(pattern,'',title)

            OUT.write(f"<title>{title}</title>\n");

            #      <text bytes="101" xml:space="preserve">#REDIRECT [[Foreign relations of Afghanistan]]

            OUT.write(f"<text bytes=\"80055\" xml:space=\"preserve\">#REDIRECT [[{target_title}]]\n")
            OUT.write("</text>\n");
            OUT.write("</page>\n");

            if debug :
                print(f"REDIRECT : {stream} : [{title}] ({before}) to [{target_title}]")
        else:
            buffer = entry.get_item().content
            html_str = bytes(buffer).decode("UTF-8")  

            OUT.write("<page>\n");

            title = entry.title

            pattern = r'\&lt;i\>|\n|\&lt;/i\>'
            title=re.sub(pattern,'',title)

            pattern = r'\&amp\;'
            title = re.sub(pattern, '&', title,flags=re.DOTALL)
            pattern = r'\&'
            title = re.sub(pattern, '&amp;', title,flags=re.DOTALL)

            OUT.write(f"<title>{title}</title>\n");

            OUT.write("<text bytes=\"80055\" xml:space=\"preserve\">\n")

            soup = BeautifulSoup(html_str, 'html.parser')

            for tag in soup.find_all('style','span','script'):
                tag.decompose()

            body = soup.find('body')

            outtext = strip_html_tags(str(body),title)

            OUT.write(outtext)

            OUT.write("</text>\n");
            OUT.write("</page>\n");
            if debug :
                 print(f"NORMAL   : {stream} : {title}")


    print("Stream ",stream," has finished")
    OUT.close()
	


for window in range(1, zim.all_entry_count, workload):
    print(window,stream)
    end = window+workload
    if end > zim.all_entry_count:
        end=zim.all_entry_count+1
    WORK.append( (stream,window,end-1, outfile + "_" + str('{:0=3}'.format(stream)) + ".wiki") )
    stream += 1

thread=[]
	
for (a,b,c,d) in WORK:
    print("Steam : ",a," Start  : ",b," End : ",c, " File : ",d)
    thread.append (multiprocessing.Process(target=extract_and_write,args=(a,b,c,d)))

for thr in thread:
	thr.start()

t=0
print("Waiting for threads to complete");
for thr in thread:
	print("Next thread", t)
	thr.join()
	t += 1
