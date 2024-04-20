import os
from pprint import pprint
import datetime
import re

from functions import get_bin_folder, \
    get_template_folder, \
    get_data_folder, \
    get_default_input_folder,\
    get_default_output_folder,\
    get_env_var
from able import EnvString, \
                 Inputable, \
                 StringReader, \
                 StringWriter, \
                 UpdaterString, \
                 TemplateString,\
                 EnvVarString, \
                 Stack,\
                 DataString,\
                 NameValuePairs,\
                 CloneRepo, \
                 StringWriter,\
                 UpserterString,\
                 RuntimeLogger,\
                 Recorder
# make bin/md2.env
#
def get_environment_filename():
    # env is stored in the bin folder bin/md2
    return '{}/md2.env'.format(get_bin_folder())

def get_environment_template_filename():
    return '{}/md2.env.tmpl'.format(get_template_folder())

def get_template_name_value_pairs():
    nv_list = NameValuePairs(multi_line_string=EnvVarString())
    nv_list = [{'name': '<<{}>>'.format(itm['name']), 'value': itm['value']} for itm in nv_list]
    return nv_list

def get_branch_folder():
    nv_list = get_template_name_value_pairs()
    return TemplateString('{}/Development/<<WS_ORGANIZATION>>/<<WS_WORKSPACE>>/<<WS_PROJECT>>/<<GH_BRANCH>>'.format(os.environ['HOME']), nv_list=nv_list)

def get_env_template():
    return '''
    WS_ORGANIZATION=<<WS_ORGANIZATION>>
    WS_WORKSPACE=<<WS_WORKSPACE>>
    '''.replace('    ', '')

def isStringNone(str_object):

    rc = str_object

    if str_object == None:
        rc = None
    elif str_object == 'None':
        rc = None

    return rc

class Memorize():
    def __init__(self, env_var_string, recorder=None):
        #print('1 memorize',recorder)
        contents = env_var_string
        for ln in contents.split('\n'):
            #print('1 memorize')

            # Define the regular expression pattern  r'^([A-Z][A-Z0-9_]+)=(.+)'
            pattern = r'^([A-Z][A-Z0-9_]+)=(.+)'

            # Use re.match() to match the entire input string
            #print('2 memorize', recorder)

            match = re.match(pattern, ln)
            if match:

                ln = ln.split('=')
                ##* loads env variables into msettings={'dup': False, 'hard_fail': True}emory
                #if recorder: recorder.add('memorize',recorder)
                os.environ[ln[0]] = ln[1]
                #print('memorize', ln[0])
            #print('3 memorize',recorder)


def initialize(recording):
    # create mdv2.env from template
    env_file_content_string=None
    env_name = get_environment_filename().split('/')[-1]

    if not os.path.isfile(get_environment_filename()):
        # init from template
        recording.add('init({})'.format(env_name))
        env_file_content_string = isStringNone(StringReader(get_environment_template_filename()))
        StringWriter(get_environment_filename(),env_file_content_string, recording=recording)

    return env_file_content_string

def load(recorder):
    # load environment from file
    #print('2 load ',DiagramString(recorder))

    env_name = get_environment_filename().split('/')[-1]

    recorder.add('load ({})'.format(env_name))

    #print('3 load ',DiagramString(recorder))
    #print('get_environment_filename',get_environment_filename())
    #if recorder: print(str(get_environment_filename()).split('/'))

    #if recorder: print('read ({})'.format(str(get_environment_filename()).split('/')[-1]))

    env_file_content_string = StringReader(get_environment_filename(),recorder=recorder)

    #print('4 load',DiagramString(recorder))
    # load environment into memory

    Memorize(env_file_content_string, recorder=recorder)
    #print('5 load',recorder)

    return env_file_content_string


