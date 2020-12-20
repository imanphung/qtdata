import sys, os, time
import datetime
from subprocess import Popen, PIPE, list2cmdline
import argparse
import subprocess

from d2o_common.legacy_lib.utils import logger as log
from d2o_common.legacy_lib.utils.systools import makedirs
from d2o_common.legacy_lib import database_api as db_api

# from d2o_common.legacy_lib.utils.handlers import ExceptionHandler

LOG_VERBOSITY = "debug"
PRINT_VERBOSITY = "debug"

CUR_USER = os.path.dirname(os.path.realpath(__file__)).split('/home/')[1].split('/')[0]
# CONFIG_DIR = '/home/{0}/.chronos/qt-data/cleaned_json_conf/'.format(CUR_USER)
LOGDIR = '/home/{0}/.chronos/qt-data/run_all_for_dept/'.format(CUR_USER)


def get_list_hotel(client):
    try:
        d = db_api.get_hotels_in_database(client)['Id'].values
        return d
    except:
        return []


def sorted_info(l_info):
    d = {}
    for client, hotel_id in l_info:
        deps = get_list_dep(client, hotel_id)
        d[(client, hotel_id)] = len(deps)
        print(client, hotel_id, len(deps))

    l = sorted(d, key=d.get)  # increasing
    for client, hotel_id in l:
        print(client, hotel_id, d[(client, hotel_id)])
    return l


def get_info_to_run(list_client):
    info = []
    for client in list_client:
        print(client)
        list_hotel = get_list_hotel(client)
        print('list hotel: ', len(list_hotel))
        for hotel in list_hotel:
            info.append((client, hotel))

    return info


def get_list_dep(client, hotel, remove_hotel_id=True):
    try:
        df = db_api.get_depts_in_hotel(client, hotel_id)
#        df = df[df['Revenue'] == True]
        if remove_hotel_id:
            df = df[df['H_Id'] != int(hotel)]
        deps = df['H_Id'].values
        return deps
    except:
        return []

def get_list_dep_season(client, hotel, remove_hotel_id=True):
    try:
        df = db_api.get_depts_in_hotel(client, hotel_id)
        df = df[(df['Revenue'] == True) | df['Labor'] == True | (df['FoodCost'] == True)]
        if remove_hotel_id:
            df = df[df['H_Id'] != int(hotel)]
        deps = df['H_Id'].values
        return deps
    except:
        return []    
    

def get_list_dep_labor(client, hotel, remove_hotel_id=True):
    try:
        df = db_api.get_depts_in_hotel(client, hotel_id)
        df = df[df['Labor'] == True]
        if remove_hotel_id:
            df = df[df['H_Id'] != int(hotel)]
        deps = df['H_Id'].values
        return deps
    except:
        return []

def get_list_dep_rev(client, hotel, remove_hotel_id=True):
    try:
        df = db_api.get_depts_in_hotel(client, hotel_id)
        df = df[df['Revenue'] == True]
        if remove_hotel_id:
            df = df[df['H_Id'] != int(hotel)]
        deps = df['H_Id'].values
        return deps
    except:
        return []



def cpu_count():
    ''' Returns the number of CPUs in the system
    '''
    num = 1
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass

    return num


def exec_commands(cmds):
    ''' Exec commands in parallel in multiple process
    (as much as we have CPU)
    '''
    if not cmds: return # empty list

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0
    def fail():
        sys.exit(1)

    max_task = cpu_count()

    processes = []
    while True:
        while cmds and len(processes) < max_task:
            task = cmds.pop()
            print(list2cmdline(task))
            p = Popen(task, stdout=PIPE, stderr=PIPE)
            processes.append(p)

        for p in processes:
            if done(p):
                if success(p):
                    print(p.stdout.read())
                    print(p.stderr.read())
                    processes.remove(p)
                else:
                    processes.remove(p)

        if not processes and not cmds:
            break
        else:
            # Quit if currentTime is in working hours and weekday
            currentTime = datetime.datetime.now()
            time.sleep(5)
#            if (currentTime.isoweekday() in [0,1,2,3,4,6]) and currentTime.hour in range(5, 18):
#                log.info("It is in working hours and weekday")
#                break
#            else:

