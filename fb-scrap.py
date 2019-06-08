#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# A simple Facebook page/post scraper.
#
# usage: fb-scrap [idpage_list.txt] {2018/05/21}

from clipper import parse_fb_json
from csv import reader, QUOTE_MINIMAL
from datetime import datetime
from json import dump as json_dump
from json import load as json_load
from os import chdir, getcwd, makedirs
from os.path import abspath, basename, isdir, isfile
from requests import get
from sys import argv
from time import time, sleep

# script configuration
ATTEMPTS = 3 # to get JSON
SECONDS = 600 # to sleep
GET_POSTS = True # True/False
FILTER_DATE = '' # 'YYYY-MM-DD'

# required for Facebook authentication
TOKEN = ""

def scrap_pages(input_name, str_date=FILTER_DATE, get_posts=GET_POSTS, token=TOKEN, folder='output'):
    '''
    Writes output JSON from facebook page IDs in a string, list or file.
    '''
    delimiter = None
    page_ids = []
    path = abspath(getcwd())

    if isfile(input_name):
        folder = folder + '/' + input_name.replace('/','_')
        print('Reading', input_name, 'file...', end=' ')
        # check file header
        with open(input_name, 'rt', encoding='utf8') as input_file:
            input_reader = reader(input_file)
            header = next(input_reader)
        # find out delimiter
        for i in ['|', '\t', '\\t', ';', ',']:
            if i in str(header): # \\t != \t
                delimiter = i.replace('\\t','\t')
        # read whole file
        with open(input_name, 'rt', encoding='utf8') as input_file:
            if delimiter:
                input_reader = reader(input_file, delimiter=delimiter, quoting=QUOTE_MINIMAL)
                header = next(input_reader) # skips first line
                for line in input_reader:
                    try: page_ids.append(line[0])
                    except Exception as e: print('Warning: line', str(input_reader.line_num) + ',', str(e) + '.')
            else: # whole lines
                input_reader = reader(input_file)
                for line in input_reader:
                    try: page_ids.append(line[0].replace('\n',''))
                    except Exception as e: print('Warning: line', str(input_reader.line_num) + ',', str(e) + '.')

    elif isinstance(input_name, str):
        page_ids = input_name.replace(', ',',').split(',')

    len_ids = len(page_ids)
    base = 'https://graph.facebook.com/v3.1/'
    access_token = "?access_token=%s" % TOKEN
    endpoint = "/posts/"
    now = 0 # counter

    if len_ids > 1:
        print(len_ids, 'pages.')

    for page_id in page_ids:

        output_file = 'page_' + page_id + '.json'
        output_folder = abspath(folder)

        retry = 0 # stops at 3rd attepmpt
        now += 1 # add page ID to counter

        # create directory
        try: makedirs(output_folder)
        except: pass

        # change directory
        chdir(output_folder)\
        if isdir(output_folder)\
        else None

        print('('+str(now)+'/'+str(len_ids)+')', page_id, end=' ')

        while True:
            url = base + page_id + endpoint + access_token
            retry += 1
            sleep(0.5)

            if isinstance(ATTEMPTS,int) and retry > ATTEMPTS:
                break

            try: # get page data from Facebook
                output = get(url)
                data = output.json()

                with open(output_file, 'w') as f:
                    json_dump(data, f)

                if 'data' in data:
                    break

                elif 'error' in data:

                    if 'message' in data['error']:
                        print(data['error']['message'])

                        if 'Application request limit reached' in data['error']['message']:
                            sleep_seconds(SECONDS)

                        elif 'was migrated to page ID' in data['error']['message']:
                            new_page_id = data['error']['message'].split('was migrated to page ID ')[1].split('.')[0]
                            print('Updated', page_id, 'to', new_page_id, '. Retrying...')
                            page_id = new_page_id

                    else: print(data['error'])

                else: print('empty')

            except Exception as e:
                print(str(e))

        if get_posts: # requires v2.9 authentication
            scrap_posts(output_file, str_date, token)

        chdir(path)

def scrap_posts(input_file, str_date=FILTER_DATE, token=TOKEN):
    '''
    Writes output JSON from facebook post IDs in a string, list or file.
    '''
    counter = 0
    base = 'https://graph.facebook.com/v2.9/'
    access_token = "&access_token=%s" % TOKEN
    fields = '?fields=id,message,story,from,created_time,shares,'+\
             'comments.limit(0).summary(total_count).as(comments),'+\
             'reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),'+\
             'reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),'+\
             'reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),'+\
             'reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),'+\
             'reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),'+\
             'reactions.type(LIKE).limit(0).summary(total_count).as(reactions_like)'

    with open(input_file) as f:
        page_data = json_load(f)

    if 'data' in page_data:
        try: print('-', len(page_data['data']), 'posts...')
        except: print('0 posts'); return
    else: print('no data'); return

    for post in page_data['data']:

        retry = 0
        counter += 1
        post_id = post['id']
        output_file = 'post_'+post_id+'.json'
        created_time = post['created_time']
        url = base + post_id + fields + access_token

        # filter YYYY-MM-DD
        if str_date and str_date not in post['created_time']:
            continue
        print(str(counter), end=' ')

        while True:

                retry += 1

                if isinstance(ATTEMPTS,int) and retry > ATTEMPTS:
                    break

                try: # get post data from Facebook

                    sleep(0.5)
                    output = get(url)

                    if retry > ATTEMPTS:
                        break

                    data = output.json()

                    if 'error' in data:

                        if 'message' in data['error']:
                            print(data['error']['message'])

                            if 'Application request limit reached' in data['error']['message']:
                                sleep_seconds(SECONDS)

                        # else: print(data['error'])

                    else: break

                except Exception as e:
                    print(str(e))

        with open(output_file, 'w') as f:
            json_dump(data, f)

    print('done')

def sleep_seconds(tts):
    '''
    Sleeps for a given amount of seconds.
    '''
    ttw = datetime.fromtimestamp(int(time() + tts))
    ttw = datetime.strftime(ttw, "%H:%M:%S")
    print('sleeping', str(int(tts)) + 's until', ttw + '...')
    sleep(tts)

if __name__ == '__main__':
    if len(argv) > 1:
        input_name = argv[1]
    else: quit('usage: fb-scrap [page_id_list.txt] [2018/05/21]')
    str_date = FILTER_DATE
    if len(argv) > 2:
        str_date = argv[2]
    scrap_pages(input_name, str_date)