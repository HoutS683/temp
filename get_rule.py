import time
import sys
from tqdm import tqdm

list_rules = {}
list_cve = []

CVEIDS = """2015-8327
2015-4147
2015-4022
2015-3329
2015-3307
2015-2787
2015-2301
2015-1231
2015-1228
2014-9674
2014-9663
2014-9661
2014-9660
2014-9658
2014-9657
2016-5408
2016-4171
2016-2109
2016-2108
2016-0749
2016-0741
2015-4643
2015-4603
2015-4602
2015-4601
2015-4600
2015-4599
2014-8241
2010-5325
2017-14746
2017-14496
2017-14493
2017-14492
2017-14491
2017-11282
2017-11281
2017-11225
2017-11215
2016-9636
2016-9635
2016-9634
2016-7050
2018-4944
2018-4878
2018-4877
2018-1111
2017-2885
2016-6814
2015-8388
2015-8386
2015-8385
2015-3812
2015-3329
2015-2328
2015-1351
2016-7039
2016-6250
2016-5408
2016-5254
2016-5118
2016-2799
2016-2794
2016-2776
2016-2182
2016-2177
2016-1962
2016-1935
2016-1930
2010-5325
2015-8327
2015-6855
2015-6525
2015-5143
2015-4473
2015-3416
2015-3415
2015-3414
2015-3333
2015-3279
2015-3258
2015-3145
2015-3144
2015-2782
2015-2740
2015-2724
2015-2331
2015-2301
2015-2155
2015-1803
2015-1592
2015-1414
2015-1289
2015-1280
2015-1279
2015-1277
2015-1276
2015-1272
2015-1265
2015-1262
2015-1260
2015-1259
2015-1258
2015-1257
2015-1256
2015-1253
2015-1252
2015-1250
2015-1249
2015-1243
2015-1242
2015-1238
2015-1237
2015-0859
2015-0838
2014-9706
2014-9663
2014-9662
2014-9661
2014-9660
2014-9658
2014-9657
2014-9656
2014-9653
2014-8157
2014-6272
2016-7117
2016-6525
2016-6354
2016-5300
2016-5180
2016-5118
2016-5108
2016-4024
2016-3981
2016-3153
2016-3092
2016-3074
2016-2851
2016-2806
2016-2385
2016-2342
2016-2195
2016-2098
2016-2054
2016-1762
2016-1669
2016-1659
2016-1653
2016-1650
2016-1649
2016-1648
2016-1647
2016-1646
2016-1522
2016-1244
2016-1243
2016-1235
2016-0749
2016-0746
2016-0718
2015-8868
2015-8779
2015-8778
2015-8710
2015-8702
2015-8560
2015-7695
2015-5727
2015-5343
2015-1779
2015-0857
2014-9906
2014-9746
2017-1000251
2017-17432
2017-16943
2017-16921
2017-16840
2017-14867
2017-14746
2017-14496
2017-14493
2017-14492
2017-14491
2017-14176
2017-12904
2017-12865
2017-11610
2017-8817
2017-8816
2017-5522
2016-10243
2016-9636
2016-9635
2016-9634
2016-8863
2016-5178
2016-4000
2016-2368
2014-5008
2018-1000178
2018-1000140
2018-1000120
2018-1000116
2018-7600
2018-7554
2018-7553
2018-7552
2018-7551
2018-7187
2018-7186
2018-6913
2018-6789
2018-5704
2018-5379
2017-1000421
2017-17833
2017-15095
2017-12380
2017-12379
2017-12377
2017-12376
2017-12375
2017-12374
2017-12187
2017-12186
2017-12185
2017-12184
2017-12183
2017-12182
2017-12181
2017-12180
2017-12179
2017-12178
2017-12177
2017-12176
2017-7525
2017-7376
2017-2885
2017-0916
2017-0915
2015-8327
2015-6826
2015-6824
2015-6820
2015-6818
2015-5143
2015-4493
2015-4492
2015-4489
2015-4487
2015-4486
2015-4485
2015-4480
2015-4479
2015-4477
2015-4475
2015-4474
2015-4473
2015-4004
2015-3905
2015-3416
2015-3415
2015-3414
2015-3408
2015-3333
2015-3308
2015-3279
2015-3258
2015-3145
2015-3144
2015-2740
2015-2724
2015-2301
2015-2265
2015-2238
2015-1803
2015-1472
2015-1346
2015-1317
2015-1315
2015-1250
2015-1249
2015-1243
2015-1242
2015-1238
2015-1237
2015-1231
2015-1230
2015-1228
2015-1219
2015-1218
2015-1217
2015-1216
2015-1215
2015-1214
2015-1205
2015-0860
2015-0847
2015-0806
2015-0805
2015-0804
2015-0803
2015-0254
2015-0240
2014-9674
2014-9668
2014-9665
2014-9663
2014-9662
2014-9661
2014-9660
2014-9659
2014-9658
2014-9657
2014-9656
2014-9604
2014-9402
2014-7942
2014-7926
2014-7923
2016-9949
2016-7117
2016-5118
2016-3981
2016-3955
2016-3947
2016-3714
2016-3679
2016-3092
2016-2834
2016-1762
2016-1659
2016-1653
2016-1649
2016-1647
2016-1646
2016-1578
2016-0795
2016-0794
2016-0746
2016-0718
2016-0483
2015-8868
2015-8779
2015-8778
2015-8560
2015-8557
2015-7801
2015-7545
2015-1779
2014-9766
2014-9761
2017-14746
2017-14496
2017-14493
2017-14492
2017-14491
2017-14176
2016-2368
2015-1329
2018-1000300
2018-1000140
2018-1000120
2018-11410
2018-6913
2015-5143
2015-4496
2015-4493
2015-4492
2015-4489
2015-4487
2015-4486
2015-4485
2015-3812
2015-3329
2015-3145
2015-2743
2015-2740
2015-2733
2015-2731
2015-2728
2015-2726
2015-2725
2015-2724
2015-2722
2015-2716
2015-2155
2015-1351
2015-0973
2014-9674
2014-9663
2014-9660
2014-9659
2014-9658
2014-9657
2016-5841
2016-5118
2016-2776
2016-2334
2016-2177
2017-3497
2015-6131
2015-6130
2015-6108
2015-6107
2015-6104
2015-6103
2015-6097
2015-2548
2015-2530
2015-2519
2015-2515
2015-2514
2015-2513
2015-2509
2015-2506
2015-2473
2015-2464
2015-2463
2015-2462
2015-2461
2015-2460
2015-2459
2015-2458
2015-2456
2015-2455
2015-2435
2015-2432
2015-2426
2015-2373
2015-1756
2015-1699
2015-1698
2015-1697
2015-1696
2015-1695
2015-1675
2015-1645
2015-1635
2015-0096
2015-0093
2015-0092
2015-0091
2015-0090
2015-0088
2015-0081
2015-0079
2015-0014
2015-0008
2016-7274
2016-7272
2016-7256
2016-7248
2016-7212
2016-7205
2016-7182
2016-3396
2016-3393
2016-3375
2016-3368
2016-3345
2016-3304
2016-3303
2016-3301
2016-3238
2016-0195
2016-0185
2016-0184
2016-0182
2016-0178
2016-0170
2016-0153
2016-0145
2016-0142
2016-0121
2016-0101
2016-0098
2016-0092
2016-0038
2016-0015
2016-0009
2017-11885
2017-11819
2017-11781
2017-11771
2017-8727
2017-8718
2017-8717
2017-8699
2017-8696
2017-8691
2017-8682
2017-8620
2017-8589
2017-8588
2017-8565
2017-8543
2017-8528
2017-8527
2017-8464
2017-8463
2017-0294
2017-0283
2017-0272
2017-0260
2017-0250
2017-0199
2017-0108
2017-0090
2017-0089
2017-0088
2017-0087
2017-0086
2017-0084
2017-0083
2017-0072
2017-0014
2017-0004
2018-8225
2018-8174
2018-8136
2018-1016
2018-1015
2018-1013
2018-1012
2018-1010
2018-1004
2018-1003
2018-0886
2018-0883
2018-0825
2015-6131
2015-6108
2015-6107
2015-6104
2015-6103
2015-2530
2015-2519
2015-2515
2015-2514
2015-2513
2015-2509
2015-2506
2015-2464
2015-2463
2015-2462
2015-2461
2015-2460
2015-2459
2015-2458
2015-2456
2015-2455
2015-2435
2015-2432
2015-2426
2015-2373
2015-1756
2015-1699
2015-1698
2015-1697
2015-1696
2015-1695
2015-1675
2015-1635
2015-0096
2015-0093
2015-0092
2015-0091
2015-0090
2015-0088
2015-0081
2015-0079
2015-0014
2015-0008
2016-0015
2017-8464
2015-6130
2015-6125
2015-6108
2015-6107
2015-6106
2015-6104
2015-6103
2015-6097
2015-2530
2015-2519
2015-2515
2015-2514
2015-2513
2015-2510
2015-2509
2015-2506
2015-2474
2015-2473
2015-2464
2015-2463
2015-2462
2015-2461
2015-2460
2015-2459
2015-2458
2015-2456
2015-2455
2015-2435
2015-2432
2015-2426
2015-1756
2015-1699
2015-1698
2015-1697
2015-1696
2015-1695
2015-1675
2015-1645
2015-1635
2015-0096
2015-0093
2015-0092
2015-0091
2015-0090
2015-0088
2015-0081
2015-0015
2015-0014
2015-0008
2016-7274
2016-7272
2016-7256
2016-7212
2016-7205
2016-7182
2016-3396
2016-3393
2016-3375
2016-3368
2016-3345
2016-3304
2016-3303
2016-3301
2016-3238
2016-3228
2016-0195
2016-0184
2016-0178
2016-0170
2016-0153
2016-0145
2016-0121
2016-0101
2016-0098
2016-0092
2016-0038
2016-0015
2016-0009
2017-11885
2017-11781
2017-11771
2017-8728
2017-8727
2017-8718
2017-8717
2017-8699
2017-8696
2017-8691
2017-8682
2017-8620
2017-8589
2017-8588
2017-8565
2017-8543
2017-8528
2017-8527
2017-8464
2017-8463
2017-0294
2017-0293
2017-0283
2017-0272
2017-0260
2017-0250
2017-0199
2017-0108
2017-0090
2017-0089
2017-0088
2017-0087
2017-0086
2017-0084
2017-0083
2017-0072
2017-0039
2017-0014
2017-0004
2018-8225
2018-8174
2018-8136
2018-1016
2018-1015
2018-1013
2018-1012
2018-1010
2018-1004
2018-1003
2018-0886
2018-0883
2018-0825
2015-6125
2015-6108
2015-6107
2015-6104
2015-6103
2015-2530
2015-2519
2015-2515
2015-2514
2015-2513
2015-2506
2015-2464
2015-2463
2015-2461
2015-2460
2015-2459
2015-2458
2015-2456
2015-2455
2015-2435
2015-2432
2015-2426
2015-2373
2015-1756
2015-1699
2015-1698
2015-1697
2015-1696
2015-1695
2015-1675
2015-1635
2015-0096
2015-0093
2015-0092
2015-0091
2015-0090
2015-0088
2015-0081
2015-0079
2015-0015
2015-0014
2015-0008
2016-7274
2016-7272
2016-7256
2016-7217
2016-7212
2016-7205
2016-7182
2016-3396
2016-3393
2016-3375
2016-3368
2016-3345
2016-3319
2016-3301
2016-3238
2016-3228
2016-3227
2016-3203
2016-0195
2016-0184
2016-0179
2016-0178
2016-0170
2016-0153
2016-0145
2016-0121
2016-0117
2016-0101
2016-0098
2016-0092
2016-0058
2016-0046
2016-0038
2016-0015
2017-11885
2017-11781
2017-11779
2017-11771
2017-8737
2017-8728
2017-8727
2017-8718
2017-8717
2017-8699
2017-8692
2017-8686
2017-8682
2017-8620
2017-8589
2017-8588
2017-8565
2017-8543
2017-8528
2017-8527
2017-8464
2017-8463
2017-0294
2017-0293
2017-0292
2017-0291
2017-0283
2017-0272
2017-0250
2017-0199
2017-0084
2017-0023
2017-0014
2018-8225
2018-8174
2018-8136
2018-1016
2018-1015
2018-1013
2018-1012
2018-1010
2018-1004
2018-1003
2018-0886
2018-0883
2018-0825
2015-1645
2015-0096
2015-0093
2015-0092
2015-0091
2015-0090
2015-0088
2015-0015
2015-0014
2017-8487
2017-0176
2014-0230
2016-3092
2016-8735
2016-0483
2016-0746
2015-4335
2016-8339
2017-15047
2015-1763
2015-3145
2016-4543
2016-1995
2017-12545
2016-2008
2016-2007
2016-2006
2016-2005
2016-2004
2017-5808
2017-5807
2013-7422
2017-12814
2015-8608
2018-6913
2015-5380
2016-6304
2016-6303
2015-8855
2015-8854
2015-8315
2015-7182
2017-10391
2017-3250
2017-3249
2018-8154
2018-0986
2016-2385
2015-6855
2015-3456
2015-3209
2016-7161
2016-1568
2015-1779
2017-8309
2015-6849
2016-0916
2015-1920
2015-1882
2016-8919"""

