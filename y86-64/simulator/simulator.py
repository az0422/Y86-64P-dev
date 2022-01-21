# -*- encoding:UTF-8 -*-

# 시뮬레이터 실행기
#
# 시뮬레이터는 기본적으로 HTTP 프로토콜을 이용한 1:1 클라이언트 - 서버 모델을 사용한다

import sys

from modules import launcher, config, simulator

class main(launcher.launcher):
    def args_set(self):
        return False
    
    def job(self, args_dict):
        configdata = config.config("config/settings.conf").read()
        serverport = 5500
        serverhost = ""

        # fetch from configuration
        serverport = int(configdata["Server"]["port"]) if "port" in configdata["Server"].keys() else 5500
        serverhost = configdata["Server"]["host"] if "host" in configdata["Server"].keys() else ""

        # make server and run
        sim = simulator.simulatorServer(serverport = serverport, serverhost = serverhost)
        sim.run()
        
        sys.exit()

    def help_print(self):
        print("No help available")
        
main().run()