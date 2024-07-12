import logging
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    function_name = req.route_params["functionName"]
    event_data = req.get_body()

    instance_id = await client.start_new(function_name, instance_id, event_data)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)
