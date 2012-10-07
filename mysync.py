#!/usr/bin/python

import ConfigParser,os,pickle,socket,sys
from os import path,stat,system,environ

confTemplate=r"""
###########################
# # 1: Location Aliases # #
###########################
# Define aliases and the strings against which command line arguments will be matched here as
# [alias] = [character pool]
# For example:
# bob = bobpchome
# This allows clumsy, fat-fingered typing of locations (i.e. remote servers) as shorthand. in
# the above example, the alias "bob" can then be used to identify other information, such as 
# the location, base path to data, etc., but 'bob', 'pc', 'home' (etc) can be used to match it;
# anything entered as the location, if it's a substring of the character pool, will suffice
# to identify it.
[location_aliases]

###########################
# # 2: Category Aliases # #
###########################
# Define aliases and strings against which command line arguments will be matched, similar to the
# location aliases. These will be of the same format, but will be used for referencing locations, i.e.
# local and remote paths to synchronize. Example:
# aud = musicaudioAudioMusic,IGNORECASE
[category_aliases]

#####################
# # 3: Base Paths # #
#####################
# For each data category and location, enter its path  as follows: 
# FOR LOCATIONS: use
# alias = path
# for the path, use the path to which all category base paths will be relative, without a trailing
# slash; for example, if one is using a backup hard drive of category alias "bhd" mounted at
# /media/BackupHDD, one could write:
# bhd = /media/BackupHDD
# and for an SSH backup server with alias "sbs" and backup files stored in ~/personal/backup/, write:
# sbs = username@remotehost:~/personal/backup
# FOR CATEGORIES: use 
# alias = localias1:path1/
#         localias2:path2/
#         etc.
# (include trailing slashes)
# For example, if you have a category with alias "mus", for Music, and on the backup hard drive it
# is at /media/BackupHDD/Music, while on the server it is at ~/personal/backup/media/Audio, the
# entry would be as follows:
# mus = bhd:/Music/
#       sbs:/media/Audio/
[basepath]

####################################
# # 4: Category-Specific Options # #
####################################
# If you wish to add specific options for categories of data, you can define them here -- i.e., 
# to show progress of how much of a large file has been transferred when synchronizing a video files
# folder with alias "vid":
# vid = -h --progress
[category_options]
"""

# Additional hard-coded configuration:
opts_default = '-av --modify-window=2'
opts = {'simple':['',"Use only the default options."],
        'clean':["--delete-after --ignore-existing --existing",
                 'Delete files in target not in source, and do nothing else.'],
        'copynew':['--ignore-existing',
                   'Skip files that exist already in target, copy new files.'],
        'update':["-u --existing",
                  'Update files that exist in both target and source such that '
                  +'the source copy is newer, but don\'t copy new files from the source.'],
        'fullupdate':['-u',
                      'Update all files on the target, skip files that have been touched '
                      +'more recently on the source, and copy new files.'],
        'verbatim':['--delete-after',
                    'Make the target a 100% carbon copy of the source, using difference in '
                    +'file size or timestamp as the criterium for transferring (WARNING: '
                    +'this will overwrite recent changes on the target and delete files not '
                    +'in the source).'],
        'ccc':['-c --delete-after',
                           'Makes the target a 100% carbon copy of the source, using checksum '
                           +'difference as the criterium for transferring (warning: this will '
                           +'be considerably slower for larger files and larger numbers of files).']}

def matchitem(inputstr,confdict,match_dir=1): # return the key corresponding to a matching value
    for item in confdict.items():
        match = (item[1] in inputstr,inputstr in item[1])[match_dir]
        if match:
            return item[0]
            break
    return None
    
def parseconf():
    """Parse the configuration. If a serialized/compressed "cache" of the config exists, open it
    instead of re-parsing the config (to make it go faster)
    """
    global aliases,categories,catopt,confTemplate,hostnames,locations,paths
    confn = environ['HOME']+'/.mydata/conf'
    if not path.exists(path.dirname(confn)):
        os.mkdir(path.dirname(confn))
        conff = open(confn,'w')
        conff.write(confTemplate)
        conff.close
        print "Please enter configuration details in ~/.mydata/conf"
        exit(1)
    
    conff = open(confn,'r') 

    try:
        refresh =stat(confc).st_mtime < stat(confn).st_mtime
    except OSError:
        system('touch '+confc)
        if not path.exists(confn):
            print 'Could not find configuration file: ~/.mydata/conf'
        system('touch '+confn)
        refresh=True
        
    if refresh:
        aliases = {}
        conf = ConfigParser.ConfigParser()
        conf.readfp(conff);
        localiases = dict(conf.items('location_aliases'))
        cataliases = dict(conf.items('category_aliases'))
        pathraw = dict(conf.items('basepath'))
        catopt = dict(conf.items('category_options'))
        hostnames = dict(conf.items('hostnames'))
        aliases.update(localiases)
        aliases.update(cataliases)
        locations = localiases.keys()
        categories = cataliases.keys()
        paths = {}
        for alias in pathraw.keys():
            if alias in categories:
                paths[alias] = dict([item.split(':') for item in pathraw[alias].split('\n')])
            else:
                paths[alias] = pathraw[alias]
        confsav = open(confc,'wb')
        savlist = [aliases,categories,catopt,hostnames,locations,paths]
        pickle.dump(savlist,confsav,pickle.HIGHEST_PROTOCOL)
    else:
        confc = open(confc,'r')
        conf = pickle.load(confc)
        aliases = conf[0]
        categories = conf[1]
        catopt = conf[2]
        hostnames = conf[3]
        locations = conf[4]
        paths = conf[5]
        confc.close()
            
def main():
    # Step 1: initialize
    args = sys.argv
    parseconf()
    cmd = 'rsync ' + opts_default
    if len(args) > 5: # add extra command line arguments
        for i in range(5,len(args)):
            cmd += ' ' + args[i]
    elif len(args) < 5:
        print 'Insufficient number of arguments.'
        sys.exit(0)

    # Step 2: orientation
    localhost = matchitem(socket.gethostname(),hostnames,match_dir=0)
    category = matchitem(args[1],aliases)
    location = matchitem(args[2],aliases)
    pull = 'pul' in args[3]
    action = matchitem(args[4],dict([[key,key] for key in opts.keys()]))
    

    # Step 3: compose the rsync command
    if not location in locations or not category in categories:
        print 'Did not find a match for location or category. Check the configuration and try again;\n'
        sys.exit(1)
    localpath = paths[localhost].replace(hostnames[localhost]+':','')+paths[category][localhost]
    remotepath = paths[location]+paths[category][location]
    cmd += ' '+opts[action][0] # Command line options based on type of transfer
    cmd += ' '+(localpath + ' ' + remotepath,remotepath+' '+localpath)[pull]

    # Step 4: execute
    try:
        raw_input('Command: "%s"\n%s\nProceed? (hit enter if ready)'%(cmd,opts[action][1]))
        system(cmd)
        print 'Done.'
    except KeyboardInterrupt:
        print '\nCancelled.'
    sys.exit(0)
    
if __name__ == '__main__':
	main()
