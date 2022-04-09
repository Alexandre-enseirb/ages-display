# ages-display

This repository was created to share the code of a small Python script that uses the request library to make requests to the agify.io library.

### Link to the library: ![agify.io](https://agify.io/)

### How to use

To run the script, run the `main.py` file with the following command:

```Bash
$python main.py
```

You can also use arguments to modify the behaviour of the script. By default, it will request for names from any country, within the `names_reduced.txt` file.

### Changing the names file

Running

```Bash
$python main.py -f <filename>
```

or

```Bash
$python main.py --filename=file
```

allows you to change the file used

### Requesting for a particular country

Running

```Bash
$python main.py -c <country>
```

or

```Bash
$python main.py --country=country
```

allows you to change the country requested. Note that you have to tell the country ISO 3166-1 alpha-2 code. A list of the available codes can be found ![here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements) or in the file `myutils.py`.


