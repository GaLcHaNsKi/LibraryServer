def elog(e: Exception, file="", line=0):
    print("ERROR: "+str(e))
    print(f"File: {file}, line>={line}")
    print("="*100)

def log(text):
    print(text)
    print("="*100)