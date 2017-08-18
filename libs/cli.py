import datetime
import re
import shlex
import subprocess
from subprocess import CalledProcessError


def extract_env_vars(cmd):
    env_vars = {}
    matches = re.split('(\S+=\S+) ', cmd)
    remaining_matches = list(matches)
    for match in matches:
        stripped_match = match.strip()
        if stripped_match != '':
            if match.find(' ') > -1 or match.find('=') < 0:
                break
            else:
                split_match = stripped_match.split('=')
                env_vars[split_match[0]] = split_match[1]
        remaining_matches.pop(0)
    remainder = ''.join(remaining_matches)
    return env_vars if len(env_vars) > 0 else None, remainder


def print_and_log(text, logfile_path):
    print(text)
    log(text, logfile_path)


def log(text, logfile_path):
    if logfile_path is not None:
        with open(logfile_path, "a") as logfile:
            logfile.write("[{}] {}\n".format(
                datetime.datetime.now().strftime("%F %H:%M:%S"), text))


def run_command(cmd, cwd=None, logfile_path=None, shell=False):
    if cwd is not None:
        print_and_log("$ cd {}".format(cwd), logfile_path)
    env_vars, stripped_cmd = None, cmd  #extract_env_vars(cmd)
    if shell:
        parsed_cmd = stripped_cmd
    else:
        parsed_cmd = shlex.split(stripped_cmd)
    print_and_log("$ {}".format(parsed_cmd), logfile_path)
    try:
        p = subprocess.Popen(parsed_cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             cwd=cwd,
                             env=env_vars,
                             bufsize=1,
                             shell=shell)
        while p.poll() is None:
            l = p.stdout.readline()  # This blocks until it receives a newline.
            print_and_log(l.decode('utf-8').rstrip(), logfile_path)
        remaining_output = p.stdout.read().decode('utf-8').strip()
        if remaining_output != "":
            print_and_log(p.stdout.read(), logfile_path)
        exit_code = p.wait()
        if exit_code != 0:
            raise LoggedException(
                "Command '{}' responded with a non-zero exit status ({}).\n"
                "An error for this command might have been printed above "
                "these lines. Please read the output in order to check what "
                "went wrong.".format(parsed_cmd, exit_code), logfile_path)
    except CalledProcessError as e:
        raise LoggedException(
            "Error running '{}':\n{}\n{}".format(parsed_cmd, e.output, str(e)),
            logfile_path)
    except LoggedException:
        raise
    except Exception as e:
        raise LoggedException("Error running '{}':\n{}".format(cmd, str(e)),
                              logfile_path)


class LoggedException(Exception):
    def __init__(self, message, logfile_path, *args, **kwargs):
        super(LoggedException, self).__init__(message, *args, **kwargs)
        log(str(self), logfile_path)
