import re

re_opt = re.compile(r'([\(]*\w+):(["\'\w\s]*[\)]*)')
re_opt_str = re.compile(r'[\(]*\w+:["\'\w\s]*[\)]*')


def nlq_parse(query,feature_names):
        
    
    query = query.strip()
    
    #process options
    options = {}
    opts = re_opt_str.findall(query)
        
    for k,v in re_opt.findall(query):
        options[k.replace('(','')] = v.replace(')','').replace('"','')
    
    #process query command
    cmd = query
    
    #remove the options from query
    for opt_str in opts:
        cmd = cmd.replace(opt_str,'')
    #split by correlation sepator     
    if ' par ' in cmd.lower():
        f_list = cmd.strip().lower().split(' par ')
    elif ',' in cmd.lower():
        f_list = cmd.strip().lower().split(',')
    elif '^' in cmd.lower():
        f_list = cmd.strip().lower().split('^')
    else:
        f_list = cmd.strip().lower().split(' by ')
    f_list = [f.strip() for f in f_list]
    
    #extract feature names
    feature_list = []
    for f in f_list:
        for feature_name in feature_names:
            if feature_name.upper() == f.upper():
                feature_list.append(feature_name)
    
    feature_y = feature_list[0] if len(feature_list)>0 else None
    feature_x = feature_list[1] if len(feature_list)>1 else None
    
    return feature_y, feature_x,options
