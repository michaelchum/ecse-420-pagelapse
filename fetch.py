from git import Repo
from selenium import webdriver
import sys
from subprocess import PIPE, Popen
from threading  import Thread
from Queue import Queue, Empty
import errno
import shutil
from multiprocessing import Process
import os
import time
import subprocess
import signal

ON_POSIX = 'posix' in sys.builtin_module_names

repo_dir = 'repos/'
tmp_dir = repo_dir + 'tmp/'
host_dir = repo_dir + 'tmp_host/'
screen_dir = 'screenshots/'
commit_per_thread = 20

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def chunks(l, n):
    # Yield successive n-sized chunks from l.
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def copy(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            print('Directory not copied. Error: %s' % e)

def fetch(repo_url):
    # create repo dir
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)
    # setup paths
    repo_name = repo_url.split('/')[-1]
    print repo_name
    repo_path = tmp_dir + repo_name
    host_path = host_dir + repo_name
    screen_path = screen_dir + repo_name

    # clone repo
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    repo = Repo.clone_from(repo_url, repo_path)

    repo = Repo(repo_path)
    git = repo.git

    # create screenshot dir
    if not os.path.exists(screen_dir):
        os.mkdir(screen_dir)
    if not os.path.exists(screen_dir+repo_name):
        os.mkdir(screen_dir+repo_name)

    # fetch all commits
    commit_list = []
    for commit in repo.iter_commits('master', max_count=2000):
        commit_list.append(commit)
    commit_list.reverse()

    # print len(commit_list)

    # filter changed files
    critical_changes = ('config.yml', '.html', '.js', '.scss', '.css', '.php', '.svg', '.png', '.gif', '.jpg', '.jpeg', '.jade')
    filtered_commit_list = []
    for i in range(1, len(commit_list)-1):
        changed_files = []
        changes = git.diff(commit_list[i-1], commit_list[i], '--name-only').split('\n')
        for change in changes:
            if change.endswith(critical_changes):
                filtered_commit_list.append(commit_list[i])
                break

    chunked_commit_list = list(chunks(commit_list, commit_per_thread))
    numThreads = len(chunked_commit_list)

    # list servers
    phantom_process_list = []

    # spawn server threads
    for x in range(numThreads):
        port = 4000 + x
        sub_chunk = chunked_commit_list[x]
        start_index = x * commit_per_thread
        sub_repo_path = repo_path + str(x)
        sub_host_path = host_path + str(x)
        copy(repo_path, sub_repo_path)
        host_address, pid = spawn_server_thread(port, sub_repo_path, sub_host_path, repo_name)
        phantom_process_list.append(spawn_phantom_process(host_address, sub_repo_path, sub_chunk, start_index, repo_name, pid, repo_url))

    for t in phantom_process_list:
        t.join()

    to_print = "gif"
    to_print += " " + repo_name + ".mp4"
    print to_print

def spawn_server_thread(port, repo_path, host_path, repo_name):

    # spawn child thread and serve 
    p = Popen(['jekyll', 'serve', '--watch', '-s', repo_path, '-d', host_path, '--port', str(port)] , stdout=PIPE, stderr=PIPE, bufsize=1, close_fds=ON_POSIX)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True # thread dies with the program
    t.start()

    host_address = 'http://localhost:' + str(port) + "/index.html"

    # wait until server starts
    while True:
        # read line without blocking
        try:  line = q.get_nowait() # or q.get(timeout=.1)
        except Empty:
            continue
        else: # got line
            print line
            if "Server running" in line:
                print "Server running " + repo_name + " " + str(p.pid) + " on " + host_address
                return host_address, p.pid

def spawn_phantom_process(host_address, repo_path, commit_list, index, repo_name, pid, repo_url):
    # spawn child thread and serve 
    t = Process(target=phantom, args=(host_address, repo_path, commit_list, index, repo_name, pid, repo_url))
    t.daemon = True # thread dies with the program
    t.start()

    return t

def phantom(host_address, repo_path, commit_list, index, repo_name, pid, repo_url):

    repo = Repo(repo_path)
    git = repo.git

    #init phantom drivers
    driver = webdriver.PhantomJS() # or add to your PATH
    driver.set_window_size(1440, 4000) # optional

    while commit_list != []:
        to_print = "commit "
        to_print += str(commit_list[0])
        to_print += " " + repo_name + '/' + str(index).zfill(3) + '.jpg'
        to_print += " " + repo_url
        to_print += " " + commit_list[0].message
        print to_print
        git.checkout(commit_list.pop(0))
        os.system("phantomjs phantom_screen.js " + host_address + " " + screen_dir + '/' + repo_name + '/' + str(index).zfill(3) + '.jpg')
        index += 1

    driver.quit()

    os.kill(pid, signal.SIGQUIT)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        fetch('https://github.com/markprokoudine/mchacks')
    else:
        fetch(sys.argv[1])



