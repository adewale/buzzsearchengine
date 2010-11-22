# Copyright (C) 2010 Google Inc.
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

from google.appengine.api.urlfetch import DownloadError
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

import logging
import os
import simple_buzz_wrapper

class MainPageHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, {}, debug=True))


class Result(object):
	def __init__(self, permalink, title, actor, actor_profile, content):
		self.permalink = permalink
		self.title = title
		self.actor = actor
		self.actor_profile = actor_profile
		self.content = content

        # content is often a duplicate of title with no additional text
        self.is_useful_content = content.strip() != title.strip()


class SearchHandler(webapp.RequestHandler):
	def __search(self, query):
		buzz_wrapper=simple_buzz_wrapper.SimpleBuzzWrapper()
		try:
			json = buzz_wrapper.search(query)
			if json.has_key('items'):
				return json['items']
			return []
		except DownloadError:
			return []
		
	def get(self):
		query = self.request.get("q")
		items = self.__search(query)
		logging.info("There were %s results" % len(items))
		
		results = []
		for item in items:
			permalink = item['links']['alternate'][0]['href']
			title = item['title']
			actor = item['actor']['name']
			actor_profile = item['actor']['profileUrl']
			content = item['object']['content']
			result = Result(permalink, title, actor, actor_profile, content)
			results.append(result)
		
		no_results = len(results) == 0
		template_values = {'q':query, 'results':results, 'no_results':no_results}
		
		path = os.path.join(os.path.dirname(__file__), 'results.html')
		self.response.out.write(template.render(path, template_values, debug=True))

application = webapp.WSGIApplication([('/', MainPageHandler), ('/search', SearchHandler)], debug = True
)


def main():
 	util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