if __name__ == "__main__":
    # ========= INPUT ===============
    parser = argparse.ArgumentParser("Generates drivers and writes result to database",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--length", help="Minimum length for each season", default=-1)
    parser.add_argument("-Y", "--years", help="Number of years of data to include", default=-1)
    parser.add_argument("-N", "--no-write", help="Run, but do not write results to database", action="store_true",
                        default=False)
    parser.add_argument("-A", "--anims", help="Create animations and plots", action="store_true", default=False)
    parser.add_argument("-I", "--inner-window", help="Inner window size", default=14)
    parser.add_argument("-O", "--outer-window", help="Outer window size", default=60)
    parser.add_argument("-X", "--hotel-or-dept", help="ID of database", default='dep')
    parser.add_argument("-G", "--type-labor", help="Labor type of department or hotel", default='t')
    parser.add_argument("-R", "--type-revenue", help="Revenue type of department or hotel", default='t')
    parser.add_argument("-F", "--type-foodcost", help="Foodcost type of department or hotel", default='t')
    parser.add_argument("-C", "--clients", help="Run selected clients Id or Name", default='all')
    parser.add_argument("-S", "--services", help="Run selected services", default='a,s,r,c')
    args = parser.parse_args()
    min_length = args.length
    years_back = args.years
    anims = args.anims
    inner_window = args.inner_window
    outer_window = args.outer_window
    type_dep = args.hotel_or_dept
    no_write = args.no_write
    pickedclient=args.clients.split(',')
    l_type = args.type_labor  ##
    r_type = args.type_revenue  ##
    f_type = args.type_foodcost
    selectedService = args.services.split(',')
    print("selectedService " + str(selectedService))
    # # Create log file
    log.set_print_verbosity(PRINT_VERBOSITY)
    # # log.set_log_verbosity(LOG_VERBOSITY)
    log.enable_colors()
    log.enable_logging()
    makedirs(LOGDIR)
    log.set_logdir(LOGDIR)
    log.set_logname(type_log='runall', time=None)

    # Quit if currentTime is in working hours and weekday
    currentTime = datetime.datetime.now()
#    if (currentTime.isoweekday() in [0,1,2,3,4,6]) and currentTime.hour in range(5, 18):
#        log.info("It is in working hours and weekday")
#        sys.exit()


    # os_path = os.path.dirname(os.path.realpath(__file__)).replace('/revenue_driver_detection','')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modules = {'department_seasons': os.path.join(dir_path, "..", 'department_seasons', 'department_seasons_json_v2.py'),
               'analyzer': os.path.join(dir_path, "..", 'analyzer', 'analyzer_json_v2.py'),
               'cost_driver_detection': '/home/tp7/d2o_service/cost_driver_detection/d2o_resource_driver_v2.py',
               'revenue_driver_detection': os.path.join(dir_path, "..", 'revenue_driver_detection',
                                                        'revenue_driver_detection_json_v2.py')}

