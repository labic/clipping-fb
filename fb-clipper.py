#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
from os import listdir, chdir
from os.path import isfile, isdir
from csv import writer, QUOTE_MINIMAL
from collections import defaultdict
import json

WORD_FILTER = []

def get_N_first(dict_words, N=False, values=False):
    '''
    Return the N topwords of a list.
    '''
    aux = []
    top_words = []

    if N == 0: return aux

    for key, value in dict_words.items():
        top_words.append([key, value])

    top_words.sort(key=lambda x:x[1], reverse=True)

    if values: # [key,value]
        for item in top_words:
            aux.append([item[0], item[1]])
    else: # default; key only
        for item in top_words:
            aux.append(item[0])

    return aux[:N] if N else aux

def parse_fb_json(input_path='.', word_filter=[]):

    q = []

    PROFILE = ""

    dict_info = defaultdict(dict)
    dict_shares = defaultdict(int)
    dict_angry_filter = defaultdict(int)
    dict_angry_unfilter = defaultdict(int)
    dict_profile = defaultdict(int)
    dict_filter = defaultdict(int)
    dict_unfilter = defaultdict(int)

    for j in listdir(input_path):

        if j.endswith('.json'):
        
            print(j)
            with open(j, "r") as read_file:
                data = json.load(read_file)

            if 'data' in data:

                pass
                # try: # PAGES
                #     HEADER = ['id', 'message', 'story', 'created_time']
                #     for i in data['data']:
                #         story = i['story'].replace('\n',' ').replace('\r','') if 'story' in i else ''
                #         created_time = i['created_time'] if 'created_time' in i else ''
                #         try: message = i['message'].replace('\n',' ').replace('\r','') if 'message' in i else ''
                #         except Exception as e: print(str(e))
                #         str_id = i['id'] if 'id' in i else ''
                # except Exception as e:
                #     if 'error' in data\
                #     and 'message' in data['error']:
                #         print(j, '=>', data['error']['message'])
                #     else: print(str(e))

            else: # single post

              try: # POSTS
                  HEADER = ['id', 'message', 'from_name', 'created_time', 'shares_count', 'comments', 'love', 'wow', 'haha', 'sad', 'angry', 'like']
                  
                  if any(i in data for i in ['message', 'story']):
                      str_id = str(data['id']).replace('\r','').replace('\n','')
                      try: message = str(data['message']).replace('\r','').replace('\n',' ') if 'message' in data else ''
                      except Exception as e: print(str(e))
                      from_name = str(data['from']['name']).replace('\r','').replace('\n','')
                      created_time = str(data['created_time']).replace('\r','').replace('\n','')
                      if 'shares' in data:
                          shares_count = str(data['shares']['count']).replace('\r','').replace('\n','')
                      else: shares_count = '0'
                      comments_summary_total_count = str(data['comments']['summary']['total_count']).replace('\r','').replace('\n','')
                      reactions_love_summary_total_count = str(data['reactions_love']['summary']['total_count']).replace('\r','').replace('\n','')
                      reactions_wow_summary_total_count = str(data['reactions_wow']['summary']['total_count']).replace('\r','').replace('\n','')
                      reactions_haha_summary_total_count = str(data['reactions_haha']['summary']['total_count']).replace('\r','').replace('\n','')
                      reactions_sad_summary_total_count = str(data['reactions_sad']['summary']['total_count']).replace('\r','').replace('\n','')
                      reactions_angry_summary_total_count = str(data['reactions_angry']['summary']['total_count']).replace('\r','').replace('\n','')
                      reactions_like_summary_total_count = str(data['reactions_like']['summary']['total_count']).replace('\r','').replace('\n','')

                      dict_info[str_id]['message'] = message
                      dict_info[str_id]['from_name'] = from_name
                      dict_info[str_id]['created_time'] = created_time
                      dict_info[str_id]['shares_count'] = shares_count
                      dict_info[str_id]['comments_summary_total_count'] = comments_summary_total_count
                      dict_info[str_id]['reactions_love_summary_total_count'] = reactions_love_summary_total_count
                      dict_info[str_id]['reactions_wow_summary_total_count'] = reactions_wow_summary_total_count
                      dict_info[str_id]['reactions_haha_summary_total_count'] = reactions_haha_summary_total_count
                      dict_info[str_id]['reactions_sad_summary_total_count'] = reactions_sad_summary_total_count
                      dict_info[str_id]['reactions_angry_summary_total_count'] = reactions_angry_summary_total_count
                      dict_info[str_id]['reactions_like_summary_total_count'] = reactions_like_summary_total_count

                      if from_name in ['Renato Casagrande', 'Aridelmo Teixeira', 'Jackeline Rocha', 'André Moreira', 'Manato', 'Rose de Freitas']:
                          dict_profile[str_id] = int(shares_count)
                          PROFILE = from_name
                      else: dict_shares[str_id] = int(shares_count)

                      if (any(a in message.lower() for a in word_filter)):
                          dict_filter[str_id] = int(shares_count)
                          dict_angry_filter[str_id] = int(reactions_angry_summary_total_count)
                      else: # geral
                          dict_unfilter[str_id] = int(shares_count)
                          dict_angry_unfilter[str_id] = int(reactions_angry_summary_total_count)

                      q.append([
                       str_id,
                       message,
                       from_name,
                       created_time,
                       shares_count,
                       comments_summary_total_count,
                       reactions_love_summary_total_count,
                       reactions_wow_summary_total_count,
                       reactions_haha_summary_total_count,
                       reactions_sad_summary_total_count,
                       reactions_angry_summary_total_count,
                       reactions_like_summary_total_count])
                  elif 'error' in data\
                  and 'message' in data['error']:
                      print(j, '=>', data['error']['message'])
              except Exception as e:
                  raise#print(str(e))

    with open('posts.tab', 'w', newline='', encoding='utf8') as f:
      file_writer = writer(f, delimiter='\t', quoting=QUOTE_MINIMAL)
      file_writer.writerow(HEADER)
      for line in q:
          file_writer.writerow(line)

    with open('clipping.txt', 'w', newline='', encoding='utf8') as f:
        count = 0
       
        if PROFILE == "":

          for i in get_N_first(dict_filter, 20):
            count += 1
            m = str(count)+')   ' + dict_info[i]['from_name']+'\nMensagem: '+dict_info[i]['message'][:500]+\
              '\nRaiva: ' + dict_info[i]['reactions_angry_summary_total_count']+\
              ' Haha: ' + dict_info[i]['reactions_haha_summary_total_count']+\
              ' Triste: ' + dict_info[i]['reactions_sad_summary_total_count']+\
              ' Uau: ' + dict_info[i]['reactions_wow_summary_total_count']+\
              ' Amei: ' + dict_info[i]['reactions_love_summary_total_count']+\
              '\nCurtidas: ' + dict_info[i]['reactions_like_summary_total_count']+\
              ' Comentários: ' + dict_info[i]['comments_summary_total_count']+\
              ' Compartilhamentos: ' + dict_info[i]['shares_count']+\
              '\nLink: https://www.facebook.com/'+i+'\n'
            f.write(m+'\n')

          f.write('Com mais reações de indignação:\n\n')
          count = 0

          for i in get_N_first(dict_angry_filter, 5):
              count += 1
              m = str(count)+')   ' + dict_info[i]['from_name']+'\nMensagem: '+dict_info[i]['message'][:500]+\
                '\nRaiva: ' + dict_info[i]['reactions_angry_summary_total_count']+\
                ' Haha: ' + dict_info[i]['reactions_haha_summary_total_count']+\
                ' Triste: ' + dict_info[i]['reactions_sad_summary_total_count']+\
                ' Uau: ' + dict_info[i]['reactions_wow_summary_total_count']+\
                ' Amei: ' + dict_info[i]['reactions_love_summary_total_count']+\
                '\nCurtidas: ' + dict_info[i]['reactions_like_summary_total_count']+\
                ' Comentários: ' + dict_info[i]['comments_summary_total_count']+\
                ' Compartilhamentos: ' + dict_info[i]['shares_count']+\
                '\nLink: https://www.facebook.com/'+i+'\n'
              f.write(m+'\n')

          f.write('\n\nGERAL\n\n')
          count = 0

          for i in get_N_first(dict_unfilter, 20):
            count += 1
            m = str(count)+')   ' + dict_info[i]['from_name']+'\nMensagem: '+dict_info[i]['message'][:500]+\
              '\nRaiva: ' + dict_info[i]['reactions_angry_summary_total_count']+\
              ' Haha: ' + dict_info[i]['reactions_haha_summary_total_count']+\
              ' Triste: ' + dict_info[i]['reactions_sad_summary_total_count']+\
              ' Uau: ' + dict_info[i]['reactions_wow_summary_total_count']+\
              ' Amei: ' + dict_info[i]['reactions_love_summary_total_count']+\
              '\nCurtidas: ' + dict_info[i]['reactions_like_summary_total_count']+\
              ' Comentários: ' + dict_info[i]['comments_summary_total_count']+\
              ' Compartilhamentos: ' + dict_info[i]['shares_count']+\
              '\nLink: https://www.facebook.com/'+i+'\n'
            f.write(m+'\n')

          f.write('Com mais reações de indignação:\n\n')
          count = 0

          for i in get_N_first(dict_angry_unfilter, 5):
              count += 1
              m = str(count)+')   ' + dict_info[i]['from_name']+'\nMensagem: '+dict_info[i]['message'][:500]+\
                '\nRaiva: ' + dict_info[i]['reactions_angry_summary_total_count']+\
                ' Haha: ' + dict_info[i]['reactions_haha_summary_total_count']+\
                ' Triste: ' + dict_info[i]['reactions_sad_summary_total_count']+\
                ' Uau: ' + dict_info[i]['reactions_wow_summary_total_count']+\
                ' Amei: ' + dict_info[i]['reactions_love_summary_total_count']+\
                '\nCurtidas: ' + dict_info[i]['reactions_like_summary_total_count']+\
                ' Comentários: ' + dict_info[i]['comments_summary_total_count']+\
                ' Compartilhamentos: ' + dict_info[i]['shares_count']+\
                '\nLink: https://www.facebook.com/'+i+'\n'
              f.write(m+'\n')

        else:

          f.write('\n---\n' + PROFILE + '\n---\n\n')

          for i in get_N_first(dict_shares, 7):
            count += 1
            m = str(count)+')   ' + dict_info[i]['from_name']+'\nMensagem: '+dict_info[i]['message'][:500]+\
              '\nRaiva: ' + dict_info[i]['reactions_angry_summary_total_count']+\
              ' Haha: ' + dict_info[i]['reactions_haha_summary_total_count']+\
              ' Triste: ' + dict_info[i]['reactions_sad_summary_total_count']+\
              ' Uau: ' + dict_info[i]['reactions_wow_summary_total_count']+\
              ' Amei: ' + dict_info[i]['reactions_love_summary_total_count']+\
              '\nCurtidas: ' + dict_info[i]['reactions_like_summary_total_count']+\
              ' Comentários: ' + dict_info[i]['comments_summary_total_count']+\
              ' Compartilhamentos: ' + dict_info[i]['shares_count']+\
              '\nLink: https://www.facebook.com/'+i+'\n'
            f.write(m+'\n')

          f.write('Perfil ' + PROFILE + ':\n\n')
          count = 0

          for i in get_N_first(dict_profile, 7):
              count += 1
              m = str(count)+')   ' + dict_info[i]['from_name']+'\nMensagem: '+dict_info[i]['message'][:500]+\
                '\nRaiva: ' + dict_info[i]['reactions_angry_summary_total_count']+\
                ' Haha: ' + dict_info[i]['reactions_haha_summary_total_count']+\
                ' Triste: ' + dict_info[i]['reactions_sad_summary_total_count']+\
                ' Uau: ' + dict_info[i]['reactions_wow_summary_total_count']+\
                ' Amei: ' + dict_info[i]['reactions_love_summary_total_count']+\
                '\nCurtidas: ' + dict_info[i]['reactions_like_summary_total_count']+\
                ' Comentários: ' + dict_info[i]['comments_summary_total_count']+\
                ' Compartilhamentos: ' + dict_info[i]['shares_count']+\
                '\nLink: https://www.facebook.com/'+i+'\n'
              f.write(m+'\n')

if __name__ == '__main__':
    input_name = '.'
    if len(argv) > 1:
      input_name = argv[1]
    parse_fb_json(input_name, WORD_FILTER)