import os
import pys

for root, dirs, files in os.walk("./tests/"):
    path = root.split(os.sep)
    for file in sorted(files):
        test_file = os.path.basename(root)+'/'+file
        test_path = (os.getcwd()+'/tests/'+test_file)
        print(test_file)
        # print('Tokens in '+test_file)
        # pys.get_tokens_file(test_path)
        pys.get_parse_output_file(test_path)
        print()
        # break
