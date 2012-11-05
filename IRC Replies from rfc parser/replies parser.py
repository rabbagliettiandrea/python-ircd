import re

def file_to_list():
    f = open('C:/file.txt', 'r')
    file_string = f.read()
    f.close()
    file_list = [row.split() for row in file_string.split('\n') if len(row.split())]
    regex = re.compile('[0-9]{3}')

    lista = []
    par = []
    for el in file_list:
        if regex.match(el[0]) != None:
            if len(par):
                lista.append(par)
            par = el
        else:
            par.extend(el)
    lista.append(par)
    
    nuova_lista = []
    for el in lista:
        s = ' '.join(el[2:])
        sub_l = el[:2]
        sub_l.append(s)
        nuova_lista.append(sub_l)
    
    return nuova_lista


__slugify_strip_re = re.compile(r'[^\w\s-]')
__slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(__slugify_strip_re.sub('', value).strip().lower())
    return __slugify_hyphenate_re.sub('_', value)


def build_lambda(stringa):
    regex = re.compile('(<[^>]+>)')
    regex2 = re.compile('("[^\s].*-.*[^\s]")')
    if '-' in stringa:
        if regex2.findall(stringa):
            inizio = stringa.find(regex2.findall(stringa)[0])
            fine = inizio+len(regex2.findall(stringa)[0])
            stringa = stringa[:fine]
        else:
            stringa = stringa[:stringa.index('-')]
    arg_list = regex.findall(stringa)
    split_list = regex.split(stringa)
    for e in split_list:
        if regex.match(e) != None:
            split_list[split_list.index(e)] = '%s'
    messaggio = ''.join(split_list)
    
    arg_string = ''
    for arg in arg_list:
        arg_string += slugify(arg.strip('<>'))
        arg_string += ', '
    arg_string = arg_string.strip(', ')
                      
    return "lambda %s: %s %% (%s)" % (arg_string, messaggio, arg_string)


def build_d():
    regex = re.compile('(-.+)%')
    output = '{\n'
    lista = file_to_list()
    for e in file_to_list():
        lambda_str = build_lambda(e[2])
        if regex.search(lambda_str):
            lambda_str = lambda_str.replace(regex.findall(lambda_str)[-1], '')
        output += "\t'%s' : ('%s', %s),\n" % (e[1], e[0], lambda_str)
    output = output.rstrip(',')
    output += '}'    
    
    return output

def write_file(string):
    f = open('C:/newfile.py','w')
    f.write(string)
    f.close()
    
if __name__ == '__main__':
    print build_d()
    write_file(build_d())
    
