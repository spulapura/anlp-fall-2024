import random

def build_training_set():
    all_lines = []    
    with open("assignment1-data/training.nl") as f:
        for line in f:
            all_lines.append(line)


    random.shuffle(all_lines)
    training_set = all_lines[0:800]
    dev_set = all_lines[800:900]
    test_set = all_lines[900:]

    with open("assignment1-data/training_set.nl", "w+") as trainfile:
        trainfile.writelines(training_set)
        trainfile.close()      
    with open("assignment1-data/dev_set.nl", "w+") as devfile:
        devfile.writelines(dev_set)
        devfile.close()      
    with open("assignment1-data/test_set.nl", "w+") as testfile:
        testfile.writelines(test_set)
        testfile.close()      


build_training_set()