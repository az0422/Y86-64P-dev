# -*- encoding:UTF-8 -*-
import socket
import zlib
import base64

class server():
    def __init__(self, serverport = 80, servername = "Python Socket Server", serverhost = "localhost"):
        self.serverport = serverport
        self.servername = servername
        self.serverhost = serverhost
        self.shutdownFlag = False
        self.jobs = { }
        self.application = None
    
    def setServerSettings(self, serverport = 80, servername = "Python Socket Server", serverhost = "localhost"):
        self.serverport = serverport
        self.servername = servername
        self.serverhost = serverhost

    # add job
    def addJob(self, request):
        def work(func):
            self.jobs[request] = func
        return work
    
    def shutdown(self):
        self.shutdownFlag = True

    # 404 Not Found
    def NotFound(self, request_dict, response_dict):
        response_dict["result"] = "%s 404 NOT FOUND" % (request_dict["header"]["request"][2])
        response_dict["body"] = "404 NOT FOUND"

        return response_dict
    
    # use in class
    def setApplication(self, application):
        self.application = application

    # console log
    def accesslog_print(self, addr_str, request_dict):
        print("%s - %s" % (addr_str, request_dict["header"]["request"]))

    # request message to dictionary
    def requestToDict(self, request_str):
        request_split = request_str.split("\r\n")
        request_dict = { "header": {}, "body": {} }
        blink_flag = False

        request_dict["header"] = { "request": request_split[0].split(" ") }
        
        # GET method
        if request_dict["header"]["request"][0] == "GET": 
            query = request_dict["header"]["request"][1].split("?")
            request_dict["header"]["request"][1] = query[0]
            
            if len(query) == 2:
                for record in query[1].split("&"):
                    (key, value) = record.split("=")
                    
                    request_dict["body"][key] = value
        
        # message to dictionary
        for str in request_split[1:]:
            str = str.strip()

            if str == "":
                blink_flag = True
                continue

            # body
            if blink_flag:
                body_list = str.split("&")
                
                for record in body_list:
                    (key, value) = record.split("=")
                    request_dict["body"][key.strip()] = value.strip()
                
            # header
            else:
                header_split = str.split(":")
                request_dict["header"][header_split[0].strip()] = header_split[1].strip()
        
        return request_dict
    
    # response dictionary to response message
    def responseDictToMessage(self, response_dict):

        # result and body
        result = "%s\r\n" % (response_dict["result"])
        body = "%s\r\n" % (response_dict["body"])

        del response_dict["body"]
        del response_dict["result"]

        # other headers
        for key in response_dict.keys():
            result += "%s: %s\r\n" % (key, response_dict[key])
        
        # merge
        result += "\r\n%s" % (body)

        return result.encode(encoding = "UTF-8")

    # run
    def run(self):
        print("run at http://%s:%d" % (self.serverhost if self.serverhost != "" else "localhost", self.serverport))

        # start socket server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.serverhost, self.serverport))
        server.listen(0)

        while True:
            # accept connect
            client, addr = server.accept()
            request_str = client.recv(65536).decode()

            # NULL message
            if request_str == "":
                client.close()
                continue
            
            # convert message to dictionary
            request_dict = self.requestToDict(request_str)

            # make default response dictionary
            response_dict = { "result": "%s 200 OK" % (request_dict["header"]["request"][2]), "Server": self.servername,
                              "Last-Modified": "Thu, 1 Jan 1970 00:00:00 GMT", "Content-Type": "text/html",
                              "Content-Length": "0", "Cache-Control": "no-store", "body": ""}

            # print log
            self.accesslog_print(addr[0], request_dict)

            # work and make message
            if request_dict["header"]["request"][1] in self.jobs.keys():
                if self.application:
                    response_dict = self.jobs[request_dict["header"]["request"][1]](self.application, request_dict, response_dict)
                else:
                    response_dict = self.jobs[request_dict["header"]["request"][1]](request_dict, response_dict)

            # not found
            else:
                response_dict["result"] = "%s 404 OK" % (request_dict["header"]["request"][2])
                response_dict["body"] = "404 NOT FOUND"
            
            # count length
            response_dict["Content-Length"] = str(len(response_dict["body"]))

            # make message
            message_byte = self.responseDictToMessage(response_dict)

            # send
            client.send(message_byte)
            client.close()

            if self.shutdownFlag:
                server.close()
                break

