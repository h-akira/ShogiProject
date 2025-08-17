import sys
import os
from hads.handler import Master
from moto import mock_aws

def lambda_handler(event, context):
  sys.path.append(os.path.dirname(__file__))
  master = Master(event, context)
  master.logger.info(f"path: {master.request.path}")
  try:
    if master.settings.USE_MOCK:
      return use_mock(master)
    else:
      return main(master)
  except Exception as e:
    if master.request.path == "/favicon.ico":
      master.logger.warning("favicon.ico not found")
    else:
      master.logger.exception(e)
    from hads.shortcuts import error_render
    import traceback
    return error_render(master, traceback.format_exc())

def main(master):
  from hads.authenticate import set_auth_by_cookie, add_set_cookie_to_header
  set_auth_by_cookie(master)
  view, kwargs = master.router.path2view(master.request.path)
  response = view(master, **kwargs)
  
  # # Cookie処理前のデバッグログ
  # master.logger.info(f"Before cookie processing - set_cookie: {getattr(master.request, 'set_cookie', None)}")
  # master.logger.info(f"Before cookie processing - clean_cookie: {getattr(master.request, 'clean_cookie', None)}")

  add_set_cookie_to_header(master, response)

  # # Cookie処理後のデバッグログ
  # master.logger.info(f"Response structure: {response}")
  # if "multiValueHeaders" in response and "Set-Cookie" in response["multiValueHeaders"]:
  #   master.logger.info(f"Cookie headers: {response['multiValueHeaders']['Set-Cookie']}")
  # else:
  #   master.logger.info("No cookie headers set")
  
  return response

@mock_aws
def use_mock(master):
  from mock.dynamodb import set_data as set_dynamodb_data
  from mock.ssm import set_data as set_ssm_data
  from hads.authenticate import set_auth_by_cookie, add_set_cookie_to_header
  set_dynamodb_data()
  set_ssm_data()
  set_auth_by_cookie(master)
  view, kwargs = master.router.path2view(master.request.path)
  response = view(master, **kwargs)
  
  # Cookie処理前のデバッグログ
  master.logger.info(f"Before cookie processing - set_cookie: {getattr(master.request, 'set_cookie', None)}")
  master.logger.info(f"Before cookie processing - clean_cookie: {getattr(master.request, 'clean_cookie', None)}")
  
  add_set_cookie_to_header(master, response)
  
  # Cookie処理後のデバッグログ
  master.logger.info(f"Response structure: {response}")
  if "multiValueHeaders" in response and "Set-Cookie" in response["multiValueHeaders"]:
    master.logger.info(f"Cookie headers: {response['multiValueHeaders']['Set-Cookie']}")
  else:
    master.logger.info("No cookie headers set")
  
  return response

if __name__ == "__main__":
  from hads.debug import main_debug_handler
  main_debug_handler(lambda_handler)
