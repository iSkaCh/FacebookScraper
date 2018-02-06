# -*- coding: utf-8 -*-
from selenium import webdriver
from getpass import getpass
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import os
import csv 
selfProfile = "https://mbasic.facebook.com/profile.php?fref=pb"


def mfacebookToBasic(url):
    """(hikaruAi method)Reformat a url to load mbasic facebook instead of regular facebook, return the same string if
    the url don't contains facebook"""

    if "m.facebook.com" in url:
        return url.replace("m.facebook.com", "mbasic.facebook.com")
    elif "www.facebook.com" in url:
        return url.replace("www.facebook.com", "mbasic.facebook.com")
    else:
        return url





dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)


class FacebookBot(webdriver.PhantomJS):
    

    def __init__(self):
        # pathToPhantomJs ="
        """(hikaruAi method) relativePhatomJs = "\\phantomjs.exe"
        service_args = None
        if images == False:
            service_args = ['--load-images=no', ]
        if pathToPhantomJs == None:
            path = self, os.getcwd() + relativePhatomJs
        else:
            path = pathToPhantomJs
            webdriver.PhantomJS.__init__(self, path, service_args=service_args)
        """
        webdriver.PhantomJS.__init__(self, executable_path="C:\\Users\\Ska\\AppData\\Roaming\\npm\\node_modules\\phantomjs-prebuilt\\lib\\phantom\\bin\\phantomjs.exe",desired_capabilities=dcap)
        
        self.set_window_size (1000,500)
    def get(self, url):
        """(hikaruAi method )The make the driver go to the url but reformat the url if is for facebook page"""
        super().get(mfacebookToBasic(url))
        self.save_screenshot("Debug.png")

    def login(self, email, password):
        """(hikaruAi method )Log to facebook using email (str) and password (str)"""

        url = "https://mbasic.facebook.com"
        self.get(url)
        email_element = self.find_element_by_name("email")
        email_element.send_keys(email)
        pass_element = self.find_element_by_name("pass")
        pass_element.send_keys(password)
        pass_element.send_keys(Keys.ENTER)
        if self.find_element_by_class_name("bi"):
            self.find_element_by_class_name("bp").click();        
        try:
            self.find_element_by_name("xc_message")
            print("Logged in")
            return True
        except NoSuchElementException as e:
            print("Fail to login")
            return False

    def logout(self):
        """(hikaruAi method)Log out from Facebook"""

        url = "https://mbasic.facebook.com/logout.php?h=AffSEUYT5RsM6bkY&t=1446949608&ref_component=mbasic_footer&ref_page=%2Fwap%2Fhome.php&refid=7"
        try:
            self.get(url)
            return True
        except Exception as e:
            print("Failed to log out ->\n", e)
            return False
    def getReviews(self,url) :
        """extracts reviews """
        self.get(url)
        links_list =[]
        dates_list = []
        posts_list = []
        
        for a in self.find_elements_by_tag_name('a'):
            if 'activity' in a.get_attribute('href'):
                links_list.append (a.get_attribute('href'))
       
        links_list=list ( set(links_list) ) 
        for l in links_list :
            self.get(l)
            try : 
                post = self.find_element_by_tag_name('p').text
                print ( post)
                date = self.find_elements_by_tag_name('abbr')[0].text
                posts_list.append(post)
                dates_list.append(date)
                
            except Exception as e:
                #print(e)
                posts_list.append('')
                dates_list.append('')
                   
        return posts_list, links_list, dates_list
    def getPostInGroup(self, url, deep=10, moreText="Show more"):
        """Get a list of posts (list:Post) in group url(str) iterating deep(int) times in the group
        pass moreText depending of your language, i couldn't find a elegant solution for this"""

        self.get(url)
        
        
        posts = []
        comments_links = []
        dates=[]
        for n in range(deep):
            print("Searching, deep ",n)
            
           
            # the most common indicator in posts is in the html ID ... every ID starts with the string 'u_0_'
            posts_element_list = self.find_elements_by_xpath("//*[contains(@id,'u_0_')]")
            
            for p in posts_element_list :
                
                
                try:
                   
                    text= p.find_element_by_tag_name("p").text
                   
                    linkToComment = p.find_element_by_partial_link_text('Comment').get_attribute('href')
                    date = p.find_element_by_tag_name("abbr").text
                  
                    if text not in posts:
                        # the use of 'u_0_' as id search string creates duplicates and so we ignore them
                        posts.append(text)
                        comments_links.append(linkToComment)
                        dates.append(date)
                except Exception:
                    continue
            
            try:
                more = self.find_element_by_partial_link_text(
                    moreText).get_attribute('href')
                self.get(more)
            except Exception as e:
                print(e)
                print(" Can't get more posts")
                break
        print ( posts)
        return posts,comments_links,dates
    def getCommentsInPost(self, url, deep=10, moreText="View previous comments…"):
        """Get a list of posts (list:Post) in group url(str) iterating deep(int) times in the group
        pass moreText depending of your language, i couldn't find a elegant solution for this"""

        self.get(url)    
        comments = []
        dates = []
        for n in range(deep):
            if n >=0 :
                print("Searching, deep ",n)
                # in the mbasic version of facebook, every commenter's name is in a h3 tag. 
                #So to find the comments we look for the h3 tag and then we extract the 1st and second div that comes after it ( usualy the comment is in the first, but when the comment contains pictures it becomes in the second
                h_list = self.find_elements_by_tag_name('h3')
                for h in h_list :
                    try :
                        c = h.find_elements_by_xpath('following-sibling::div[1]')
                        for comment in c :
                            try: 
                                date = h.find_element_by_xpath("..").find_element_by_tag_name("abbr").text
                                comments.append(comment.text)
                                dates.append ( date )
                                print ( comment.text )
                            except Exception :
                                continue
                        
                        c = h.find_elements_by_xpath('following-sibling::div[2]')
                        for comment in c :
                            try:
                                date = h.find_element_by_xpath("..").find_element_by_tag_name("abbr").text
                                comments.append(comment.text)
                                dates.append(date)
                                print ( comment.text )   
                            except Exception :
                                continue    
                    except Exception :
                        continue                  
            try:
                more = self.find_element_by_partial_link_text(
                    moreText).get_attribute('href')
                self.get(more)
            except Exception as e:
                print(e)
                print(" Can't get more comments")
                break
        return comments,dates
    def extractPostandComments(self,url,filename):
        ''' function that extracts everything '''
        output_file = open (filename,'w',newline='',
                            encoding='utf-8')
        output = csv.writer(output_file, delimiter=',',quotechar='"')      
    
    
        posts,comments_links,post_dates = self.getPostInGroup(deep=20,url=url)  
        for i in range(len(posts)):
            print ( "post ", i , " out of " , len(posts))
            output.writerow([posts[i],'post',comments_links[i],post_dates[i] ] )
            comments,comments_dates = bot.getCommentsInPost(deep=8,url=comments_links[i] )
            for j in range ( len(comments)):
                    output.writerow([comments[j],'comment',comments_links[i],comments_dates[j] ] )
            
        output_file.close()        
if __name__ == '__main__':
    bot = FacebookBot()
    try:
        bot.login(input("email : "), getpass("password : "))
    except Exception:
        print( 'already logged ' )
    
    #bot.extractPostandComments(url="https://mbasic.facebook.com/groups/search/?groupID=SAMPLEID",filename="filename.csv") 
    bot.close()
    
    