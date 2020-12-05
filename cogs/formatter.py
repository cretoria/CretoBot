import discord
import datetime
import asyncio
import json
import urllib
import aiohttp
import random
import re
import gspread

from discord.ext import commands

message_history = '/home/pi/cretobot/formatter/msg_history.txt'

class Formatter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def compile_ops(self, ctx, start_id: int=None, end_id: int=None, *, title: str=None):

        start_msg = await ctx.channel.fetch_message(start_id)
        end_msg = await ctx.channel.fetch_message(end_id)
        war_history = await ctx.message.channel.history(before = end_msg.created_at, after = start_msg.created_at, limit = None).flatten()
#         print('\n'.join('{}'.format(message.content) for message in war_history))
        msg_content = [message.content for message in war_history]
#         print(*msg_content, sep='\n')
        format_content = '\n'.join('{}'.format(message.content) for message in war_history)
#         print(format_content)
               
        list_of_ops = format_content.split('\n')
        print('list of ops created')
        with open('msg_history.txt','w+') as f_write:
            f_write.write(format_content)
        prov_list = []
        ops_list = []
        
        print('starting prov/ops compiling')
        print(list_of_ops)
        ### now to start parsing individual ops to popualte data in the table
        firstlinecount = 0
        for line in list_of_ops:
            # determine if ops is thievery or sorcery    
            op_cat = ('thievery' if line.startswith('🕵️') == True else 'sorcery')
            # for now, splitting the line in order to single out user#
            split_line = []
            split_line = line.split()
            loc = split_line.index(next(x for x in split_line 
                                        if x.endswith("#")))
            prov = ' '.join(split_line[1:loc])+' ({})'.format(split_line[loc])

            if prov not in prov_list:
                prov_list.append(prov)

            # use regex to locate the op type
            op_type = re.search('<<__(.+?)__', line).group(1)

            print(op_type)
            if op_type not in ops_list:
                ops_list.append(op_type)

            # look for FAIL to determine if success is yes/no
            if '__FAIL__' in line:
                success = 'no'
            else:
                success = 'yes'

            if success == 'yes':
                try:
                    op_damage = re.search('>> \*\*(.+?)\*\*\|', line).group(1)
                except:
                    op_damage = None
            else:
                op_damage = 'n/a'
            firstlinecount += 1
            print('{} | {} | success: {}'.format(firstlinecount, op_type, success))

        print('Prov List and Ops List compiled.')

        data = dict([p,{o:{"attempts":0,"success":0,"damage":0} for o in ops_list}] for p in prov_list)
        line_count = 0
        for line in list_of_ops:
    
            # for now, splitting the line in order to single out user#
            split_line = line.split()
            loc = split_line.index(next(x for x in split_line 
                                        if x.endswith("#")))
            prov = ' '.join(split_line[1:loc])+' ({})'.format(split_line[loc])

            # use regex to locate the op type
            try:
                op_type = re.search('<<__(.+?)__', line).group(1)
            except:
                print('RegEx search failed at line {}, which was \n {}'.format(line_count, line))
            # look for FAIL to determine if success is yes/no
            if '__FAIL__' in line:
                success = 0
            else:
                success = 1

            if success == 1:
                try:
                    op_damage = int(re.search('>> \*\*(.+?)\*\*\|', line).group(1))
                except:
                    op_damage = 0
            else:
                op_damage = 0

            line_count += 1
            print('{} {}'.format(line_count,op_type))
            for p, q in data.items():
                if p == prov:
#                     print('{} did {}.'.format(prov,op_type))
                    q[op_type]['attempts'] += 1
                    q[op_type]['success'] += success
                    q[op_type]['damage'] += op_damage
        
        with open('ops_output.json', 'w+') as outf:
            json.dump(data, outf, indent=4, sort_keys=True)
        
        print('about to start converting to table')
        # first separate out the op types for the header row
        for k, v in data.items():
            header_row = list(v)
            break

        # we'll start buiding the html line by line, starting with the header row
        # basic html tags will be added later
        header_row.insert(0,'Province')     # need to insert column name for provs

        table_rows = []
        table_rows.append(','.join('{}'.format(h.title()) for h in header_row))

        # now let's start populating the table with the json data
        for k, v in data.items():
            row_data = ['{}'.format(k)]
            for x, y in v.items():
                row_data.append('{} ({}/{})'.format(y['damage'],y['success'],y['attempts']))
            table_rows.append(','.join(r for r in row_data))
            
        final_table = '\n'.join(table_rows)
        print('Converted to csv format')
        
        gc = gspread.service_account(filename='/home/pi/cretobot/formatter/service_account.json')

        ### Create new spreadsheet and share w/myself
        sh = gc.create('{} War Ops'.format(title))
        sh.share('echamp404@gmail.com', perm_type='user', role='writer')
        print(sh.id)
        gc.import_csv(sh.id, final_table)
    
        print("Sent to Sheets")
        await ctx.send('```SUCCESS```')

def setup(bot):
    bot.add_cog(Formatter(bot))
