import csv
import collections
import sys
import pdb
import datetime

# always adjust to current date
#date = '20190819'
date = datetime.datetime.now().strftime("%Y%m%d")

# define path variables
pmc_path = 'Input/PMC_test_levels.csv'
#snt_path = 'Input/20191204_SN-T.csv'
#snt_path = 'Input/SN-T_2020-04-15_disciplines.csv'
snt_path = 'Input/AddedSN-Tdisciplines_20200415.csv'
output_missing_PMC = date + '_whereabouts_of_PMCs_in_SN-T.csv'

def check_snt_for_pmc_completeness(pmc_code, current_pmc, pmc_level, pmc_missing_outputfile):
# skip first item 'Term' in PMC list
	if current_pmc == 'Term':
		return
	else:
			# always expect that PMC code is not found
			hit = False;
			renaming_alert = '';
			synonym_alert = '';
			domain_alert = '';
			newLabel = '';
			snt_multiplicity = 0;
			newLabel = 'not found'
			# open SN-T
			with open(snt_path, newline='', encoding='utf-8', errors = 'ignore') as SNT:
				SNT_reader = csv.reader(SNT, delimiter='|', quotechar='\'')
				# process each row in SN-T
				for row in SNT_reader:
						if (current_pmc.lower().strip() == row[29].lower().strip()):
							   hit = True
							   newLabel = 'found'
							   synonym_alert = ''
							   domain_alert = ''
							   break # break here, because a finding as prefLabel should overwrite any finding as synonym or rephrased term
                        else:
                            try: synonym = row[0]
                            except IndexError: synonym = ''
                        if (current_pmc.lower().strip() in synonym.strip().lower()):
                            checkSynonym = 'aaa' + synonym.strip().lower() + '---'
                            checkSynonym = checkSynonym.replace('"', '')
                            #print(checkSynonym)
                            pos = checkSynonym.find(current_pmc.strip().lower())
                            if not checkSynonym[pos - 2].isalpha() and (not checkSynonym[pos + len(current_pmc.strip()) + 1].isalpha() or checkSynonym[pos + len(current_pmc.strip())] in (',' + ';')):
                                print('checkSynonym: ', checkSynonym)
                                synonym_alert = row[0]
                                newLabel = row[29]
                                break
                            else:
                                try: domain = row[25]
                                except IndexError: domain = ''
                                if (current_pmc.lower().strip() in domain.strip().lower()):
                                    checkDomain = 'aaa' + domain.strip().strip('"').lower() + '---'
                                    checkDomain = checkDomain.replace('"', '')
                                    pos = checkDomain.find(current_pmc.strip().lower())
                                    print('checkDomain: ', checkDomain)
                                    print('current_pmc: ', current_pmc)
                                    print('pos :', pos)
                                    print(row[29])
                                    if not checkDomain[pos - 2].isalpha() and (not checkDomain[pos + len(current_pmc.strip()) + 1].isalpha() or checkDomain[pos + len(current_pmc.strip())] == ','):
                                        domain_alert = row[25]
                                        newLabel = row[29]

			pmc_missing_outputfile.writerow([pmc_code, current_pmc, newLabel, synonym_alert, domain_alert])




### MAIN PROGRAM BEGINS HERE ###

# MM, 8.12.18: added encoding information 'Latin-1', because script did not run otherwise on my computer
#with open(pmc_path, newline='', encoding='Latin-1') as pmcfile, open(npg_path, newline='', encoding='Latin-1') as npgfile, open(snt_path, newline='', encoding='Latin-1') as SNT, open(output_file, 'w', newline='', encoding='Latin-1') as csvout, open(output_missing, 'w', newline='') as missing, open(output_missing_PMC, 'w', newline='') as missing_PMC_stream, open(output_missing_NPG, 'w', newline='') as missing_NPG_stream:
with open(pmc_path, newline='', encoding='utf-8') as pmcfile, open(snt_path, newline='', encoding='utf-8') as SNT, open(output_missing_PMC, 'w', newline='') as missing_PMC_stream:

	# read in PMC codes and check SN-T for completeness
	pmc_reader = csv.DictReader(pmcfile, delimiter='|', fieldnames=['Level', 'Code', 'Term']) #read in PMCs
	list_of_pmcs = []
	# write heading
	CSVwriter = csv.writer(missing_PMC_stream, delimiter='|', quoting=csv.QUOTE_MINIMAL)
	CSVwriter.writerow(['Code','PMC term','New SN-T subject','Synonym','Domain'])
	for i in pmc_reader:
		list_of_pmcs.append(i)
		check_snt_for_pmc_completeness(i['Code'].strip(),i['Term'].strip(),i['Level'],CSVwriter)