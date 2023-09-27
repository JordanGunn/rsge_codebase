import re
import os
# import glob

def run_from_gui(fGlob, outputDir, recurse):
    #fList = [os.path.basename(f) for f in glob.glob(f'{inputDir}\\**\*',recursive=True)
                   #if f[-4:] in {'.tif', '.jpg', '.jpeg', '.sid'}]
    '''
    extensions= ("*.tif", "*.tiff", "*.jpg", "*.jpeg", "*.sid")
    fGlob = []
    for extension in extensions:
        fGlob.extend(glob.glob(inputDir+"/"+extension))
    '''
    fList = []
    pList = []
    for f in fGlob:
        fList.append(os.path.split(f)[1])
        pList.append(os.path.split(f)[0])

    run_test(outputDir, fList, pList, recurse)

def run_test(outputDir, fList, pList, recurse):
    orthoRegex = r'^bc_\d{3}[a-z]\d{3}(_\d_\d_\d_|_)x(c|ci|b|fc)\d{3}mm_(bcalb|utm08|utm8|utm09|utm9|utm10|utm11)_2\d{3}(.tif|.tiff|.jpg|.jpeg|.sid)$'
    rasterRegex = r'^bc_\d{3}[a-z]\d{3}(_\d_\d_\d_|_)x(li|r|rgb)([1-9]m|\\d[1-9]m)_(bcalb|utm08|utm8|utm09|utm9|utm10|utm11)_2\d{3}(|_dsm).(tif|tiff|asc)$'
    rawRegex = r'^(\d[1-9]|[1-9]\d)bcd([1-9]\d|\d[1-9])([1-9]\d{2}|\d[1-9]\d|\d{2}[1-9])_([1-9]\d{2}|\d[1-9]\d|\d{2}[1-9])_([1-9]\d|\d[1-9])_([1-9]\d|[1-9])bit_(rgb|rgbir).(tif|tiff|sid|jpg|jpeg)$'
    badFilenames = []

    for x in range(len(fList)):
        
        if (re.match(orthoRegex, str(fList[x])) == None) and (re.match(rasterRegex, str(fList[x])) == None) and (re.match(rawRegex, str(fList[x])) == None):
            if recurse == 1:
                badFilenames.append(f"{pList[x]}/{fList[x]}")
            else:
                badFilenames.append(fList[x])

    with open(f'{outputDir}\\filename_check.txt', mode='w+') as out:
        print(f"Bad filenames: {len(badFilenames)} of {len(fList)}", file=out)
        print(f"\nList of bad filenames:", file=out)
        for fn in badFilenames:
            print(fn, file=out)
    
    if len(badFilenames) < 1:
        print("No bad filenames found", flush=True)

#if __name__ == '__main__':
    #run_from_gui()