def confirm(env_file_content_string, recording):
    # print('env_file_content_string',env_file_content_string.replace('\n','|'))
    recording.add('confirm')
    os.environ['WS_ORGANIZATION'] = Inputable().get_input('WS_ORGANIZATION',
                                                          get_env_var('WS_ORGANIZATION', 'test-org'),
                                                          hardstop=True)
    recording.add('confirm')
    os.environ['WS_WORKSPACE'] = Inputable().get_input('WS_WORKSPACE',
                                                       get_env_var('WS_WORKSPACE', 'test-ws'),
                                                       hardstop=True)
    recording.add('confirm')
    os.environ['WS_PROJECT'] = Inputable().get_input('WS_PROJECT',
                                                     get_env_var('WS_PROJECT', 'test-prj'),
                                                     hardstop=True)
    recording.add('confirm')
    os.environ['GH_TRUNK'] = Inputable().get_input('GH_TRUNK',
                                                   get_env_var('GH_TRUNK', 'main'),
                                                   hardstop=True)
    recording.add('confirm')
    os.environ['GH_BRANCH'] = Inputable().get_input('GH_BRANCH',
                                                    get_env_var('GH_BRANCH', 'first'),
                                                    hardstop=True)
    recording.add('confirm')
    os.environ['GH_REPO'] = Inputable().get_input('GH_REPO',
                                                  get_env_var('GH_REPO', 'py_test'),
                                                  hardstop=True)
    recording.add('confirm')
    os.environ['GH_USER'] = Inputable().get_input('GH_USER',
                                                  get_env_var('GH_USER', 'x'),
                                                  hardstop=True)
    recording.add('confirm')
    os.environ['GH_MESSAGE'] = Inputable().get_input('GH_MESSAGE',
                                                     get_env_var('GH_MESSAGE', 'init'),
                                                     hardstop=True)
    recording.add('confirm')
    os.environ['GH_TOKEN'] = Inputable().get_input('GH_TOKEN',
                                                   get_env_var('GH_TOKEN', 'x'),
                                                   hardstop=True)
    recording.add('confirm')
    env_file_content_string = UpserterString(env_file_content_string,
                                             settings={'dup': True, 'hard_fail': True}) \
                                .upsert(EnvVarString())
    return env_file_content_string

def hasDups(content_list):
    ##__Does content have duplicate non blank lines__
    if isinstance(content_list, str):
        content_list = content_list.split('\n')
    # remove all blank lines
    content_list = [ln for ln in content_list if len(ln.strip()) != 0]
    # a set by definition has no duplicates
    if len(content_list) != len(set(content_list)):
        return True
    return False

def showDuplicates(content_list):
    if isinstance(content_list, str):
        content_list = content_list.split('\n')
    print('Duplicates')
    l1 = []
    for item in content_list:
        if item not in l1:
            l1.append(item)
        else:
            print('* dup: ',item)

class LLTitle(str):
    def __new__(cls, title):
        contents = '# Title: {} \n## source: {} \n## by: {}'.format(title,str(__file__).split('/')[-1], os.environ['USER'])
        instance = super().__new__(cls, contents)
        return instance

class LLBranch(str):
    def __new__(cls, target=None):
        if not target:
            target = get_branch_folder()
        nv_list = get_template_name_value_pairs()
        contents = '* branch: {}'.format(TemplateString(target, nv_list))
        instance = super().__new__(cls, contents)
        return instance

class LLTime(str):
    def __new__(cls, msg):
        contents = '{}: {}'.format(datetime.datetime.now(),msg)
        instance = super().__new__(cls, contents)
        return instance

class LLStar(str):
    def __new__(cls, msg):
        contents = '* {}'.format(msg)
        instance = super().__new__(cls, contents)
        return instance

class LLEnv(str):
    def __new__(cls, msg=None):
        contents = msg
        if not msg:
            nv_list = NameValuePairs(multi_line_string=EnvVarString())
            nv_list = ['* {}: {}'.format(nv['name'],nv['value']) for nv in nv_list]
            contents = '\n'.join(nv_list)

        instance = super().__new__(cls, contents)
        return instance


