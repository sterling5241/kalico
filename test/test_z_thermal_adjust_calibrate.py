"""Z_THERMAL_ADJUST_CALIBRATE reports the coefficient before writing data."""

import builtins
from types import SimpleNamespace

import pytest

from klippy.extras import z_thermal_adjust


@pytest.fixture
def calibration(monkeypatch, tmp_path):
    monkeypatch.setattr(
        z_thermal_adjust.tempfile, "gettempdir", lambda: str(tmp_path)
    )
    messages = []
    nozzle = z_thermal_adjust.NozzleCalibration.__new__(
        z_thermal_adjust.NozzleCalibration
    )
    nozzle.gcmd = SimpleNamespace(respond_info=messages.append)
    temps = [150.0, 175.0, 200.0, 225.0, 250.0]
    nozzle.temperatures = temps + temps[::-1]
    nozzle.z_values = [
        0.1 + 0.0005 * (temp - 150.0) for temp in nozzle.temperatures
    ]
    return nozzle, messages, tmp_path


def test_coefficient_reported_before_data_written(calibration):
    nozzle, messages, tmp_path = calibration

    temp_coeff = nozzle._calculate_and_report_coeff()

    assert temp_coeff == pytest.approx(-0.0005)
    assert messages[0] == "Nozzle expands 0.0500mm over 100.0C"
    assert messages[1] == "Temperature Coefficient: -0.0005"
    assert messages[2].startswith("Nozzle elongation data written to ")
    (csv_file,) = tmp_path.glob("nozzle_elongation_*.csv")
    lines = csv_file.read_text().splitlines()
    assert lines[0] == "temperature,z"
    assert len(lines) == 11
    assert lines[1] == "150.0,0.100000"
    assert lines[5] == "250.0,0.150000"


def test_calibration_does_not_import_matplotlib(monkeypatch, calibration):
    nozzle, _, _ = calibration
    real_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] == "matplotlib":
            raise AssertionError("matplotlib imported in the reactor thread")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    nozzle._calculate_and_report_coeff()
