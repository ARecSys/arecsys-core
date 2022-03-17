
# Use the AppSearch client directly:
from elastic_enterprise_search import AppSearch

url = "https://test-99cff2.ent.eastus2.azure.elastic-cloud.com"
engine_name = "articles-metadata"

search_key = # SEARCH_KEY #
private_key = # PRIVATE_KEY #

app_search = AppSearch( url, http_auth = private_key )
enginesearch = app_search.get_engine( engine_name )

def insert ( enginesearch , doc ):
    
    return app_search.index_documents( engine_name = enginesearch["name"], documents = doc )

def search ( enginesearch, body ):

    return app_search.search( engine_name = enginesearch["name"], body = body )

# body = {
#     "query": "Val"
# }

# resp = search ( enginesearch , body)

# print(resp)