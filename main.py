import sys
import requests
import matplotlib.pyplot as plt
from myutils import *



def display_help():
    """
    Displays the help

    ARGS:
        None

    Returns:
        None
    """
    print(help_string)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def args_applier(args, kwargs, countries = countries):
    """
    Applies the arguments given in the command line.
    Checks for any duplicate argument, which are not allowed

    ARGS:
        - args: a dictionary of arguments with "-x" as a key, where x is a
        letter, and the argument value as a value. (e.g. {"-f": "foo.txt"})
        - kwargs: a dictionary of arguments with a string as a key, and its
        value as a value (e.g. {"filename": "foo.txt"})
        - countries: the list of valid country strings. Defaults to the
        countries list in utils.py

    Returns:
        - filename: the final string for our names file (defaults to "names.txt")
        - country: the country that will be used for the request (defaults to None)
    """
    # default values
    filename="names_reduced.txt"
    country=None

    # we will parse the arguments using ttheir keys
    args_keys = args.keys()
    kwargs_keys = kwargs.keys()

    # first, we check if the user needs help
    if "-h" in args_keys:
        display_help()
        sys.exit(1) # if help is displayed, exit

    # then, we check for the filename flag
    # checking for double argument
    if "-f" in args_keys and "filename" in kwargs_keys:
        raise DuplicateArgumentError("Duplicate argument found: filename. Exiting.")

    else:
        # no duplicate
        if "-f" in args_keys:
            if args["-f"] == None:
                raise IllegalArgumentError("Error. -f argument must be followed with a name")

            filename = args["-f"]
        elif "filename" in kwargs_keys:
            filename = kwargs["filename"]

    # finally, we check for the country flag
    # checking for double argument
    if "-c" in args_keys and "country" in kwargs_keys:
        raise DuplicateArgumentError("Duplicate argument found: country. Exiting.")
        sys.exit(2)
    else:
        # no duplicate
        # if the country was given with -c <country>
        if "-c" in args_keys and args["-c"] in countries:
            country = args["-c"]
        # if the country was given with --country=country
        elif "country" in kwargs_keys and kwargs["country"] in countries:
            country = kwargs["country"]
        # if "-c" was given without a country
        elif "-c" in args_keys and args["-c"] == None:
            if args["-f"] == None:
                raise IllegalArgumentError("Error. -c argument must be followed with a name")

    return filename, country

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def args_parser(argv):
    """
    Parses the list of command line arguments to find all the allowed arguments.

    ARGS:
        - argv: the list of command line arguments

    Returns:
        - args: A dictionary of the arguments given with one dash, and their
        respective value.
        - kwargs: A dictionary of the arguments given with two dashes, and
        their respective value.
    """

    # Preparing the variables
    argc=len(argv)
    args={}
    kwargs={}
    ptr=1 # pointer on the current parsed argument

    # allowed args with one and two dashes
    args_list = ["-h", "-f", "-c"]
    kwargs_list = ["--filename","--country"]

    # if we had "-c" for instance, we don't want the country to be classified as an
    # invalid argument
    pass_next=False

    for elem in argv[1:]: # script name is skipped

        if "=" in elem and "--" in elem: # checking for --key=value args

            [str1,str2] = elem.split("=")

            if not str1 in kwargs_list:  # if InvalidArgument is found
                raise IllegalArgumentError("An error occured while parsing argument {}: Invalid argument".format(elem))
                sys.exit(2)

            # if the arg is valid, it is stored using the keyword as a key
            kwargs[str1[2:]] = str2
        else:                            # checking for -arg <value>

            if elem in args_list and ptr+1<argc: # if we have a value following the arg
                args[elem] = argv[ptr+1]
                pass_next=True
            elif elem in args_list: # if not, we store it anyway, might be a "-h"
                args[elem] = None
            elif pass_next:         # if we have to pass this argument, we won't pass the next one
                pass_next=False
            else:                   # invalid argument error
                raise IllegalArgumentError("An error occured while parsing argument {}: Invalid argument".format(elem))
                sys.exit(2)
        ptr+=1

    return args, kwargs

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def make_request(names, country=None):
    """
    Turns the list of names into a list of requests.
    As agify.io limits batch requests to 10 replies at a time,
    we will have to create batches of 10 names.

    ARGS:
        - names: A list of the names we have to request from the API
        - country: An additional argument for the requests

    Returns:
        - ret: A list of API responses
    """

    ret = []

    for loop in range(len(names)):

        if loop%10 == 0:   # enter every ten names (and at start)
            if loop>0:     # code to execute only after first loop

                if country is not None: # if a country has been specified
                    req += "&country_id={}".format(country) # add it to the request

                # make the request
                res = requests.get(req)
                if res.status_code!=200:
                    raise Exception("API request failed.")
                ret.append(res.json()) # store the request as a readable dictionary

            # prepare the next request
            req = "https://api.agify.io/?name[]={}".format(names[loop])
        else:
            # add a name to the request
            req+="&name[]={}".format(names[loop])


    res = requests.get(req)
    if res.status_code!=200:
        raise Exception("API request failed.")
    ret.append(res.json())

    return ret


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def sort_results(result):
    """
    Transforms the list of dictionaries we created from the API responses
    into two dictionaries. Both will use the names as keys. One will store
    the 'age' field as its values, and the other will store the 'count' field.

    ARGS:
        - result: list of dictionaries created from agify.io's responses

    Returns:
        - age_per_name: a dictionary which stores the names as keys and the ages
        as values
        - count_per_name: a dictionary which stores the names as keys and the count
        as values
    """
    age_per_name   = {}
    count_per_name = {}

    for res in result:
        # First we need to check if res is a list or a dictionary.
        # If we only made one request, it will be a dictionary.
        # if we made two or more requests, it will be a list of dictionaries
        if type(res) is list:

            # res is a dictionary, and we need to iterate through it
            for elem in res:
                if elem['age'] is not None:
                    age_per_name[elem['name']]   = elem['age']
                    count_per_name[elem['name']] = elem['count']

        # res is already an entry of the dictionary
        else:
            if res['age'] is not None:
                age_per_name[res['name']]   = res['age']
                count_per_name[res['name']] = res['count']

    return age_per_name, count_per_name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def plot(age_per_name, count_per_name, filename):
    """
    Uses the results from the api request to plot together the mean age and
    the number of people having the same name

    ARGS:
        age_per_name: a dictionary with the names as keys, and the age as
        values

        count_per_name: a dictionary with the names as keys and the count
        as values

        filename: the string that stores the filename, for title purposes

    Returns:
        None
    """

    # Plotted values
    names = list(age_per_name.keys())
    ages = list(age_per_name.values())
    count = list(count_per_name.values())

    fig, host = plt.subplots(figsize=(8,5))

    fig.suptitle("Results of the API with the file {}".format(filename))

    # axis duplication
    ax = host.twinx()

    # plotting the mean age against the names
    color="tab:blue"
    host.set_xlabel("Names")
    host.set_ylabel("Mean age")
    plt1, = host.plot(names,ages,color=color, label="Mean age")
    host.tick_params(axis='y',labelcolor=color) # to make the y axis colored


    # plotting the count against the names
    color="tab:green"
    ax.set_ylabel("Count")
    plt2, = ax.plot(names,count,color=color, label="Name count")
    ax.tick_params(axis='y',labelcolor=color) # to make the y axis colored

    # making the names rotate on the x_axis for readability
    host.xaxis.set_ticks(names)
    host.set_xticklabels(names, rotation=60)

    # creating the legend
    host.legend([plt1,plt2],["Age","Count"])

    # moving the second plot's y axis to the right
    ax.yaxis.set_ticks_position('right')

    plt.show()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def read_names(file, alphabet=alphabet):
    """
    Reads the file line by line, and returns all the names in it, stripped
    from their '\n'.
    Note that if a line does not start with an alphabetic letter

    ARGS:
        - file: the open txt file from which the names will be read
        - alphabet: a list of letters that describes all authorized first letters.
        Any other first letter will make this program consider the line as a
        commentary and not read it.

    Returns:
        - names: a list of names, stripped from their '\n'
    """

    lines = file.readlines()
    names=[]

    for line in lines:
        if line[0].upper() in alphabet:
            names.append(line.strip())

    return names

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main(argv):
    """
    Main function of the program

    ARGS:
        argv: command line's arguments

    Return:
        None
    """

    # reading the command line's arguments
    args, kwargs = args_parser(argv)
    filename, country = args_applier(args, kwargs)

    # checking if the file does exist
    try:
        f = open(filename,'r')
    except(FileNotFoundError):
        raise Exception("Specified file not found: {}".format(filename))

    # reading the file and preparing the request
    names = read_names(f)
    result = make_request(names, country)

    # turn the API's response in two dictionaries
    age_per_name, count_per_name = sort_results(result)

    # plot everything
    plot(age_per_name, count_per_name, filename)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
        main(sys.argv)
