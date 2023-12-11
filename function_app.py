import os
import logging
import azure.functions as func

# Semantic Kernel のインポート
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.core_skills import TimeSkill

AZURE_OPENAI_ENDPOINT = os.environ["OPENAI_API_BASE"]
AZURE_OPENAI_KEY = os.environ["OPENAI_API_KEY"]
AZURE_OPENAI_DEPLOYMENT_NAME = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
async def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        result = await callsk(name)
        return func.HttpResponse(f"Result : {result}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

async def callsk(input):
    kernel = sk.Kernel(log=sk.NullLogger())
    kernel.add_chat_service(
        "chat_completion",
        AzureChatCompletion(
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
        ),
    )
    plugins_directory = "./plugins"

    # Import the WriterPlugin from the plugins directory.
    writer_plugin = kernel.import_semantic_skill_from_directory(
        plugins_directory, "WriterPlugin"
    )

    result = await kernel.run_async(
        writer_plugin["ShortPoem"],input_str=input
    )

    return result