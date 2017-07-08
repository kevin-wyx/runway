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


def run_command(cmd, cwd=None):
    print("$ {}".format(cmd))
    env_vars, stripped_cmd = extract_env_vars(cmd)
    try:
        p = subprocess.Popen(shlex.split(stripped_cmd),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             cwd=cwd,
                             env=env_vars,
                             bufsize=1)
        for line in iter(p.stdout.readline, ""):
            print(line.decode('utf-8').rstrip())
        exit_code = p.wait()
        if exit_code != 0:
            raise Exception("Command '{}' responded with a non-zero exit "
                            "status ({}).\nAn error for this command might "
                            "have been printed above these lines. Please read "
                            "the output in order to check what went "
                            "wrong.".format(cmd, exit_code))
    except CalledProcessError as e:
        raise Exception("Error running '{}':\n{}\n{}".format(cmd, e.output,
                                                             e.message))
    except Exception as e:
        raise Exception("Error running '{}':\n{}".format(cmd, e.message))
