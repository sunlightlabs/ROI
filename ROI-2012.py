
import urllib
import os
import csv
import gspread
import re

from datetime import datetime

from passwords import *

#from get_election_results import elect_results

#total ie spending by group
ie_total = {}
#total ie spending per candidate
candid_total = {}
org_total = {}
candids = {}
names = {}
winners = {}

print "starting..."

def common_mistakes(): 
    candidates = csv.reader(open('oops.csv', 'rU'))
    candidates.next()
    for line in candidates:
        old_name = (line[0].encode('ascii', 'ignore'))
        name = (line[1].encode('ascii', 'ignore'))
        num = (line[2].encode('ascii', 'ignore')).strip()
        names[old_name] = [num, name]
    return names
    
mistakes = common_mistakes()

def generals():
    generals = []
    reader = csv.reader(open("generals.csv", "rU"))
    reader.next()
    for line in reader:
        fec_id = (line[2].encode('ascii', 'ignore'))
        generals.append(fec_id)
    
    return generals

generals =  generals()

def Winning():
    # Login with your Google account.


    gc = gspread.login(email,password)
    doc_name = 'election_results'
    # Open a worksheet from spreadsheet with one shot
    wks = gc.open(doc_name).sheet1
    
    worksheet_data = wks.get_all_values()
    directions_row = worksheet_data[0]
    row_headers = worksheet_data[1]
    data_rows = worksheet_data[2:]
    
    winners = {}
    
    for row in data_rows:
        (fec_id, winner, name, party, office, state, district, loser) = row[:8]
        fec_id = row[0].strip()
        info = [fec_id, winner, name, party, office, state, district, loser] 
        winners[fec_id] = info
        
    if info[1] != "1" or info[7] != "1":
        print info[2], "not called yet", info[1]
    return winners
  
winners = Winning()


def IE_data_suck():
    ftum = urllib.urlopen("http://assets.sunlightfoundation.com/reporting/FTUM-data/all_expenditures.csv")
    money = csv.reader(ftum)
    for i in range(3):
        money.next()
    count = 0
    org_cand_track = []
    
    #org variables
    cand_tracker = {}

     
    for line in money:
        #assigning fields
        com_name = (line[0].encode('ascii', 'ignore'))
        com_num = (line[1].encode('ascii', 'ignore'))
        if len(com_num) < 8:
            com_num = com_name
            if len(com_num) < 1:
                com_num = count
        super = (line[2].encode('ascii', 'ignore'))
        cand_name = (line[4].encode('ascii', 'ignore'))
        support_oppose = (line[5].encode('ascii', 'ignore'))
        cand_num = (line[6].encode('ascii', 'ignore')).strip()
        if len(cand_num) < 8:
            cand_num = cand_name
            
        if mistakes.has_key(cand_num):
            cand_name = mistakes[cand_num][1]
            cand_num = mistakes[cand_num][0]

        cand_name = str(cand_name).replace('"', '').title()
        party = (line[7].encode('ascii', 'ignore'))
        state = (line[10].encode('ascii', 'ignore'))
        amount = float((line[11].encode('ascii', 'ignore')))
        pg = (line[3].encode('ascii', 'ignore')).strip()
        
        if pg != "G":
            primary = amount
            amount = 0
        elif pg == "G" and (cand_num not in generals):
            if winners.has_key(cand_num): 
                print cand_name, cand_num, "not in general"
            else:
                primary = amount
                amount = 0
                pg = "O"
        else:
            primary = 0
        
        if winners.has_key(cand_num) and winners[cand_num][1] == "1":
            win = "WON GENERAL"
        elif winners.has_key(cand_num) and winners[cand_num][7] == "1":
            win = "LOST GENERAL"
        else:
            win = "-"   
        key = com_num + "-" + cand_num
        
        #for IE total
        com_can_details = [amount, com_name, com_num, super, cand_name, support_oppose, party, state, primary, win, cand_num]
        
