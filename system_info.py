import csv

def system_info():
    read_csv('../SystemInfo.csv', True)

    return 'Hello world'

def read_csv(file_path, header=False):
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file) 

        for r in reader:
            print(r)
            # if (r[0] == '금융SW연구소')
            #     rtn_data = '{}\t{}'.format(r[0], r[1])
            #     pass


        # rtn_data = ['{}\t{}'.format(r[0], r[1]) for r in reader]
        
        # if(header):
        #     rtn_data.pop(0) 
            
    file.close()
    
    print(rtn_data)
    return rtn_data

    
 
if __name__ == '__main__':
    system_info();