#
# Copyright 2014 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
## -*- coding: utf-8 -*-

import os
import cherrypy
import requests
import json
from mako.template import Template
from mako.lookup import TemplateLookup
import portfolio


class PersonalityInsightsService:
    """Wrapper on the Personality Insights service"""

    def __init__(self, vcapServices):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """

        # Feel free to clone this credentials, but it's expiring
        self.purl = "https://gateway.watsonplatform.net/personality-insights/api"
        self.pusername = "046142e1-22ee-43c1-8e38-a6d5489e00da"
        self.p_pwd = "fZJvhQLckeMC"

        # if vcapServices is not None:
        #     print("Parsing VCAP_SERVICES")
        #     services = json.loads(vcapServices)
        #     svcName = "personality_insights"
        #     if svcName in services:
        #         print("Personality Insights service found!")
        #         svc = services[svcName][0]["credentials"]
        #         self.purl = svc["url"]
        #         self.pusername = svc["username"]
        #         self.p_pwd = svc["password"]
        #     else:
        #         print("ERROR: The Personality Insights service was not found")

    def getProfile(self, text):
        """Returns the profile by doing a POST to /v2/profile with text"""

        if self.purl is None:
            raise Exception("No Personality Insights service is bound to this app")
        response = requests.post(self.purl + "/v2/profile",
                                 auth=(self.pusername, self.p_pwd),
                                 headers = {"content-type": "text/plain"},
                                 data=text
                                 )
        try:
            return json.loads(response.text)
        except:
            raise Exception("Error processing the request, HTTP: %d" % response.status_code)

class TradeOffAnalyticService:
    """Wrapper on the Personality Insights service"""

    def __init__(self):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """

        # Feel free to clone this credentials, but it's expiring
        self.t_url = "https://gateway.watsonplatform.net/tradeoff-analytics/api"
        self.t_username = "2943249c-ee9e-4172-bf7f-f2e09da8abf5"
        self.t_pwd = "zmu8rxzikUGX"

        # if vcapServices is not None:
        #     print("Parsing VCAP_SERVICES")
        #     services = json.loads(vcapServices)
        #     svcName = "personality_insights"
        #     if svcName in services:
        #         print("Personality Insights service found!")
        #         svc = services[svcName][0]["credentials"]
        #         self.url = svc["url"]
        #         self.username = svc["username"]
        #         self.password = svc["password"]
        #     else:
        #         print("ERROR: The Personality Insights service was not found")

    def getData(self, data):
        """Returns the profile by doing a POST to /v2/profile with text"""
        if self.t_url is None:
            raise Exception("No Trade Off Analytics service is bound to this app")
        response = requests.post(self.t_url + "/v1/dilemmas?generate_visualization=false",
                                 auth=(self.t_username, self.t_pwd),
                                 headers = {"content-type": "application/json"},
                                 data=data
                                 )
        try:
            return json.loads(response.text)
        except:
            raise Exception("Error processing the request, HTTP: %d" % response.status_code)

class TradeService(object):
    exposed = True

    def __init__(self, service):
        self.service = service
        self.defaultContent = None
        try:
            f = open('bond.json', 'r')

            #code = parse_json_watson(str_js)
            self.defaultContent = f.read()
        except Exception as e:
            print "ERROR: couldn't read mobidick.txt: %s" % e
        finally:
            f.close()

    def GET(self):
        """Shows the default page with sample text content"""

        return lookup.get_template("index.html").render(content='nothing')


    def POST(self):
        """
        Send 'text' to the Personality Insights API
        and return the response.
        """
        try:
            recommendJson = self.service.getData(self.defaultContent)
            res = {}
            code= portfolio.parse_json_watson(json.dumps(recommendJson))
            return code.to_json()
        except Exception as e:
            print "ERROR: %s" % e
            return str(e)

class PersonalService(object):
    """
    REST service/app. Since we just have 1 GET and 1 POST URLs,
    there is not even need to look at paths in the request.
    This class implements the handler API for cherrypy library.
    """
    exposed = True

    def __init__(self, service):
        self.service = service

    def GET(self):
        """Shows the default page with sample text content"""

        return lookup.get_template("personal.html").render(content='nothing')


    def POST(self):
        """
        Send 'text' to the Personality Insights API
        and return the response.
        """
        try:
            profileJson = self.service.getProfile(cherrypy.request.body.read())
            return json.dumps(profileJson)
        except Exception as e:
            print "ERROR: %s" % e
            return str(e)

class PortfolioService(object):
    exposed = True
    def GET(self,customer_id):
        ret, var, cash, stock,bond = portfolio.compute_portfolio_value(customer_id)
        data = {}
        data['ret']=str(ret)
        data['var']=str(var)
        data['cash']=str(cash)
        data['stock'] = str(stock)
        data['bond']=str(bond)
        return json.dumps(data)


if __name__ == '__main__':
    lookup = TemplateLookup(directories=["templates"])

    # Get host/port from the Bluemix environment, or default to local
    HOST_NAME = os.getenv("VCAP_APP_HOST", "127.0.0.1")
    PORT_NUMBER = int(os.getenv("VCAP_APP_PORT", "3000"))
    cherrypy.config.update({
        "server.socket_host": HOST_NAME,
        "server.socket_port": PORT_NUMBER,
    })

    # Configure 2 paths: "public" for all JS/CSS content, and everything
    # else in "/" handled by the DemoService
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.response_headers.on": True,
            "tools.staticdir.root": os.path.abspath(os.getcwd())
        },
        "/public": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "./public"
        }
    }

    # Create the Personality Insights Wrapper
    personalityInsights = PersonalityInsightsService(os.getenv("VCAP_SERVICES"))
    tradeoff = TradeOffAnalyticService()
    webapp = TradeService(tradeoff)
    webapp.personal = PersonalService(personalityInsights)
    webapp.portfolio = PortfolioService()
    # Start the server
    print("Listening on %s:%d" % (HOST_NAME, PORT_NUMBER))
    cherrypy.quickstart(webapp, "/", config=conf)
