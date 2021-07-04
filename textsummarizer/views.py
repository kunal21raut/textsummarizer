from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Summary
from datetime import date
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.stem import PorterStemmer
# for web scrapping
from urllib.request import urlopen
import bs4 as bs
import urllib.request
import re

from bs4 import BeautifulSoup
import requests

# Create your views here.

#Login View
def login_page(request):
    if request.method == 'POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername,password=loginpassword)

        if user is not None:
            login(request,user)
            messages.success(request,"Successfully Logged In")
            return redirect('summary')
        else:
            messages.warning(request,"Invalid Credentials ! Please try again.")
            return redirect('login_page')
    return render(request,'textsummarizer/login.html')


#Register View
def register_page(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).first():
            messages.warning(request,"Username is already taken ! please try another username.")
            return redirect('summary')
        if User.objects.filter(email=email).first():
            messages.warning(request,"Email is already Registered !")
            return redirect('summary')
        
        # create user
        myuser = User.objects.create_user(username=username,email=email,password=password)
        myuser.save()
        messages.success(request,"Congratulations ! Your account has been created successfully.")
        return redirect('login_page')

    return render(request,'textsummarizer/register.html')


#logout View
@login_required(login_url='login_page')
def logout_page(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('summary')

summary2 = ''
def summary(request):
    if request.method == 'POST':
        
        original_text = request.POST['text']
        # print(original_text)
        if len(original_text) < 360:
            messages.success(request,"Your text is already a short summary.")
            return redirect('summary')
        else:
            stop_word = set(stopwords.words("english"))
            word_token = word_token = word_tokenize(original_text)

            freq_table = {}
            ps = PorterStemmer()
                
            for word in word_token:
                word = ps.stem(word)
                if word not in stop_word:
                    continue
                if word in freq_table:
                    freq_table[word] +=1
                else:
                    freq_table[word] = 1
                
            sentence = sent_tokenize(original_text)
            # Sentence Value
            sent_value = {}

            for sent in sentence:
                word_count_in_sent = (len(word_tokenize(sent)))
                #     print(word_count_in_sent,end="\t")
                    
                for wordCount in freq_table:
                    if wordCount in sent.lower():
                        if sent[:10] in sent_value:
                            sent_value[sent[:10]] += freq_table[wordCount]
                        else:
                            sent_value[sent[:10]] = freq_table[wordCount]
                    
                sent_value[sent[:10]] = (sent_value[sent[:10]])//word_count_in_sent
                
            # Average score
            sumValue = 0

            for entry in sent_value:
                sumValue += sent_value[entry]

            average = int(sumValue / len(sent_value))

            # generate summary
            sentence_count = 0

            summary = ""

            for sent in sentence:
                if sent[:10] in sent_value and sent_value[sent[:10]] > (average*1.1):
                    summary += " " + sent
                    sentence_count =+1
            
         
                
            context = {'original_text':original_text,
                        'summary':summary,
                        'len_of_summary':len(summary),
                        'lenOfOriginalText':len(original_text),
                       
                        }
            # print(context)
            global summary2
            def summary2():
                return summary

            return render(request,'textsummarizer/summary.html',context=context)

    return render(request,'textsummarizer/summary.html')

@login_required
def save_summary(request):
    shortsum = summary2()
    # print(shortsum)
    summary_save = Summary(user=request.user,body=shortsum,date_created=date.today())
    summary_save.save()
    messages.success(request,"Summary saved successfully.")
    context = {'saved_summary':shortsum}
    return render(request,"textsummarizer/saved_summary.html",context=context)


def about(request):
    return render(request,'textsummarizer/about.html')

# for Web Scrapping 
@login_required(login_url='login_page')
def webpage_summary(request):
    if request.method == 'POST':
        inputurl = request.POST['inputurl']

        scrapped_data = urllib.request.urlopen(inputurl)
        article = scrapped_data.read()

        parsed_article = bs.BeautifulSoup(article,'lxml')

        paragraphs = parsed_article.find_all('p')

        text = ""

        for p in paragraphs:
            text += p.text

        # text = " ".join(text)
        
        print(len(text))

        new_text = text.strip( )
        # print(new_text)

        print(len(new_text))

        if len(new_text) < 360:
            messages.success(request,"Your text is already a short summary.")
            return redirect('summary')
        else:
            stop_word = set(stopwords.words("english"))
            word_token = word_token = word_tokenize(new_text)

            freq_table = {}
            ps = PorterStemmer()
                
            for word in word_token:
                # word = word.replace(']','').replace('[','').replace(')','')
                word = ps.stem(word)
                
                punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
                if word not in punctuations:
                    continue
                
                if word not in stop_word:
                    if word in freq_table:
                        freq_table[word] +=1
                    else:
                        freq_table[word] = 1
                
            sentence = sent_tokenize(new_text)
            # Sentence Value
            sent_value = {}

            for sent in sentence:
                word_count_in_sent = (len(word_tokenize(sent)))
                #     print(word_count_in_sent,end="\t")
                    
                for wordCount in freq_table:
                    if wordCount in sent.lower():
                        if sent[:10] in sent_value:
                            sent_value[sent[:10]] += freq_table[wordCount]
                        else:
                            sent_value[sent[:10]] = freq_table[wordCount]
                    
                sent_value[sent[:10]] = (sent_value[sent[:10]])//word_count_in_sent
                
            # Average score
            sumValue = 0

            for entry in sent_value:
                sumValue += sent_value[entry]

            average = int(sumValue / len(sent_value))

            # generate summary
            sentence_count = 0

            web_summary = ""

            for sent in sentence:
                if sent[:10] in sent_value and sent_value[sent[:10]] > (average*1.5):
                    web_summary += " " + sent
                    sentence_count =+1
                
            context = {'original_text':new_text,
                        'web_summary':web_summary,
                        'len_of_summary':len(web_summary),
                        'lenOfOriginalText':len(new_text)
                        }
            print(len(web_summary))
            
            return render(request,'textsummarizer/webpage_summary.html',context=context)


    return render(request,'textsummarizer/webpage_summary.html')