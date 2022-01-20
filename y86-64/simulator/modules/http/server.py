# -*- encoding:UTF-8 -*-
import socket

class server():
    def __init__(self, serverport = 80, servername = "Python Socket Server", serverhost = "localhost"):
        self.serverport = serverport
        self.servername = servername
        self.serverhost = serverhost
        self.shutdownFlag = False
        self.jobs = { }
        self.application = None
        
        self.accesslog_flag = True
    
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
        response_dict["result"] = "%s 404 NOT FOUND" % (request_dict["RAW"]["request"])
        response_dict["body"] = "404 NOT FOUND"

        return response_dict
    
    # use in class
    def setApplication(self, application):
        self.application = application

    # console log
    def accesslog_print(self, addr_str, request_dict):
        if self.accesslog_flag:
            print("%s - %s" % (addr_str, "%s, %s, %s" % (request_dict["mathod"], request_dict["path"], request_dict[""])))

    # request message to dictionary
    def requestToDict(self, request_str):
        header_str, data_str = request_str.split("\r\n\r\n")
        header_list = header_str.split("\r\n")
        
        method, path, httpv = header_list[0].split(" ")
        
        # header
        header_dict = {}
        
        for record in header_list[1:]:
            key, data = record.split(": ")
            header_dict[key] = data
        
        # GET data
        get_data_dict = {}
        get_data_str = ""
        
        if path.find("?") + 1:
            path, get_data_str = path.split("?")
            
            for record in get_data_str.split("&"):
                if record.find("=") + 1:
                    key, data = record.split("=")
                    get_data_dict[key] = data
                else:
                    get_data_dict[record] = True
        
        # POST data
        post_data_dict = {}
        
        if method == "POST" and data_str:
            if header_dict["Content-Type"] == "application/x-www-form-urlencoded":
                for record in data_str.split("&"):
                    if record.find("="):
                        key, data = record.split("=")
                        post_data_dict[key] = data
                    else:
                        post_data_dict[record] = True
                        
            elif header_dict["Content-Type"] == "text/plan":
                post_data_dict["RAW"] = data_str
                
            # elif header_dict["Content-Type] == "multipart/form-data"
        
        return { "method": method, "path": path, "httpv": httpv, "RAW": { "GET": get_data_str, "POST": data_str, "request": header_list[0] },
                 "GET": get_data_dict, "POST": post_data_dict }
    
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
            response_dict = { "result": "%s 200 OK" % (request_dict["httpv"]), "Server": self.servername,
                              "Last-Modified": "Thu, 1 Jan 1970 00:00:00 GMT", "Content-Type": "text/html",
                              "Content-Length": "0", "Cache-Control": "no-store", "body": "" }

            # print log
            self.accesslog_print(addr[0], request_dict)

            # work and make message
            if request_dict["path"] in self.jobs.keys():
                if self.application:
                    response_dict = self.jobs[request_dict["path"]](self.application, request_dict, response_dict)
                else:
                    response_dict = self.jobs[request_dict["path"]](request_dict, response_dict)

            # not found
            else:
                response_dict["result"] = "%s 404 OK" % (request_dict["httpv"])
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

