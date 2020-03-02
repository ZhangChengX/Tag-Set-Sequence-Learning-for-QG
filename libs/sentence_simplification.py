# coding: utf-8

import subprocess
import config

class SentenceSimplification:

    input_file = config.root_path + 'tmp_input.txt'
    output_file = config.root_path + 'tmp_output.txt'

    def __init__(self):
        pass

    def simplify(self, text):
        rst = []
        # Write file
        with open(self.input_file, 'w') as file:
            if type(text) is list:
                text = '\n'.join(text)
            file.write(text)
        
        p = subprocess.Popen(['java', '-jar', config.root_path + 'libs/sentence-simplification-5.0.0-jar-with-dependencies.jar', self.input_file, self.output_file], 
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        # output = p.communicate()
        p.communicate()
        
        # Read file
        with open(self.output_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'core sentence: ' == line[:15]:
                    if ' .\n' in line:
                        line = line.replace(' .\n', '.')
                    rst.append(line[15:])
        return rst


if __name__ == "__main__":
    pass

