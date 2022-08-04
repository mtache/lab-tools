import os, shutil, pathlib, nornir

from nornir.core.task import Task, Result
from rich.progress import Progress
from ceos_lab import templates
from importlib.resources import path
from nornir_napalm.plugins.tasks import napalm_configure
from ceos_lab.config import apply_templates

STOP_TERMINATTR = """
daemon TerminAttr
   shutdown
!
"""
START_TERMINATTR = """
daemon TerminAttr
   no shutdown
!
"""

def onboard(nornir: nornir.core.Nornir, topology: dict, token: pathlib.Path) -> Result:
    with Progress() as bar:
        task_id = bar.add_task("Onboard to CloudVision", total=len(nornir.inventory.hosts))
        def onboard_device(task: Task):
            device_path = os.path.join(f"clab-{topology['name']}", str(task.host), 'flash', 'cv-onboarding-token')
            bar.console.log(f"Copying {token} to {device_path}")
            shutil.copyfile(token, device_path)
            with path(templates, 'onboard') as p:
                task.run(task=apply_templates, folder=p, bar=bar)
            task.run(task=napalm_configure, dry_run=False, configuration=STOP_TERMINATTR)
            task.run(task=napalm_configure, dry_run=False, configuration=START_TERMINATTR)
            bar.console.log(f"{task.host}: TerminAttr restarted.")
            bar.update(task_id, advance=1)
        return nornir.run(task=onboard_device)
