import click
from azureml.core import Experiment
from azureml.core.authentication import AzureCliAuthentication
from azureml.train.estimator import Estimator
import requests


@click.command()
@click.option("--ct", "--compute-target", "compute_target", type=str, default='cpu-cluster')
@click.option("--wait-for-completion", is_flag=True)
def main(compute_target, wait_for_completion):
    # Use the authorization that Azure CLI Core is logged into
    cli_auth = AzureCliAuthentication()

    experiment = Experiment.from_directory("..", auth=cli_auth)
    ws = experiment.workspace

    cluster = ws.compute_targets[compute_target]

    # ngrok starts a local webserver that shows details about the tunnels that are created
    # this webserver listens at port 4040
    tunnels = requests.get('http://localhost:4040/api/tunnels').json()
    _, debug_url, debug_port = tunnels['tunnels'][0]['public_url'].replace("/", "").split(":")

    est = Estimator(source_directory=".",
                    entry_script='train.py',
                    compute_target=cluster,
                    conda_packages=['scikit-learn', 'pandas'],
                    pip_packages=['pydevd-pycharm~=192.5728.105'],
                    use_docker=True,
                    environment_variables={"PYCHARM_DEBUG": True,
                                           "PYCHARM_DEBUG_PORT": debug_port,
                                           "PYCHARM_DEBUG_HOST": debug_url}
                    )

    print("Submitting Debug Run")
    run = experiment.submit(est)
    print("Run Submitted")
    if wait_for_completion:
        run.wait_for_completion()
        print("Finishing Run")


if __name__ == "__main__":
    main()
