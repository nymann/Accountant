import time


def logger_rest(action, http_code, http_url):
    filename = time.strftime("%Y_%m.log")
    file = open(filename, 'a')
    file_text = "{0}\t{1} {2}\t{3}\n".format(action, http_code, http_url, time.strftime("%Y.%m.%d-%H:%M:%S"))
    print(file_text)
    file.write(file_text)
    file.close()