'''
loc rule tu 4 file rule co san
tra ve list cac rule khong trung lap
list_rule[] = key:value = ten_cve:rule
list_cve = mang ten cac cve
'''
def get_rule():

	#list 4 file chua rule
	list_file = ["C:/Users/duongnt/Downloads/a/suricata4/total.rules",
				"C:/Users/duongnt/Downloads/a/emergingthreats/total.rules",
				"C:/Users/duongnt/Downloads/a/ptresearch_git/total.rules",
				"C:/Users/duongnt/Downloads/a/snort/total.rules"
				]
	count = 0
	duf = 0
	total = 0

	for i in list_file:
		#check lan luot 4 file
		print "checking: " + i
		afile = open(i, 'rb') 

		for line in afile:
			if "reference:cve" in line or "reference: cve" in line:
				temp_line = line.split("cve,")
				temp_list = temp_line[1].split(";", 1)
				cve_name = temp_list[0]
				if " " in cve_name:
					cve_name = cve_name[1:len(cve_name)]
				if "CVE" in cve_name or "cve" in cve_name:
					cve_name = cve_name[4:len(cve_name)]
				#print cve_name
				try:
					cve_year = int(cve_name[0:4])
				except ValueError:
					#print "Error: " + cve_name
					continue
					
				if cve_year < 2015:
					continue 
				total += 1  

				if cve_name not in list_rules:
					count += 1
					list_rules[cve_name] = temp_line[0]+"reference:cve,"+cve_name+";"+temp_list[1]
					#print list_rules[cve_name]
					list_cve.append(cve_name)
				else:
					duf += 1
 	
		afile.close()

	list_cve.sort()

	print "-------------------------------"
	print "total = " + str(total)
	print "-------------------------------"
	print "duplicate = " + str(duf)
	print "-------------------------------"
	print "=> rules = " + str(count)
	print "-------------------------------"
	
