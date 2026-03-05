def elog(e: Exception, file="", function=""):
    print("ERROR:", e)
    print(f"File: {file}, {function}")
    print("="*100)


def log(text):
    print(text)
    print("="*100)