#    all_clients = db_api.get_all_client()
#    if('all' not in pickedclient):
#        all_clients=all_clients.loc[(all_clients['Id'].isin(pickedclient))|(all_clients['Name'].isin(pickedclient))]
#    run_clients = all_clients['Id'].values
#    info = get_info_to_run(run_clients)
#    info = sorted_info(info)

    info = list(set([(u'29041DF0-701D-446E-9842-D2769F057A35', 20), \
                    (u'29041DF0-701D-446E-9842-D2769F057A35', 40), \
                    (u'29041DF0-701D-446E-9842-D2769F057A35', 60), \
                    (u'29041DF0-701D-446E-9842-D2769F057A35', 80), \
                    (u'29041DF0-701D-446E-9842-D2769F057A35', 100)
                    ]))

    hotel_commands_season = []
    hotel_commands_revenue = []
    hotel_commands_analyzer = []
    hotel_commands_cost_driver = []
     #
    v_type = 1
    align = 1
    for client, hotel_id in info:
        if "s" in selectedService:
            dep_ids = get_list_dep_season(client, hotel_id, remove_hotel_id=False)  ## +
            print('Hotel {} __ List of season depts: {}'.format(hotel_id, dep_ids))
            for dep in dep_ids:  ## +
                r_type = 't'
                l_type = 'f'
                f_type = 'f'
                season_call_list = [
                    '/home/henry/anaconda2/envs/deven/bin/python', modules['department_seasons'],
    #                    '-l', '%s' % min_length,
                    '-c', '%s' % client,
                    # '-N', '%s' % no_write,
                    '-A', '%s' % anims,
    #                    '-O', '%s' % outer_window,
    #                    '-I', '%s' % inner_window,
                    '-X', '%s' % type_dep,
    #                    '-l', '%s' % min_length,
                    '-Y', '%s' % years_back,
                    '-i', '%s' % dep,   ## -+
                    '-G', '%s' % l_type,
                    '-R', '%s' % r_type,
                    '-F', '%s' % f_type,
                    '-v', '%s' % v_type]
                hotel_commands_season.append(season_call_list)
            # subprocess.call(season_call_list)

        if "r" in selectedService:
            dep_ids = get_list_dep_rev(client, hotel_id, remove_hotel_id=True)  ## +
            print('Hotel {} __ List of revenue depts: {}'.format(hotel_id, dep_ids))
            for dep in dep_ids:                
                revenue_driver_call_list = [
                    '/home/henry/anaconda2/envs/deven/bin/python', modules['revenue_driver_detection'],
                    # '-N', '%s' % no_write,
                    '-Y', '%s' % years_back,
                    '-c', '%s' % client,
                    '-i', '%s' % hotel_id,
                    '-k', '%s' % dep,
                    '-v', '%s' % v_type]  ## +
                hotel_commands_revenue.append(revenue_driver_call_list)
            #subprocess.call(revenue_driver_call_list)

        if "a" in selectedService:
            dep_ids = get_list_dep_rev(client, hotel_id, remove_hotel_id=False)  ## +
            print('Hotel {} __ List of analyzer depts: {}'.format(hotel_id, dep_ids))
            for dep in dep_ids:   
                analyzer_call_list = [
                    '/home/henry/anaconda2/envs/analyzer_env/bin/python', modules['analyzer'],
                    '-c', '%s' % client,
                    '-i', '%s' % hotel_id,
                    '-v', '%s' % v_type,
                    '-k', '%s' % dep]  ## +
                hotel_commands_analyzer.append(analyzer_call_list)
            # subprocess.call(analyzer_call_list)

        if "c" in selectedService:
            dep_ids = get_list_dep_labor(client, hotel_id, remove_hotel_id=True)  ## +
            print('Hotel {} __ List of optimalstaffing depts: {}'.format(hotel_id, dep_ids))
            for dep in dep_ids:  
                cost_driver_detection_call_list = [
                    '/home/henry/anaconda2/envs/deven/bin/python', modules['cost_driver_detection'],
                    # '-N', '%s' % no_write,
                    # '-Y', '%s' % years_back,
                    '-c', '%s' % client,
                    # '--write_log',
                    '-i', '%s' % hotel_id,
                    '-d', '%s' % dep,
                    '-a', '%s' % align,
                    '-v', '%s' % v_type]  ## +
                hotel_commands_cost_driver.append(cost_driver_detection_call_list)
                    # subprocess.call(cost_driver_detection_call_list)


    # print("len of hotel_commands " + str(len(hotel_commands)))
    # import csv

    # with open("/home/henry/rev_test/dep_commands.csv", 'wb') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    #     wr.writerow(hotel_commands_analyzer)

    start_time_revenue = time.time()
    exec_commands(hotel_commands_season)
    print("--- RUN SEASON FOR client %s in %s seconds ---" % ('Thon', time.time() - start_time_revenue))
    start_time_revenue = time.time()
    exec_commands(hotel_commands_revenue)
    print("--- RUN REVENUE FOR client %s in %s seconds ---" % ('Thon', time.time() - start_time_revenue))
    start_time_revenue = time.time()
    exec_commands(hotel_commands_analyzer)
    start_time_revenue = time.time()
    print("--- RUN OS FOR client %s in %s seconds ---" % ('Thon', time.time() - start_time_revenue))
    exec_commands(hotel_commands_cost_driver)

    # print("---REVENUE DRIVER: %s---" %(hotel_id))

    # start_time_revenue = time.time()
    # revenue_driver_call_list = [
    #     'python', modules['revenue_driver_detection'],
    #     #'-N', '%s' % no_write,
    #     '-Y', '%s' % years_back,
    #     '-c', '%s' % client,
    #     '-i', '%s' % hotel_id]
    # subprocess.call(revenue_driver_call_list)
    # print("--- RUN REVENUE FOR HOTEL %s in %s seconds ---" % (hotel_id, time.time() - start_time_revenue))
    # log.info("--- RUN REVENUE FOR HOTEL %s in %s seconds ---" % (hotel_id, time.time() - start_time_revenue))