#Org totals
        if pg == "G":
            if org_total.has_key(com_num) and cand_tracker.has_key(com_num) and cand_num in cand_tracker[com_num]:
                if winners.has_key(cand_num) and winners[cand_num][1] == "1":
                    if support_oppose == "Support":
                        #money_win
                        org_total[com_num][3] = amount + org_total[com_num][3]
                    else:
                        #trash_money 
                        org_total[com_num][5] = amount + org_total[com_num][5]
                elif winners.has_key(cand_num) and winners[cand_num][7] == "1":
                    if support_oppose == "Oppose":
                        #money_loose 
                        org_total[com_num][4] = amount + org_total[com_num][4]
                    else:
                        #trash_money 
                        org_total[com_num][5] = amount + org_total[com_num][5]
                else:
                    org_total[com_num][5] = amount + org_total[com_num][5]
                
                org_total[com_num][2] += amount
                
                    
            elif org_total.has_key(com_num) and cand_tracker.has_key(com_num):
                org_total[com_num][6] = 1 + org_total[com_num][6]
                if winners.has_key(cand_num) and winners[cand_num][1] == "1":
                    if support_oppose == "Support":
                        #money_win
                        org_total[com_num][3] = amount + org_total[com_num][3]
                        #win_count
                        org_total[com_num][7] = 1 + org_total[com_num][7]
                    else:
                        #trash_money
                        org_total[com_num][5] = amount + org_total[com_num][5]
                elif winners.has_key(cand_num) and winners[cand_num][7] == "1":
                    if support_oppose == "Oppose":
                        #money_loose
                        org_total[com_num][4] = amount + org_total[com_num][4]
                        #loose_count
                        org_total[com_num][8] = 1 + org_total[com_num][8]
                    else:
                        #trash_money
                        org_total[com_num][5] = amount + org_total[com_num][5]
                else:
                    #trash_money
                    org_total[com_num][5] = amount + org_total[com_num][5]
                
                cand_tracker[com_num].append(cand_num)
                org_total[com_num][2] += amount
            else:
                cand_count = 1
                if winners.has_key(cand_num) and winners[cand_num][1] == "1":
                    if support_oppose == "Support":
                        money_win = amount
                        money_loose = 0
                        win_count = 1
                        loose_count = 0
                        trash_money = 0
                    
                    else:
                        money_win = 0
                        win_count = 0
                        loose_count = 0
                        money_loose = 0
                        trash_money = amount 
                        
                elif winners.has_key(cand_num) and winners[cand_num][7] == "1":
                    if support_oppose == "Oppose":
                        money_loose = amount
                        loose_count = 1
                        money_win = 0
                        win_count = 0
                        trash_money = 0
                        
                    else:
                        trash_money = amount
                        money_win = 0
                        win_count = 0
                        loose_count = 0
                        money_loose = 0
                else:
                    money_win = 0
                    win_count = 0
                    loose_count = 0
                    money_loose = 0
                    trash_money = amount
                    
                cand_tracker[com_num] = [cand_num]
                if org_total.has_key(com_num) and org_total[com_num][9] != 0:
                    info = [com_name, com_num, amount, money_win, money_loose, trash_money, cand_count, win_count, loose_count, org_total[com_num][9], 0]
                else:
                    info = [com_name, com_num, amount, money_win, money_loose, trash_money, cand_count, win_count, loose_count, primary, 0] 
                org_total[com_num] = info
                
       
        else:
            if org_total.has_key(com_num):
                org_total[com_num][9] += primary
            else:
                org_total[com_num] = [com_name, com_num, 0, 0, 0, 0, 0, 0, 0, primary,0]
                
        if org_total[com_num][2] != 0:
            roi = (org_total[com_num][3] + org_total[com_num][4])/ org_total[com_num][2] * 100
            org_total[com_num][10] = roi

        """Candidate Totals"""
        
        if candid_total.has_key(cand_num):
            candid_total[cand_num][1] = candid_total[cand_num][1] + amount
        
        else:
            candid_total[cand_num] = [cand_name, amount, cand_num]
            
        """IE totals"""    
        
        if ie_total.has_key(key):
            if ie_total[key].has_key(cand_num):
                # to access previous_amount = ie_total[com_num][cand_num][0]
                ie_total[key][cand_num][0] += amount
                ie_total[key][cand_num][8] += primary   
            else:
                ie_total[key] = {cand_num : com_can_details}  
        else: 
            ie_total[key] = {cand_num : com_can_details}
        
        count += 1
        
        if pg == "G":
            if winners.has_key(cand_num) or cand_num in generals:
                x=1
            else:
                print "Misplaced - ", cand_num, "  ", cand_name 
       
IE_data_suck()    
   
#writing files
day = str(datetime.today())[:10]

ie_name = 'ie_stats' + day + '.csv'
writer = csv.writer(open(ie_name,'wb'))
labels = ["total spent in general", "committee name", "committee number", "super pac", "candidate", "support/oppose", "party", "state", "total spent in Primary or other elections", "result", "candidate identifier"]
writer.writerow(labels)
for org in ie_total.keys():
    for k in ie_total[org]:
        writer.writerow(ie_total[org][k])

org_name = 'org_stats' + day + '.csv'
writer = csv.writer(open(org_name,'wb'))
labels = ["Committee Name", "FEC ID", "General Election Spending", "money to support winning candidates", "money to oppose loosing candidates", "Money that did not produce intended result", "number of candidates mentioned in the general", "Number of supported candidates that won", "number of opposed candidates that lost", "spending in primary or other election", "ROI"]
writer.writerow(labels)
for com in org_total.keys():
    writer.writerow(org_total[com])   

cand_name = 'cand_test' + day + '.csv'
writer = csv.writer(open(cand_name,'wb'))

for cand in candid_total.keys(): 
    writer.writerow(candid_total[cand])
    
print "done" 
