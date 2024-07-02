import json
import os
import re
import sys
import traceback
from ansi2html import Ansi2HTMLConverter
from ansible_runner import run_command
from ansible_webx import config
from ansible_webx.app.socketio_instance import socketio

conv = Ansi2HTMLConverter()


def parse_output(data):

    output_lines = data.splitlines()
    recap = ''
    errors = []
    warnings = []
    patternfatal = r'(\x1b\[\d+;\d+m)fatal.*\x1b\[0m'
    patternerror = r'(\x1b\[\d+;\d+m)ERROR.*\x1b\[0m'
    ansi_seq_error = None
    patternwarning = r'(\x1b\[\d+;\d+m)\[WARNING\].*\x1b\[0m'
    ansi_seq_warning = None

    # Iterate over lines to find PLAY RECAP
    for idx, line in enumerate(output_lines):

        if 'PLAY RECAP' in line:
            # If found, get the next line which contains the recap data
            recap = output_lines[idx + 1]

        if (match_fatal := re.match(patternfatal,
                                    line)) or (match_fatal := re.match(
                                        patternerror, line)):
            print(repr(line))
            # Access the captured ANSI escape sequence or error message here
            ansi_seq_error = match_fatal.group(
                1)  # Capturing ANSI escape sequence
            errors.append(line)
        elif ansi_seq_error and re.match(
                re.escape(ansi_seq_error) + r'.*', line
        ):  # Check if the next line starts with the same ANSI escape sequence of the fatal error captured
            errors[len(errors) - 1] = errors[len(errors) - 1] + '\n' + line
        elif ansi_seq_error:
            ansi_seq_error = None

        if (match_warning := re.match(patternwarning, line)):
            print(repr(line))
            warnings.append(line)
            ansi_seq_warning = match_warning.group(
                1)  # Capturing ANSI escape sequence
        elif ansi_seq_warning and re.match(
                re.escape(ansi_seq_warning) + r'.*', line
        ):  # Check if the next line starts with the same ANSI escape sequence of the fatal error captured
            warnings[len(warnings) -
                     1] = warnings[len(warnings) - 1] + '\n' + line
        elif ansi_seq_warning:
            ansi_seq_warning = None

    warnings = [
        conv.convert(ansi=warn_line, full=False) for warn_line in warnings
    ]
    errors = [
        conv.convert(ansi=error_line, full=False) for error_line in errors
    ]

    recap = conv.convert(recap, full=False) if recap else None

    return recap, warnings, errors


def event_handler(event_data, sid):
    # Emitting to 'all' ensures that stdout is emitted, but could not give desirable experience when working with multiple sessions.
    # The 'client' approach has been tested and works with gevent and Flask's built-in web servers,
    # allowing for emitting to a specific client, which is the preferred method in such cases.
    if config['app'].get('emit', 'all') == 'all':
        sid = None
    # Process event data and emit stdout to the specific client or to all
    if sid is not None:
        socketio.emit('message',
                      conv.convert(ansi=event_data['stdout'], full=False),
                      room=sid)
    else:
        socketio.emit('message',
                      conv.convert(ansi=event_data['stdout'], full=False))


def run_ansible(playbook_directory=None,
                playbook=None,
                tags=None,
                extra_vars=None,
                limit=None,
                **kwargs):

    os.chdir(playbook_directory)

    inventory_file = f"{playbook_directory}/hosts"

    cmdline_args = [playbook, '-i', inventory_file]

    # Prepare tags
    if tags is not None:
        cmdline_args.extend(['--tags', ",".join(tags)])

    # Prepare extra vars
    if extra_vars is not None:
        extra_vars_str = json.dumps(extra_vars)
        cmdline_args.extend(['--extra-vars', extra_vars_str])

    # Prepare limit
    if limit is not None: cmdline_args.extend(['--limit', limit])

    sid = kwargs.get('sid', None)
    try:
        out, _, _ = run_command(
            executable_cmd='ansible-playbook',
            cmdline_args=cmdline_args,
            input_fd=sys.stdin,
            output_fd=sys.stdout,
            error_fd=sys.stderr,
            event_handler=lambda event_data: event_handler(event_data, sid),
            runner_mode='pexpect')

        recap, warning_output, error_output = parse_output(out)
        command_error = None
    except Exception as e:
        warning_output = None
        error_output = None
        recap = None
        command_error = str(e)
        print(e)
        print(traceback.print_exc())
    finally:
        return recap, warning_output, error_output, command_error


if __name__ == '__main__':

    playbook_directory = f"{config['app'].get('root_directory')}"
    playbook = 'playbook.yml'
    extra_vars = {"one_site": "server.com"}
    tags = ["prepare_website"]
    limit = "server"

    run_ansible(playbook_directory,
                playbook,
                tags=tags,
                extra_vars=extra_vars,
                limit=limit)
