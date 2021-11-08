import ndjson
import sys
import getopt
from os.path import exists, dirname
from pathlib import Path
import dateutil.parser as parser

def getMethod(lines) -> str:
    if len(lines) == 1:
        method = 'Connect'
    else:
        lines[1] = lines[1][:-1]
        method = " ".join(lines)

    return method.title()

def getIP(line: str) -> str:
    if line[-1] == ',':
        line = line[8:-2]
    else:
        line = line[8:-1]

    return line

def getTime(line: str) -> str:
    return parser.parse(line).isoformat()

def getOptions(argv):
    inputfile = '/var/log/vsftpd.log'
    outputfile = '/var/log/parsed-vsftpd.ndjson'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["log=","json="])
    except getopt.GetoptError as e:
        print(e.msg)
        print('Usage: test.py -i <ftplogfile> -o <jsonfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: test.py -i <ftplogfile> -o <jsonfile>')
            sys.exit()
        elif opt in ("-i", "--log"):
            inputfile = arg
        elif opt in ("-o", "--json"):
            outputfile = arg

    return inputfile, outputfile

def main(argv):
    inputLog, outputNdjson = getOptions(argv)

    if exists("./counter.txt"):
        with open("./counter.txt", 'r') as counter_file:
            counter = int(counter_file.read())
    else:
        counter = 0            

    if exists(outputNdjson):
        with open(outputNdjson, 'r') as logNdjson:
            ndjsonObj = ndjson.load(logNdjson)
    else:
        Path(dirname(outputNdjson)).mkdir(parents=True, exist_ok=True)
        ndjsonObj = []

    with open(inputLog, 'r') as log:
        for _ in range(counter):
            next(log)
        for record in log:
            params = record.split()

            ip = getIP(list(filter(lambda x: '::ffff:' in x, params[7:]))[0])

            time = getTime(" ".join(params[:5]))

            if 'CONNECT:' == params[7]:
                method = getMethod(params[7:8])
            else:
                method = getMethod(params[8:10])

            entry = {
                "IP" : ip,
                "Time" : time,
                "Method" : method
            }
            if entry['Method']=="Ok Download":
                entry['File'] = params[12][1:-2]
            counter = counter + 1
            ndjsonObj.append(entry)

    with open(outputNdjson, 'w') as logNdjson:
        ndjson.dump(ndjsonObj, logNdjson)
    with open("./counter.txt", 'w') as counter_file:
        counter_file.write(str(counter))


if __name__ == '__main__':
    main(sys.argv[1:])