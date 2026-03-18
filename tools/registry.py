from typing import Callable, Dict
from tools.docker_run import docker_run
from tools.docker_ps import docker_ps
from tools.docker_logs import docker_logs
from tools.docker_stop import docker_stop
from tools.docker_stop_all import docker_stop_all
from tools.docker_build import docker_build
from tools.docker_images import docker_images
from tools.docker_rm import docker_rm
from tools.docker_rmi import docker_rmi
from tools.docker_exec import docker_exec
from tools.docker_inspect import docker_inspect
from tools.docker_ports import docker_ports
from tools.docker_restart import docker_restart
from tools.docker_prune import docker_prune
from tools.docker_pull import docker_pull
from tools.docker_stats import docker_stats
from tools.docker_network import docker_network
from tools.docker_volume import docker_volume

TOOLS: Dict[str, Callable] = {
    "docker_run": docker_run,
    "docker_ps": docker_ps,
    "docker_logs": docker_logs,
    "docker_stop": docker_stop,
    "docker_stop_all": docker_stop_all,
    "docker_build": docker_build,
    "docker_images": docker_images,
    "docker_rm": docker_rm,
    "docker_rmi": docker_rmi,
    "docker_exec": docker_exec,
    "docker_inspect": docker_inspect,
    "docker_ports": docker_ports,
    "docker_restart": docker_restart,
    "docker_prune": docker_prune,
    "docker_pull": docker_pull,
    "docker_stats": docker_stats,
    "docker_network": docker_network,
    "docker_volume": docker_volume,
}