'''
tra ve cac rule co trong file excel
'''
def search_rule_in_excel():

	hits = []

	for CVEID in CVEIDS.splitlines():
		if CVEID in list_cve:
			if CVEID not in hits:
				hits.append(CVEID)

	#------------------------------------------------------------
	#cve in file excel
	hits.sort()
	print "\n-------------------------------"
	print "rules in list excel = " + str(len(hits))
	print "write to file: \"E:/code/list_rules_excel\""
	print "-------------------------------"
	wfile = open("E:/code/list_rules_excel", 'w+')
	wfile.write("Total: " + str(len(hits)) + " rules")
	wfile.write("\n---------------------------------\n\n")

	for i in hits:
		wfile.write("cve-"+i+"\n\n")
		wfile.write(list_rules[i])
		wfile.write("\n---------------------------------\n\n")

	wfile.close()
'''
loc cac rule
'''
def filter_rules():
	count = 0
	list_string = ["RCE", "Remote", "remote", "network", "unauthenticate", "Unauthenticate", "Network"]
	black_list_cve = [
						#["2015-1398", "2016-2208", "2016-2345", "2016-3088", "2016-6367", "2016-6563", "2016-6662",
						#"2016-3087", "2016-8523", "2017-1000353", "2017-11885", "2016-6415", "2017-12635",
						#"2017-12636", "2017-2491", "2017-2741", "2017-3066" ,"2017-8045", "2017-9791"
						"2015-1398", "2016-2208", "2016-2345", "2016-3088", "2016-6367", "2016-6415",
						"2016-6563", "2016-6662", "2016-8523", "2017-1000353", "2017-2491", "2017-2741",
						"2017-8045",
						"2018-1000006", "2018-1000049" ,"2018-1000094", "2018-1000207", "2018-1146", "2018-12520"
						,"2018-2380", "2018-1146", "2018-12520", "2018-2380", "2018-3813", "2018-5955"
						,"2018-7520"]
	wfile = open("E:/code/list_rules_filter", 'w+')
	for i in list_cve:
		if i in black_list_cve:
			continue
		for x in list_string:
			if x in list_rules[i]:
				count += 1
				wfile.write("cve-"+i+"\n\n")
				wfile.write(list_rules[i])
				wfile.write("\n---------------------------------\n\n")
				break
	wfile.close()
	print "\n-------------------------------"
	print "rules filter = " + str(count)		
	print "-------------------------------"

if __name__ == "__main__":

	get_rule()
	#search_rule_in_excel()
	#filter_rules()
	

	#------------------------------------------------------------
	#total rules
	'''
	wfile = open("E:/code/list_rules", 'w+')
	for i in list_cve:
		wfile.write("cve-"+i+"\n\n")
		wfile.write(list_rules[i])
		wfile.write("\n---------------------------------\n\n")
	wfile.close()
	'''

	#------------------------------------------------------------
	#temp
	

	

 