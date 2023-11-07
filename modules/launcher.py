# -*- encoding:UTF-8 -*-
import sys

# launcher class
# 
# 실행 프로그램을 구성하기 위한 부모 클래스이다
#
# 이 클래스를 상속하여 사용할 수 있다

class launcher():
    def __init__(self):
        self.requireArgs = True
    
    def args_set(self):
        return True

    # load args to dictionary
    def loadArgs(self):
        result = { "help": False }
        args = sys.argv

        # nothing argument 
        if len(args) == 1:
            if self.requireArgs:
                return { "help": True }
            else:
                return { "help": False }
        
        # exist arguments
        i = 0
        while i < len(args):
            if i == 0:
                i += 1
                continue

            if args[i] == "-h" or args[i] == "--help":
                result["help"] = True
                break

            if args[i].startswith("-") or args[i].startswith("--"):
                result[args[i]] = args[i + 1]
                i += 1
            
            else:
                result["file"] = args[i]
            
            i += 1
        
        return result

    # work
    def job(self, args_dict):
        pass

    # help message
    def help_print(args):
        pass

    # run
    def run(self):
        self.requireArgs = self.args_set()

        try:
            args_dict = self.loadArgs()
        except IndexError:
            self.help_print()
            sys.exit()

        if args_dict["help"]:
            self.help_print()
        
        else:
            self.job(args_dict)