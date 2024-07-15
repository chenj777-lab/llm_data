import math
import sys
import datetime

def ymd_to_int(date):
    res = int(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
    return res

def label_degree(infile,part,threshold,outfile):
    threshold = int(threshold)
    parts = part.strip().split(',')
    parts_int = [int(x.strip()) for x in parts]
    wfile = open(outfile, 'w')
    with open(infile) as f:
        for text in f:
            l = []
            float_val = []
            texts = text.strip().split('\t')
            if float(texts[8]) < 140:
                continue
            for i in texts[10:]:
                float_i = float(i)
                l.append(float_i)
                float_val.append(float_i)
            l.sort(reverse = True)
            length = len(l)
            first_index = math.floor(parts_int[0]*length/10) - 1
            first_front_index = math.floor(parts_int[0]*length/20) - 1
            first = l[first_index]
            first_front = l[first_front_index]
 
            second_index = math.floor(sum(parts_int[:2])*length/10) - 1
            second_front_index = math.floor((2*parts_int[0]+parts_int[1])*length/20) - 1
            second = l[second_index]
            second_front = l[second_front_index]

            third_index = math.floor(sum(parts_int[:3])*length/10)-1
            third_front_index = math.floor((4*sum(parts_int[:2]) + 1*parts_int[2])*length/40) - 1         
            third_middle_index = math.floor((4*sum(parts_int[:2]) + 3*parts_int[2])*length/40) - 1   
            third = l[third_index]
            third_front = l[third_front_index] 
            third_middle = l[third_middle_index]
 								
            forth_index = math.floor(sum(parts_int[:4])*length/10)-1
            forth_front_index = math.floor((2*sum(parts_int[:3]) + parts_int[3])*length/20) - 1                                                                                           
            forth = l[forth_index]
            forth_front = l[forth_front_index]

            fifth_front_index = math.floor((2*sum(parts_int[:4]) + parts_int[4])*length/20) - 1
            fifth_front = l[fifth_front_index]
            
            begin_time = ymd_to_int(texts[2])
            index = begin_time - threshold
            #print(texts[1],length,parts_int,first_front,first,second_front,second,third_front,third_middle,third,forth_front,forth,fifth_front)
            for i in float_val:
                index += threshold
                if i >= first:
                    if i < first_front:
                        continue
                    label = 5
                elif i >= second:
                    if i > second_front:
                        continue
                    label = 4
                elif i >= third:
                    if i > third_front or i < third_middle:
                        continue
                    label = 3
                elif i >= forth:
                    if i > forth_front:
                        continue
                    label = 2
                elif i <= fifth_front:
                    label = 1
                else:
                    continue
                
                if index < begin_time + threshold:
                    continue
                string = texts[1] + '\t' + str(index - threshold) + '\t' + str(index) + '\t' + str(label) 
                #string = texts[1] + '\t' + str(index - threshold) + '\t' + str(index) + '\t' + str(label) + '\t' + str(i)
                wfile.write(string+'\n')
    wfile.close()

                
if __name__ == "__main__":
    label_degree(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

