from flask import Flask, request, jsonify
import json
import subprocess
import os
import re
import tempfile

app = Flask(__name__)

NSJAIL_PATH = "/usr/local/bin/nsjail"
SANDBOX_DIR =  "/mnt/sandbox"  # Runtime sandbox location

@app.route("/", methods=["GET"])
def root():
    return "StackSync Challenge is running!"

@app.route('/execute', methods=['POST'])
def execute_script():
    data = request.get_json()

    if not data or 'script' not in data:
        return jsonify({"error": "Missing 'script' field"}), 400

    script = data['script']
    if not isinstance(script, str) or not script.strip():
        return jsonify({"error": "Script must be a non-empty string"}), 400

    if not re.search(r'def\s+main\s*\(\s*\)\s*:', script):
        return jsonify({"error": "Script must contain a main() function"}), 400

    # Ensure sandbox/tmp exists
    os.makedirs(os.path.join(SANDBOX_DIR, "tmp"), exist_ok=True)

    # Create script file path (this gets bind-mounted into the jail as /tmp/script.py)
    script_path = os.path.join(SANDBOX_DIR, "tmp", "script.py")

    # Wrap the user script
    modified_script = f"""
import sys
import json
from io import StringIO

sys.path.append('/usr/local/lib/python3.10/dist-packages')

{script}

if __name__ == "__main__":
    original_stdout = sys.stdout
    sys.stdout = captured_stdout = StringIO()

    try:
        result = main()
        try:
            json_result = json.dumps(result)
        except TypeError as e:
            print(f"Error: Return value from main() is not JSON serializable: {{e}}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {{str(e)}}", file=sys.stderr)
        sys.exit(1)
    finally:
        captured_output = captured_stdout.getvalue()
        sys.stdout = original_stdout

    if captured_output:
        print(captured_output, end='')
    print(json_result)
"""

    # try:
    with open(script_path, "w") as f:
        f.write(modified_script)

    result = subprocess.run(
        [
            NSJAIL_PATH,
            "--mode", "o",
            "--chroot", "/mnt/sandbox",
            "--cwd", "/tmp",
            "--time_limit", "10",

            "--disable_clone_newuser",
            "--disable_clone_newnet",
            "--disable_clone_newpid",
            "--disable_clone_newipc",
            "--disable_clone_newuts",
            "--disable_clone_newcgroup",

            "--rlimit_as", "256",
            "--rlimit_fsize", "5",
            "--rlimit_nproc", "10",
	    
	    "--bindmount", "/usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:ro",
	    "--bindmount", "/usr/local/lib:/usr/local/lib:ro",
            "--bindmount", "/usr/bin/python3.10:/usr/bin/python3.10:ro",
            "--bindmount", "/lib/x86_64-linux-gnu/libm.so.6:/lib/x86_64-linux-gnu/libm.so.6:ro",
            "--bindmount", "/lib/x86_64-linux-gnu/libexpat.so.1:/lib/x86_64-linux-gnu/libexpat.so.1:ro",
            "--bindmount", "/lib/x86_64-linux-gnu/libz.so.1:/lib/x86_64-linux-gnu/libz.so.1:ro",
            "--bindmount", "/lib/x86_64-linux-gnu/libc.so.6:/lib/x86_64-linux-gnu/libc.so.6:ro",
            "--bindmount", "/lib64/ld-linux-x86-64.so.2:/lib64/ld-linux-x86-64.so.2:ro",

            "--bindmount", "/usr/lib/python3.10:/usr/lib/python3.10:ro",
            "--bindmount", "/usr/local/lib/python3.10/dist-packages:/usr/local/lib/python3.10/dist-packages:ro",

            "--bindmount", "/mnt/sandbox/tmp:/tmp:rw",
            "--bindmount", "/dev/null:/dev/null:ro",
            "--bindmount", "/dev/urandom:/dev/urandom:ro",
            "--bindmount", "/proc:/proc:ro",

            "--", "/usr/bin/python3.10", "script.py"
        ],
        capture_output=True,
        text=True,
        timeout=11
    )


    # except subprocess.TimeoutExpired:
    #     return jsonify({"error": "Script execution timed out"}), 408
    # except Exception as e:
    #     return jsonify({"error": f"Execution error: {str(e)}"}), 500
    # finally:
    #     if script_path:
    #         try:
    #             os.remove(script_path)
    #         except:
    #             pass

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        return jsonify({
            "error": "Script execution failed",
            "stderr": stderr,
            "stdout": stdout
        }), 400

    try:
        lines = stdout.splitlines()
        if not lines:
            return jsonify({"error": "No output from script"}), 400

        json_result = json.loads(lines[-1])
        stdout_content = '\n'.join(lines[:-1]) if len(lines) > 1 else ""

        return jsonify({
            "result": json_result,
            "stdout": stdout_content
        })
    except json.JSONDecodeError:
        return jsonify({
            "error": "Script did not return valid JSON from main()",
            "stdout": stdout
        }), 422

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
