# A probe that is only used for bed mesh, so it does not take the
# "probe" name from the main probe
from . import probe


def load_config(config):
    return probe.PrinterProbe(
        config,
        probe.ProbeEndstopWrapper(config),
        pin_chip_name="mesh_probe",
        command_prefix="MESH_",
    )