class DiagramString(str):

    def __new__(cls, recording=None):
        contents = recording
        if not recording:
            contents=''

        contents = ''
        if 'step_list' not in recording:
            recording['step_list'] = []

        for s in recording['step_list']:
            if s['count'] == 1:
                contents += ' {}'.format(s['msg'])
            else:
                contents += ' {} ({})'.format(s['msg'], s['count'])

        instance = super().__new__(cls, contents)
        return instance

def main():
    log = RuntimeLogger()
    recorder= Recorder()

    ## Setup Environment
    ##* Initialize Environment
    #recorder.add('Clone')
    #print('log',os.environ)
    #log.write(LLTitle('Clone'))
    # default values ... d_
    d_GH_TRUNK='main'

    ##* Initialize environment

    env_file_content_string = initialize(recorder)

    ##* Load environment variables into memory

    env_file_content_string = load(recorder)

    ##* Confirm environment variables

    env_file_content_string = confirm(env_file_content_string, recorder)

    # initiate
    # load
    # confirm
    # memorize

    log.write('__Project__')
    log.write(LLBranch())
    #log.write('__Environment__')
    # log.write(LLEnv())
    # HOME/ORG/WS/PROJECT/BRANCH/REPO

    ##* Save environment variables to environment file on request
    ##* Collect env variables from memory

    ## Save first version of env file in bin folder

    # update existing env file
    if os.path.isfile(get_environment_filename()):
        # update "a=b" pattern
        env_file_content_string = UpserterString(env_file_content_string, settings={'dup':True, 'hard_fail': True},recorder=recorder)\
                                    .upsert(EnvVarString())

    nv_list = NameValuePairs(multi_line_string=EnvVarString())

    # wrap nv_list name in <<>>
    nv_list = [{'name': '<<{}>>'.format(itm['name']), 'value': itm['value']} for itm in nv_list]

    # update any missing template values
    env_file_content_string = TemplateString(env_file_content_string, nv_list)
    branch_folder = get_branch_folder()
    # branch_folder = TemplateString('{}/Development/<<WS_ORGANIZATION>>/<<WS_WORKSPACE>>/<<WS_PROJECT>>/<<GH_BRANCH>>'.format(os.environ['HOME']), nv_list=nv_list)
    repo_folder = '{}/{}'.format(branch_folder, os.environ['GH_REPO'])
    log.write('__Actions__')
    ## Create the branch folder home/org/ws/prj/branch when not found
    #log.write('* Create Branch folder when not found')
    if not os.path.isdir(branch_folder):
        recorder.add('mkdir (/{})'.format(branch_folder.split('/')[-1]))
        #recorder.add('mkdir')

    os.makedirs( branch_folder, exist_ok=True )

    if not os.path.isdir(branch_folder):
        raise Exception('Branch folder was not created! {}'.format(branch_folder))

    ## Clone Project
    ##* Download Clone when clone doesnt exit

    if not os.path.isdir(repo_folder):
        repo_name = repo_folder.split('/')[-1]
        recorder.add('clone ({})'.format(repo_name))
        #log.write(LLTime('* Clone repo when repo doesnt exist'))
        CloneRepo(repo_folder=repo_folder,  username_gh=os.environ['GH_USER'])
    else:
        repo_name = repo_folder.split('/')[-1]
        recorder.add('cloned ({})'.format(repo_name))

    ##* Save environment to file
    env_file_content_string = StringReader(get_environment_filename())

    StringWriter(get_environment_filename(), env_file_content_string)
    recorder.add('save({})'.format(get_environment_filename().split('/')[-1]))
    #log.write('* Save environment {}'.format(get_environment_filename()))
    log.write(DiagramString(recorder))
    log.write('\n')
    print(DiagramString(recorder))

if __name__ == "__main__":
    # execute as docker
    main()
