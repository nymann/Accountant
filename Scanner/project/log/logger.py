import time


def logger_rest(action, http_code, http_url):
    log_to_file("{0}\t{1} {2}\t{3}\n".format(action, http_code, http_url, time.strftime("%Y.%m.%d-%H:%M:%S")))


def logger_error(user_id, beverage_id):
    log_to_file("{0}\t{1}{2}\t{3}{4}\t{5}\n".format('An error occurred', 'User ID: ', user_id, 'Beverage ID: ',
                                                    beverage_id, time.strftime("%Y.%m.%d-%H:%M:%S")))


def log_to_file(log_msg):
    filename = time.strftime("%Y_%m.log")
    file = open(filename, 'a')

    print(log_msg)

    file.write(log_msg)
    file.close()
